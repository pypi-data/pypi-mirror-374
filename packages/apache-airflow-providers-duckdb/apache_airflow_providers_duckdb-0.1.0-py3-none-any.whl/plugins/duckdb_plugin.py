from typing import Any, Dict, List
import duckdb
from airflow.plugins_manager import AirflowPlugin
from airflow.hooks.base import BaseHook
from airflow.models.connection import Connection
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator  # For optional operator

# Custom Hook for DuckDB
class DuckDBHook(BaseHook):
    """
    Hook for DuckDB connections.
    Uses 'extra' JSON for config (e.g., {"path": "/path/to/db.db", "threads": 4, "extensions": ["httpfs", "parquet"]}).
    If 'extensions' is provided as a list in extras, it will automatically run INSTALL and LOAD for each extension
    after establishing the connection, before any queries are executed.
    """
    conn_name_attr = 'duckdb_conn_id'
    default_conn_name = 'duckdb_default'
    conn_type = 'duckdb'  # This defines the conn type
    hook_name = 'DuckDB'

    @staticmethod
    def get_connection_form_widgets() -> Dict[str, Any]:
        """Custom form fields for the UI."""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from wtforms import StringField
        return {
            "extra__duckdb__path": StringField("Path (e.g., :memory: or /path/to/db.db)", widget=BS3TextFieldWidget()),
            "extra__duckdb__extensions": StringField("Extensions (comma-separated, e.g., httpfs,parquet)", widget=BS3TextFieldWidget()),
        }

    @staticmethod
    def get_ui_field_behaviour() -> Dict[str, Any]:
        """Defines UI behavior: Hide unnecessary fields like host/port/login."""
        return {
            "hidden_fields": ["host", "port", "schema", "login", "password"],
            "relabeling": {},
            "placeholders": {
                "extra": '{"path": ":memory:", "threads": 4, "extensions": ["httpfs", "parquet"]}',
            },
        }

    def __init__(self, duckdb_conn_id: str = default_conn_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duckdb_conn_id = duckdb_conn_id

    def get_conn(self):
        conn: Connection = self.get_connection(self.duckdb_conn_id)
        extra = conn.extra_dejson()
        path = extra.get('path', ':memory:')  # Default to in-memory
        config = {k: v for k, v in extra.items() if k not in ('path', 'extensions')}  # Other config (exclude extensions)
        
        # Establish connection
        db_conn = duckdb.connect(database=path, config=config)
        
        # Handle extensions: Install and load each one if specified
        extensions = extra.get('extensions', [])
        if isinstance(extensions, str):
            extensions = [ext.strip() for ext in extensions.split(',') if ext.strip()]  # Parse comma-separated string from UI field
        elif not isinstance(extensions, list):
            extensions = []  # Ensure it's a list
        
        for ext in extensions:
            db_conn.execute(f"INSTALL '{ext}';")
            db_conn.execute(f"LOAD '{ext}';")
        
        return db_conn

    def run(self, sql, autocommit=True, parameters=None, handler=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, parameters)
        if autocommit:
            conn.commit()
        if handler:
            results = handler(cursor)
        else:
            results = cursor.fetchall()
        cursor.close()
        conn.close()  # Close after run for safety
        return results

# Optional: Custom Operator (inherits from SQLExecuteQueryOperator)
class DuckDBOperator(SQLExecuteQueryOperator):
    template_fields = ('sql',)
    template_ext = ('.sql',)
    ui_color = '#a22041'  # Custom color for UI

    def __init__(self, *args, duckdb_conn_id='duckdb_default', **kwargs):
        super().__init__(conn_id=duckdb_conn_id, *args, **kwargs)

# Register the plugin
class DuckDBPlugin(AirflowPlugin):
    name = "duckdb_plugin"
    hooks = [DuckDBHook]
    operators = [DuckDBOperator]  # Optional

