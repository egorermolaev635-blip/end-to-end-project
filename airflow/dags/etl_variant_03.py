import os

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = os.environ.get("ETL_PROJECT_DIR", "/opt/airflow/project")
DB_URL = os.environ.get(
    "DB_URL",
    "postgresql+psycopg2://analytics:analytics_pass@postgres:5432/analytics_db",
)
CONFIG_PATH = "variant_03.yml"

with DAG(
    dag_id="etl_variant_03",
    description="Сквозной ETL: extract -> transform -> load -> dq",
    start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["etl", "variant_03", "week11"],
    default_args={"owner": "variant_03"},
) as dag:
    extract = BashOperator(
        task_id="extract",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f'echo "config: {CONFIG_PATH}" && '
            "python src/extract.py"
        ),
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f'echo "config: {CONFIG_PATH}" && '
            "python src/transform.py"
        ),
    )

    load = BashOperator(
        task_id="load",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f'export DB_URL="{DB_URL}" && '
            f'echo "config: {CONFIG_PATH}" && '
            f'echo "db: {DB_URL}" && '
            "python src/load.py"
        ),
    )

    dq = BashOperator(
        task_id="dq",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f'echo "config: {CONFIG_PATH}" && '
            "python src/dq.py"
        ),
    )

    extract >> transform >> load >> dq
