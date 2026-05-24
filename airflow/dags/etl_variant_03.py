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
    description="Сквозной инкрементальный ETL: extract -> transform -> dq -> load",
    start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),
    schedule="0 2 * * *",
    catchup=False,
    tags=["etl", "variant_03", "week12"],
    default_args={"owner": "variant_03"},
) as dag:
    
    extract = BashOperator(
        task_id="extract",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/extract.py --date {{{{ ds }}}}"
        ),
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/transform.py --date {{{{ ds }}}}"
        ),
    )

    dq = BashOperator(
        task_id="dq",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/dq.py --date {{{{ ds }}}}"
        ),
    )

    load = BashOperator(
        task_id="load",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f'export DB_URL="{DB_URL}" && '
            f"python src/load.py --date {{{{ ds }}}}"
        ),
    )

    extract >> transform >> dq >> load
