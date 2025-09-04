from __future__ import annotations
from typing import Dict, List
import json

import duckdb

from airflow.providers.common.sql.hooks.sql import DbApiHook
from airflow.exceptions import AirflowException

class DuckDBHook(DbApiHook):
    """Interact with DuckDB, with support for installing/loading extensions via connection extras."""

    conn_name_attr = "duckdb_conn_id"
    default_conn_name = "duckdb_default"
    conn_type = "duckdb"
    hook_name = "DuckDB"
    placeholder = "?"

    def get_conn(self) -> duckdb.DuckDBPyConnection:
        """Returns a duckdb connection object, with optional extensions installed/loaded."""
        conn_id = getattr(self, self.conn_name_attr)
        airflow_conn = self.get_connection(conn_id)

        # Connect to DuckDB (in-memory or file-based)
        if not airflow_conn.host:
            conn = duckdb.connect(":memory:")
        else:
            conn = duckdb.connect(airflow_conn.host)

        # Handle extensions from extra field (JSON)
        extra = airflow_conn.extra_dejson()  # Parses extra as dict
        install_extensions: List[str] = extra.get("install_extensions", [])
        load_extensions: List[str] = extra.get("load_extensions", [])

        try:
            for ext in install_extensions:
                conn.install_extension(ext)
            for ext in load_extensions:
                conn.load_extension(ext)
        except Exception as e:
            raise AirflowException(f"Failed to install/load DuckDB extension: {str(e)}")

        return conn

    def get_uri(self) -> str:
        """Override DbApiHook get_uri method for get_sqlalchemy_engine()"""
        conn_id = getattr(self, self.conn_name_attr)
        airflow_conn = self.get_connection(conn_id)
        if not airflow_conn.host:
            return "duckdb:///:memory:"
        return f"duckdb:///{airflow_conn.host}"

    @staticmethod
    def get_ui_field_behaviour() -> Dict:
        """Returns custom field behaviour"""
        return {
            "hidden_fields": ["login", "password", "schema", "port"],  # Extra is not hidden, so users can edit it
            "relabeling": {
                "host": "File (leave blank for in-memory database)",
            },
        }
