import graphlib
import re
import rpy2.robjects as robjects
from rpy2.robjects import RObject
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final, Literal, Optional, Union

from dbt.config import RuntimeConfig
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.nodes import (
    ColumnInfo,
    ModelNode,
    SeedNode,
    SnapshotNode,
    SourceDefinition,
)

from dbt_dbplyr._dialects import IbisDialect,parse_db_dtype_to_ibis_dtype, ibis_dtype_to_r
from dbt_dbplyr._dialects import r_expr_to_sql
from dbt_dbplyr._references import (
    _REF_IDENTIFIER_PREFIX,
    _REF_IDENTIFIER_SUFFIX,
    _SOURCE_IDENTIFIER_PREFIX,
    _SOURCE_IDENTIFIER_SEPARATOR,
    _SOURCE_IDENTIFIER_SUFFIX,
    _Reference,
    ref,
    source,
)

R_FILE_EXTENSION: Final = "R"
R_SQL_FOLDER_NAME: Final = "__R_sql"

SQL_TO_R_TYPES = {
    "integer": "integer",
    "bigint": "bigint",
    "double": "numeric",
    "float": "numeric",
    "real": "numeric",
    "numeric": "numeric",
    "decimal": "numeric",
    "varchar": "character",
    "text": "character",
    "string": "character",
    "boolean": "logical",
    "bit": "logical",
    "date": "Date",
    "timestamp": "POSIXct",
    "datetime": "POSIXct",
}


_RefLookup = dict[str, Union[ModelNode, SeedNode, SnapshotNode]]
_SourcesLookup = dict[str, dict[str, SourceDefinition]]
_LetterCase = Literal["lower", "upper"]

@dataclass
class RExprInfo:
    def __init__(self, r_path: Path, depends_on: tuple[str], func: robjects.functions.SignatureTranslatedFunction):
        self.r_path = Path(r_path)
        self.func = func
        self.depends_on = depends_on
        self._tbl_lazy = None
        self._schema = None

    def __call__(self, *args, **kwargs):
        """Allows the object itself to be called, while caching tbl_lazy."""
        self._tbl_lazy = self.func(*args, **kwargs)
        return self._tbl_lazy

    @property
    def name(self) -> str:
        return self.r_path.stem

    @property
    def sql_path(self) -> Path:
        return self.r_path.parent / R_SQL_FOLDER_NAME / f"{self.name}.sql"
    
    @property
    def schema(self):
        if self._schema is None:
            if self._tbl_lazy is None:
                raise ValueError("tbl_lazy not built yet. Call the model func first.")
            r_schema = robjects.r["tbl_lazy_to_schema"](self._tbl_lazy)
            self._schema = {str(name): str(r_schema.rx2(name)[0]) for name in r_schema.names}
        return self._schema


def compile_r_expressions_to_sql(
    all_r_expr_infos: list[RExprInfo],
    manifest: Manifest,
    runtime_config: RuntimeConfig,
    ibis_dialect: IbisDialect,
) -> None:
    # Order Ibis expressions by their dependencies so that the once which
    # depend on other Ibis expressions are compiled after the ones they depend on.
    # For example, if model_a depends on model_b, then model_b will be compiled
    # first and will appear in the list before model_a.
    all_r_expr_infos = _sort_r_exprs_by_dependencies(all_r_expr_infos)

    ref_infos, source_infos = _extract_ref_and_source_infos(manifest)

    letter_case_in_db, letter_case_in_expr = _get_letter_case_conversion_rules(
        runtime_config
    )

    # Schemas of the R expressions themselves in case they are referenced
    # by other downstream R expressions
    r_expr_schemas = {}
    # Convert R expressions to SQL and write to file
    for r_expr_info in all_r_expr_infos:
        references: list[str] = []
        for r in r_expr_info.depends_on:
            if isinstance(r, source):
                schema = _get_schema_for_source(
                    r,
                    source_infos,
                    ibis_dialect=ibis_dialect
                )
            elif isinstance(r, ref):
                schema = _get_schema_for_ref(
                    r,
                    ref_infos,
                    r_model_schemas=r_expr_schemas,
                    ibis_dialect=ibis_dialect
                )
            else:
                raise ValueError(f"Unknown reference type: {type(r)}")
            dbt_table = r.to_dbplyr(schema,ibis_dialect=ibis_dialect)
            dbt_table = _set_letter_case_on_r_expression(
                dbt_table, letter_case_in_expr
            )

            references.append(dbt_table)
        r_expr = r_expr_info(*references)
        r_expr = _set_letter_case_on_r_expression(r_expr, letter_case_in_db)

        r_expr_schemas[r_expr_info.name] = r_expr_info.schema

        # Convert to SQL and write to file
        dbt_sql = _to_dbt_sql(r_expr)
        r_expr_info.sql_path.parent.mkdir(parents=False, exist_ok=True)
        r_expr_info.sql_path.write_text(dbt_sql)


def _set_letter_case_on_r_expression(r_expr, letter_case: Optional[_LetterCase]):
    """Apply letter casing to an R dbplyr expression (tbl_lazy)."""

    if letter_case:
        rename_df = robjects.globalenv["rename_df"]
        r_expr = rename_df(r_expr, letter_case)

    return r_expr


def _sort_r_exprs_by_dependencies(
    r_exprs: list[RExprInfo],
) -> list[RExprInfo]:
    r_expr_lookup = {m.name: m for m in r_exprs}

    # Only look at ref. source references are not relevant for this sorting
    # as they already exist -> Don't need to compile them. Also no need to consider
    # refs which are not R expressions
    graph = {
        r_expr_name: [
            d.name
            for d in r_expr.depends_on
            if isinstance(d, ref) and d.name in r_expr_lookup
        ]
        for r_expr_name, r_expr in r_expr_lookup.items()
    }
    sorter = graphlib.TopologicalSorter(graph)
    r_expr_order = list(sorter.static_order())

    return [r_expr_lookup[m] for m in r_expr_order]


def _extract_ref_and_source_infos(
    dbt_manifest: Manifest,
) -> tuple[_RefLookup, _SourcesLookup]:
    nodes = list(dbt_manifest.nodes.values())
    models_and_seeds = [
        n for n in nodes if isinstance(n, (ModelNode, SeedNode, SnapshotNode))
    ]
    ref_lookup = {m.name: m for m in models_and_seeds}

    sources = dbt_manifest.sources.values()
    sources_lookup: defaultdict[str, dict[str, SourceDefinition]] = defaultdict(dict)
    for s in sources:
        sources_lookup[s.source_name][s.name] = s
    return ref_lookup, dict(sources_lookup)


def _get_letter_case_conversion_rules(
    runtime_config: RuntimeConfig,
) -> tuple[Optional[_LetterCase], Optional[_LetterCase]]:
    # Variables as defined in e.g. dbt_project.yml
    dbt_project_vars = runtime_config.vars.vars
    project_name = runtime_config.project_name
    target_name = runtime_config.target_name

    in_db_var_name = f"dbt_r_letter_case_in_db_{project_name}_{target_name}"
    in_expr_var_name = "dbt_r_letter_case_in_expr"

    in_db_raw = dbt_project_vars.get(in_db_var_name, None)
    in_expr_raw = dbt_project_vars.get(in_expr_var_name, None)
    in_db = _validate_letter_case_var(in_db_var_name, in_db_raw)
    in_expr = _validate_letter_case_var(in_expr_var_name, in_expr_raw)
    return in_db, in_expr


def _get_schema_for_source(source, source_infos: dict[str, dict], ibis_dialect: IbisDialect) -> dict[str, str]:
    if source.source_name not in source_infos:
        raise ValueError(f"Source '{source.source_name}' not found in source metadata.")

    if source.table_name not in source_infos[source.source_name]:
        raise ValueError(f"Table '{source.table_name}' not found in source metadata for source '{source.source_name}'.")

    source_def = source_infos[source.source_name][source.table_name]
    columns = getattr(source_def, "columns", {})
    if not columns:
        raise ValueError(f"Source '{source.source_name}.{source.table_name}' has no columns defined.")

    return _columns_to_r_schema(columns = columns, ibis_dialect=ibis_dialect)



def _get_schema_for_ref(
        ref,
        ref_infos: dict[str, object],
        r_model_schemas: dict[str, dict[str, str]],
        ibis_dialect: IbisDialect
    ) -> dict[str, str]:
    """
    Get the schema for a referenced R model (or seed).
    - ref_infos: metadata from ModelNode or SeedNode objects
    - r_model_schemas: optional precomputed schema dictionary for R models
    Returns a dict mapping column names -> R types.
    """
    # 1. Try to get schema from the model/seed metadata
    schema = None
    columns_with_missing_types = []

    if ref.name in ref_infos:
        info = ref_infos[ref.name]

        if isinstance(info, SeedNode):
            # Seed: column types in config
            columns = {
                name: ColumnInfo(name=name, data_type=dt)
                for name, dt in info.config.column_types.items()
            }
        else:
            # Regular R model: take from columns attribute
            columns = info.columns

        if columns:
            # Check for missing types
            missing_types = [c.name for c in columns.values() if c.data_type is None]
            if missing_types:
                columns_with_missing_types = missing_types
            else:
                schema = _columns_to_r_schema(columns, ibis_dialect=ibis_dialect)

    # 2. Fallback: check if a precomputed R model schema was provided
    if schema is None and ref.name in r_model_schemas:
        schema = r_model_schemas[ref.name]

    # 3. Raise error if still not found
    if schema is None:
        if columns_with_missing_types:
            raise ValueError(
                f"The following columns of '{ref.name}' do not have a data type configured: "
                + ", ".join(f"'{c}'" for c in columns_with_missing_types)
            )
        else:
            raise ValueError(
                f"Could not determine schema for model '{ref.name}'. Define it in YAML or ensure the R model is structured correctly."
            )

    return schema


def _columns_to_r_schema(
    columns: dict[str, ColumnInfo],
    ibis_dialect: IbisDialect,
) -> dict[str, str]:
    schema_dict: dict[str, str] = {}
    for c in columns.values():
        if c.data_type is None:
            raise ValueError(f"Could not determine data type for column '{c.name}'")
        ibis_dtype = parse_db_dtype_to_ibis_dtype(
            c.data_type, ibis_dialect=ibis_dialect
        )
        schema_dict[c.name] = ibis_dtype_to_r(ibis_dtype)
    return schema_dict


def _to_dbt_sql(r_expr: RObject) -> str:
    sql = r_expr_to_sql(r_expr)
    sql = sql.replace("`", '"') #dbplyr uses backticks not quote marks
    capture_pattern = "(.+?)"

    # Remove quotation marks around the source name and table name as
    # quoting identifiers should be handled by DBT in case it is needed.
    quotation_marks_pattern = r'"?'

    # Insert ref jinja function
    sql = re.sub(
        quotation_marks_pattern
        + _REF_IDENTIFIER_PREFIX
        + capture_pattern
        + _REF_IDENTIFIER_SUFFIX
        + quotation_marks_pattern,
        r"{{ ref('\1') }}",
        sql,
    )

    # Insert source jinja function
    sql = re.sub(
        quotation_marks_pattern
        + _SOURCE_IDENTIFIER_PREFIX
        + capture_pattern
        + _SOURCE_IDENTIFIER_SEPARATOR
        + capture_pattern
        + _SOURCE_IDENTIFIER_SUFFIX
        + quotation_marks_pattern,
        r"{{ source('\1', '\2') }}",
        sql,
    )

    # Replace "SELECT {{ ref(...) }}.*" or "SELECT {{ source(...) }}.*" with "SELECT *"
    sql = re.sub(
        r"SELECT\s+\{\{\s*(ref|source)\([^)]+\)\s*\}\}\.\*",
        "SELECT *",
        sql,
    )
    
    return sql


def _validate_letter_case_var(variable_name: str, value: Any) -> Optional[_LetterCase]:
    if value is not None and value not in ["lower", "upper"]:
        raise ValueError(
            f"The {variable_name} variable needs to be set to"
            + f" either 'lower' or 'upper' but currently has a value of '{value}'."
            + " If you want the default behaviour of Ibis, you can omit this variable."
        )
    return value
