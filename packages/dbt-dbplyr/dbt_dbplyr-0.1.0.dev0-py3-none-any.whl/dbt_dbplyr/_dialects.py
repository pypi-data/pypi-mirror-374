from typing import NewType

from rpy2.robjects.packages import importr

import ibis.backends.sql.datatypes as sql_dt
import ibis.expr.datatypes as dt
import ibis.expr.types as ir
from dbt.contracts.graph.manifest import Manifest
from ibis.formats import TypeMapper

# Use NewType to make sure that we don't accidentally mix these up, i.e.
# pass a DBTAdapterType to a function that expects an IbisDialect or vice versa.
IbisDialect = NewType("IbisDialect", str)
DBTAdapterType = NewType("DBTAdapterType", str)

DBTAdapterTypeToIbisDialect: dict[DBTAdapterType, IbisDialect] = {
    DBTAdapterType("postgres"): IbisDialect("postgres"),
    DBTAdapterType("redshift"): IbisDialect("postgres"),
    DBTAdapterType("snowflake"): IbisDialect("snowflake"),
    DBTAdapterType("trino"): IbisDialect("trino"),
    DBTAdapterType("mysql"): IbisDialect("mysql"),
    DBTAdapterType("sqlite"): IbisDialect("sqlite"),
    DBTAdapterType("oracle"): IbisDialect("oracle"),
    DBTAdapterType("duckdb"): IbisDialect("duckdb"),
    DBTAdapterType("bigquery"): IbisDialect("bigquery"),
    DBTAdapterType("databricks"): IbisDialect("databricks"),
}

IbisDialectToTypeMapper: dict[IbisDialect, type[TypeMapper]] = {
    IbisDialect("postgres"): sql_dt.PostgresType,
    IbisDialect("snowflake"): sql_dt.SnowflakeType,
    IbisDialect("trino"): sql_dt.TrinoType,
    IbisDialect("mysql"): sql_dt.MySQLType,
    IbisDialect("sqlite"): sql_dt.SQLiteType,
    IbisDialect("oracle"): sql_dt.OracleType,
    IbisDialect("duckdb"): sql_dt.DuckDBType,
    IbisDialect("bigquery"): sql_dt.BigQueryType,
    IbisDialect("databricks"): sql_dt.DatabricksType,
}


IBIS_TO_R_TYPE = {
    dt.String: "character",
    dt.Int8: "integer",
    dt.Int16: "integer",
    dt.Int32: "integer",
    dt.Int64: "bigint",
    dt.Float32: "double",
    dt.Float64: "double",
    dt.Boolean: "logical",
    dt.Timestamp: "POSIXct",
    dt.Date: "Date",
    dt.Time: "POSIXct",   # optional: require hms pkg
    dt.Binary: "character",
    dt.Decimal: "numeric",
    # you can extend with arrays/maps/json → "list"
}


def get_ibis_dialect(manifest: Manifest) -> IbisDialect:
    dbt_adapter_type = manifest.metadata.adapter_type
    if dbt_adapter_type is None:
        raise ValueError("Could not determine dbt adapter type")
    elif dbt_adapter_type not in DBTAdapterTypeToIbisDialect:
        raise ValueError(
            f"DBT adapter type {dbt_adapter_type} is not supported by dbt-ibis."
        )
    return DBTAdapterTypeToIbisDialect[DBTAdapterType(dbt_adapter_type)]


def parse_db_dtype_to_ibis_dtype(
    db_dtype: str, ibis_dialect: IbisDialect
) -> dt.DataType:
    type_mapper = IbisDialectToTypeMapper[ibis_dialect]
    return type_mapper.from_string(db_dtype)

def ibis_dtype_to_r(dtype: dt.DataType) -> str:
    for ibis_type, r_type in IBIS_TO_R_TYPE.items():
        if isinstance(dtype, ibis_type):
            return r_type
    return "character"

def r_expr_to_sql(r_expr) -> str:
    """
    Convert an R dbplyr tbl_lazy object to a SQL string for dbt.
    """
    # sql_render returns an R character vector (length 1)
    dbplyr = importr("dbplyr")
    sql_str = dbplyr.sql_render(r_expr)[0]  # extract the first element as string
    return str(sql_str)

