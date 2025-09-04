def get_provider_info():
    return {
        "package-name": "airflow-provider-duckdb",
        "name": "DuckDB Airflow Provider",
        "description": "DuckDB (duckdb.org) provider for Apache Airflow",
        "hook-class-names": ["duckdb_provider.hooks.duckdb_hook.DuckDBHook"],
        "versions": ["0.0.1"],
        "connection-types": [
            {
                "hook-class-name": "duckdb_provider.hooks.duckdb_hook.DuckDBHook",
                "connection-type": "duckdb",
            }
        ],
    }
