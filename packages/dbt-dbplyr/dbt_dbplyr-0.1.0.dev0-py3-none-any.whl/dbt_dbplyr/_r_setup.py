# dbt_dbplyr/r_setup.py
from rpy2 import robjects
from rpy2.robjects import packages as rpackages
import logging

logger = logging.getLogger(__name__)

REQUIRED_PACKAGES = ["tibble", "dplyr", "dbplyr", "bit64","duckdb"]

def install_missing_packages():
    utils = rpackages.importr("utils")
    installed = utils.installed_packages()
    installed_names = [pkg for pkg in installed.rownames]

    missing = [pkg for pkg in REQUIRED_PACKAGES if pkg not in installed_names]
    if missing:
        logger.info(f"Installing missing R packages: {missing}")
        utils.install_packages(robjects.StrVector(missing))


def register_r_helpers():
    robjects.r("""
    library(tibble)
    library(dbplyr)
    library(dplyr)

    # Map dbt adapter type to dbplyr simulate_* backend
    get_dbplyr_con <- function(dialect) {
      con <- switch(
        dialect,
        "postgres"   = simulate_postgres(),
        "snowflake"  = simulate_snowflake(),
        "trino"      = simulate_trino(),
        "mysql"      = simulate_mysql(),
        "sqlite"     = simulate_sqlite(),
        "oracle"     = simulate_oracle(),
        "duckdb"     = duckdb::simulate_duckdb(),
        "bigquery"   = simulate_bigquery(),
        "databricks" = simulate_spark_sql(),       # databricks → spark
        stop(paste("Unsupported dbplyr dialect:", dialect))
      )
      return(con)
    }

    # Build a tbl_lazy using schema + dialect
    schema_to_tbl_lazy <- function(schema_list, name, dialect = "postgres") {
      # Create tibble with proper types
      tib <- tibble::tibble()
      for (col in names(schema_list)) {
        type <- schema_list[[col]]
        val <- switch(
          type,
          "character" = NA_character_,
          "double"    = NA_real_,
          "numeric"   = NA_real_,
          "integer"   = NA_integer_,
          "logical"   = NA,
          "Date"      = as.Date(NA),
          "POSIXct"   = as.POSIXct(NA),
          "bigint"    = bit64::integer64(NA),
          stop(paste("Unsupported type", type))
        )
        tib[[col]] <- val
      }

      # Pick the simulated backend connection
      con <- get_dbplyr_con(dialect)

      # Return lazy table
      tbl_lazy <- dbplyr::tbl_lazy(tib, name = name, con = con)
      return(tbl_lazy)
    }

               
    tbl_lazy_to_schema <- function(tbl) {
      # get remote columns
      col_names <- tbl_vars(tbl)
      types <- sapply(col_names, function(col) {
        class(tbl[[col]])[1]  # first class string
      })
      names(types) <- col_names
      as.list(types)
    }
               
    rename_df <- function(df, method = NULL) {

      rename_fun <- function(cn) {
        x <- trimws(cn)
        x <- gsub("-", "_", x, fixed = TRUE)
        x <- gsub(" ", "_", x, fixed = TRUE)
        x <- gsub("([A-z0-9])([A-Z])", "\\1_\\2", x, perl = FALSE)
        if (method == "lower") tolower(x) else toupper(x)
      }

      if ("tbl_lazy" %in% class(df)) {
        df <- dplyr::rename_with(df, rename_fun, dplyr::everything())
      } else {
        new_names <- rename_fun(names(df))
        if (any(duplicated(new_names))) stop("Renaming produced duplicate column names!")
        names(df) <- new_names
      }

      df
    }

    """)

_r_environment_ready = False

def setup_r_environment():
    global _r_environment_ready
    if _r_environment_ready:
        return
    try:
        install_missing_packages()
        register_r_helpers()
        logger.info("R environment ready")
        _r_environment_ready = True
    except Exception as e:
        logger.warning(f"R environment setup failed: {e}")
