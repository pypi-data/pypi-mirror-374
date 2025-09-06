from abc import ABC, abstractproperty
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Final, Union
from rpy2.robjects import ListVector, StrVector
import rpy2.robjects as robjects

from dbt_dbplyr._dialects import IbisDialect

_REF_IDENTIFIER_PREFIX: Final = "__dbplyr_ref__"
_REF_IDENTIFIER_SUFFIX: Final = "__rid__"
_SOURCE_IDENTIFIER_PREFIX: Final = "__dbplyr_source__"
_SOURCE_IDENTIFIER_SUFFIX: Final = "__sid__"
_SOURCE_IDENTIFIER_SEPARATOR: Final = "__ibd_sep__"

class _Reference(ABC):
    @abstractproperty

    def _r_table_name(self) -> str:
        """Generate the table name in dbt-dbplyr format."""
        pass

    def get_schema(self) -> dict[str, str]:
            return self._schema

    def get_table_name(self) -> str:
        return self._r_table_name

    
    def to_dbplyr(self, schema: dict[str, str], ibis_dialect: IbisDialect):
        if schema is None:
            raise NotImplementedError("Schema must be provided")

        self._schema = schema

        # No conversion – assume schema already uses R-compatible type strings
        schema_r = robjects.ListVector({
            col: robjects.StrVector(["character" if type_str == "NULL" else type_str])
            for col, type_str in schema.items()
        })

        # Call the R schema function with explicit dialect
        r_schema_func = robjects.globalenv["schema_to_tbl_lazy"]
        lazy_tbl = r_schema_func(schema_r, self._r_table_name, ibis_dialect)
        return lazy_tbl

@dataclass
class ref(_Reference):
    """A reference to a dbt model."""

    name: str

    @property
    def _r_table_name(self) -> str:
        return _REF_IDENTIFIER_PREFIX + self.name + _REF_IDENTIFIER_SUFFIX


@dataclass
class source(_Reference):
    """A reference to a dbt source."""

    source_name: str
    table_name: str

    @property
    def _r_table_name(self) -> str:
        return (
            _SOURCE_IDENTIFIER_PREFIX
            + self.source_name
            + _SOURCE_IDENTIFIER_SEPARATOR
            + self.table_name
            + _SOURCE_IDENTIFIER_SUFFIX
        )


