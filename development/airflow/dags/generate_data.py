from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

from utils.generator import generate


default_args = {
    "owner":"airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": None,
    "retry_delay": timedelta(minutes=1)
}

with DAG(dag_id="generate_data", default_args=default_args, schedule_interval=None, catchup=False, max_active_runs=1, tags=["generator"] ) as dag:
    
    start = EmptyOperator(task_id="start_job")
    
    generate_data = PythonOperator(
            task_id="generate_data",
            python_callable=generate,
            op_kwargs={
                'start': 10,
                'end': 20
            },
        )
    
    end = EmptyOperator(task_id="end_job")
    
    start >> generate_data >> end