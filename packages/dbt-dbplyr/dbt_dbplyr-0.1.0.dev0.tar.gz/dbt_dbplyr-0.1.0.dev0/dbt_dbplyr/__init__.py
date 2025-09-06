__all__ = ["compile_ibis_to_sql", "depends_on", "ref", "source"]
__version__ = "0.1.0dev"

import logging
import subprocess
import sys
import re
import rpy2.robjects as robjects
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from typing import Callable, Optional, Union
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage

from dbt.cli.main import cli

from dbt_dbplyr import _dialects
from dbt_dbplyr._compile import R_FILE_EXTENSION as _R_FILE_EXTENSION
from dbt_dbplyr._compile import R_SQL_FOLDER_NAME as _R_SQL_FOLDER_NAME
from dbt_dbplyr._compile import RExprInfo as _RExprInfo
from dbt_dbplyr._compile import (
    compile_r_expressions_to_sql as _compile_r_expressions_to_sql,
)
from dbt_dbplyr._logging import configure_logging as _configure_logging
from dbt_dbplyr._parse_dbt_project import (
    disable_node_not_found_error as _disable_node_not_found_error,
)
from dbt_dbplyr._parse_dbt_project import (
    invoke_parse_customized as _invoke_parse_customized,
)
from dbt_dbplyr._references import _Reference, source, ref

from dbt_dbplyr._r_setup import setup_r_environment

setup_r_environment()

logger = logging.getLogger(__name__)
_configure_logging(logger)

def compile_r_to_sql(dbt_parse_arguments: Optional[list[str]] = None) -> None:
    """Compiles all Ibis code to SQL and writes them to the .sql files
    in the dbt project. There is no need to call this function directly as
    you'd usually use the dbt-ibis command line interface instead. This function
    is equivalent to `dbt-ibis precompile`. However, it is
    provided for convenience in case you want to call it from Python.
    """
    logger.info("Parse dbt project")
    with _disable_node_not_found_error():
        manifest, runtime_config = _invoke_parse_customized(dbt_parse_arguments)

    ibis_dialect = _dialects.get_ibis_dialect(manifest)

    project_root = runtime_config.project_root
    # We can treat models and singular tests as equivalent for the purpose
    # of compiling Ibis expressions to SQL.
    paths = runtime_config.model_paths + runtime_config.test_paths

    all_r_expr_infos = _get_r_expr_infos(
        project_root=project_root,
        paths=paths,
    )
    if len(all_r_expr_infos) == 0:
        logger.info("No R expressions found.")
        return
    else:
        logger.info(f"Compiling {len(all_r_expr_infos)} R expressions to SQL")

        _compile_r_expressions_to_sql(
            all_r_expr_infos=all_r_expr_infos,
            manifest=manifest,
            ibis_dialect = ibis_dialect,
            runtime_config=runtime_config,
        )

        _clean_up_unused_sql_files(
            [r_expr_info.sql_path for r_expr_info in all_r_expr_infos],
            project_root=project_root,
            paths=paths,
        )
        logger.info("Finished compiling Ibis expressions to SQL")


def _parse_cli_arguments() -> tuple[str, list[str]]:
    # First argument of sys.argv is path to this file. We then look for
    # the name of the actual dbt subcommand that the user wants to run and ignore
    # any global flags that come before it.
    # We return the subcommand as well as separately in a list, all subsequent
    # arguments which can then be passed to
    # _parse_customized so that a user can e.g. set --project-dir etc.
    # For example, "dbt-dbplyr --warn-error run --select stg_orders --project-dir folder"
    # becomes "--select stg_orders --project-dir folder"
    # in variable args. parse_customized will then ignore "--select stg_orders"
    all_args = sys.argv[1:]
    subcommand_idx = next(
        i
        for i, arg in enumerate(all_args)
        if arg in [*list(cli.commands.keys()), "precompile"]
    )
    args = all_args[subcommand_idx + 1 :]
    subcommand = all_args[subcommand_idx]
    return subcommand, args


def _get_r_expr_infos(
    project_root: Union[str, Path], paths: list[str]
) -> list[_RExprInfo]:
    r_files = _glob_in_paths(
        project_root=project_root,
        paths=paths,
        pattern=f"**/*.{_R_FILE_EXTENSION}",
    )
    r_expr_infos: list[_RExprInfo] = []
    for file in r_files:
        func = _get_expr_func(file)
        depends_on = _extract_r_model_dependencies(file)
        r_expr_infos.append(
            _RExprInfo(r_path=file, depends_on=depends_on, func=func)
        )
    return r_expr_infos


def _extract_r_model_dependencies(file: Path) -> tuple[_Reference, ...]:
    """
    Extract refs and sources from an R model function by inspecting default arguments.
    Returns a tuple of _Reference instances, e.g. (ref("stg_orders"), source("raw", "customers"))
    """
    r_pkg = robjects.packages.SignatureTranslatedAnonymousPackage(
        file.read_text(), "model_module"
    )

    if not hasattr(r_pkg, "model"):
        raise ValueError(f"No `model` function found in {file}")

    r_func = r_pkg.model
    formals = robjects.r["formals"](r_func)

    references: list[_Reference] = []

    for i in range(len(formals)):
        default_val = formals[i]
        default_str = str(default_val)

        # Extract refs
        for name in re.findall(r'ref\(["\']([\w_]+)["\']\)', default_str):
            references.append(ref(name=name))

        # Extract sources
        for src, table in re.findall(r'source\(["\']([\w_]+)["\']\s*,\s*["\']([\w_]+)["\']\)', default_str):
            references.append(source(source_name=src, table_name=table))

    # Type validation like dbt-dbplyr
    if not all(isinstance(r, _Reference) for r in references):
        raise ValueError(
            "All arguments to depends_on need to be either an instance of "
            "dbt_dbplyr.ref or dbt_dbplyr.source"
        )

    return tuple(references)

def _glob_in_paths(
    project_root: Union[str, Path], paths: list[str], pattern: str
) -> list[Path]:
    if isinstance(project_root, str):
        project_root = Path(project_root)

    matches: list[Path] = []
    for m_path in paths:
        matches.extend(list((project_root / m_path).glob(pattern)))
    return matches


def _get_expr_func(file: Path) -> robjects.functions.SignatureTranslatedFunction:
    """
    Load an R model file and return the `model` function as a callable.
    Mimics the style of dbt_ibis `_get_expr_func`.
    """
    if not file.exists():
        raise ValueError(f"File does not exist: {file}")

    # Read the R code
    try:
        r_code = file.read_text()
    except Exception as e:
        raise ValueError(f"Could not read file {file}: {e}") from e

    # Wrap R code into a temporary anonymous package
    try:
        r_pkg = SignatureTranslatedAnonymousPackage(r_code, "model_module")
    except Exception as e:
        raise ValueError(f"Could not load R code from {file}: {e}") from e

    # Expect the model function to be defined
    if not hasattr(r_pkg, "model"):
        raise ValueError(f"No `model` function found in {file}")

    model_func = getattr(r_pkg, "model")

    if not callable(model_func):
        raise ValueError(f"`model` in {file} is not callable")

    return model_func

def _clean_up_unused_sql_files(
    used_sql_files: list[Path],
    project_root: Union[str, Path],
    paths: list[str],
) -> None:
    """Deletes all .sql files in any of the _IBIS_SQL_FOLDER_NAME folders which
    are not referenced by any Ibis expression. This takes care of the case where
    a user deletes an Ibis expression but the .sql file remains.
    """
    all_sql_files = _glob_in_paths(
        project_root=project_root,
        paths=paths,
        pattern=f"**/{_R_SQL_FOLDER_NAME}/*.sql",
    )
    # Resolve to absolute paths so we can compare them
    all_sql_files = [f.resolve() for f in all_sql_files]
    used_sql_files = [f.resolve() for f in used_sql_files]
    unused_sql_files = [f for f in all_sql_files if f not in used_sql_files]
    if unused_sql_files:
        for f in unused_sql_files:
            f.unlink()
        logger.info(
            f"Cleaned up {len(unused_sql_files)} unused .sql files"
            + f" in your {_R_SQL_FOLDER_NAME} folders"
        )


def main() -> None:
    dbt_subcommand, dbt_parse_arguments = _parse_cli_arguments()
    if dbt_subcommand != "deps":
        # If it's deps, we cannot yet parse the dbt project as it will raise
        # an error due to missing dependencies. We also don't need to so that's fine
        compile_r_to_sql(dbt_parse_arguments)
    if dbt_subcommand != "precompile":
        # Execute the actual dbt command
        process = subprocess.run(  # noqa: S603
            ["dbt"] + sys.argv[1:],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        sys.exit(process.returncode)


if __name__ == "__main__":
    main()
