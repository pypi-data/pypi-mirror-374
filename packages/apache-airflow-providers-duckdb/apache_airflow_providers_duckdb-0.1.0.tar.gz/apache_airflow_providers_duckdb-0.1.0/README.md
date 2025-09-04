# Airflow DuckDB Provider (Unofficial)

[![PyPI version](https://badge.fury.io/py/apache-airflow-providers-duckdb.svg)](https://badge.fury.io/py/apache-airflow-providers-duckdb)
[![License](https://img.shields.io/badge/License-APACHE-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

This is an **unofficial** provider package for integrating [DuckDB](https://duckdb.org/) (an embeddable analytical database) with [Apache Airflow](https://airflow.apache.org/). It registers a custom 'duckdb' connection type in Airflow's UI, along with a `DuckDBHook` and `DuckDBOperator` for seamless use in your DAGs.

**Disclaimer**: This is not an official Apache Airflow provider and is not affiliated with the Apache Software Foundation. It's a community-driven extension. If you're interested in making this official, consider contributing to the Airflow project.

## Features
- Registers 'duckdb' as a connection type in Airflow's Admin > Connections UI.
- Custom hook (`DuckDBHook`) for connecting to DuckDB (in-memory or file-based).
- Custom operator (`DuckDBOperator`) for executing SQL queries.
- Supports DuckDB configuration via connection extras (e.g., path, threads).
- Compatible with Airflow 2.0+.

## Requirements
- Apache Airflow >= 2.0.0
- DuckDB >= 0.8.0
- Python >= 3.8

## Installation
Install via PyPI:

```bash
pip install apache-airflow-providers-duckdb
```

After installation, restart your Airflow services (webserver, scheduler, workers) to load the plugin. For distributed setups (e.g., Celery or Kubernetes), ensure the package is installed on all nodes.

If you encounter naming conflicts or prefer a different package name, you can install from source (see Contributing below).

Usage
Setting Up a Connection
Go to Airflow UI > Admin > Connections > Create.
Select Conn Type: 'duckdb'.
Fill in:
Conn Id: e.g., duckdb_default.
Extra: JSON config, e.g., {"path": "/path/to/my_duckdb_file.db", "threads": 4} (or use the custom "Path" field in the form).
Save. DuckDB supports in-memory mode with {"path": ":memory:"}.
Alternatively, via CLI:

```bash
airflow connections add 'duckdb_default' \
  --conn-type 'duckdb' \
  --conn-extra '{"path": "/path/to/my_duckdb_file.db", "threads": 4}'
```

Example DAG
Import the hook and operator in your DAG file:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from apache_airflow_providers_duckdb.plugins.duckdb_plugin import DuckDBHook, DuckDBOperator  # Adjust import if package name changes

def run_with_hook(**kwargs):
    hook = DuckDBHook(duckdb_conn_id='duckdb_default')
    result = hook.run("SELECT 42 AS answer")
    print(result)  # Output: [(42,)]

with DAG(dag_id='duckdb_example', start_date=datetime(2023, 1, 1), catchup=False) as dag:
    # Using DuckDBOperator
    op_task = DuckDBOperator(
        task_id='run_query_op',
        duckdb_conn_id='duckdb_default',
        sql='SELECT * FROM my_table;',
    )
    
    # Using DuckDBHook in PythonOperator
    hook_task = PythonOperator(
        task_id='run_query_hook',
        python_callable=run_with_hook,
    )
    
    op_task >> hook_task
```

Configuration
In-Memory Mode: Set "path": ":memory:" in extras for temporary, fast analytics.
File-Based: Specify a file path like "path": "/path/to/db.db".
Advanced Config: Pass other DuckDB options (e.g., "threads": 4, "memory_limit": "2GB") in extras.
For more on DuckDB, see the official docs.

Troubleshooting
Conn Type Not Appearing: Ensure the package is installed and Airflow is restarted. Run airflow plugins to verify 'duckdb_plugin' is loaded.
Import Errors: Check your Python path and ensure the package is in your environment.
Distributed Airflow: Install the package on all workers.
Errors in Hook: Verify DuckDB is installed (pip show duckdb) and check Airflow logs.
If issues persist, open an issue on this repo.

Contributing
Contributions are welcome! Fork the repo, make changes, and submit a pull request.

Clone: git clone https://github.com/yourusername/airflow-duckdb-provider.git (replace with your repo URL).
Install dev deps: pip install -e .[dev] (add [project.optional-dependencies] in pyproject.toml if needed).
Build: python -m build.
Test locally: Install the wheel and run Airflow.
If you'd like to make this an official Airflow provider, consider submitting it to the Apache Airflow GitHub.

License
This project is licensed under the MIT License - see the LICENSE file for details.


