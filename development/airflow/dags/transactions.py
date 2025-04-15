from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from datetime import datetime, timedelta
import os
import json

from utils.druid_publishing import druid_publishing

druid_host = Variable.get("DRUID_HOST")
pg_host = Variable.get("PG_HOST")
pg_port = Variable.get("PG_PORT")
pg_user = Variable.get("PG_USER")
pg_password = Variable.get("PG_PASSWORD")
minio_endpoint = Variable.get("MINIO_ENDPOINT")
minio_access_key = Variable.get("MINIO_ACCESS_KEY")
minio_secret_key = Variable.get("MINIO_SECRET_KEY")

default_args = {
    "owner":"airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": None,
    "retry_delay": timedelta(minutes=1)
}

def job_creator(config, general_config, dag):
    
    tier = general_config['tier']
    
    if tier == "tier-data-ingestion":
        
        minio_config = {
            "endpoint": minio_endpoint,
            "access_key": minio_access_key,
            "secret_key": minio_secret_key,
            "minio_bucket": general_config['minio_bucket'],
            "minio_path": general_config['minio_path'],
            "destination_path": config['destination_path']
        }
        
        return SparkSubmitOperator(
            task_id=f"{tier}_{config['name']}_job",
            application=general_config['spark_job_script_path'],
            conn_id='spark_default',
            env_vars = {
                "HADOOP_CONF_DIR":"/etc/hadoop/conf"
            },
            conf={
                "spark.driver.memory": "1G",
                "spark.executor.memory": "1G",
                "spark.executor.cores": "2",
                "spark.sql.parquet.int96RebaseModeInWrite": "CORRECTED",
                "spark.sql.parquet.datetimeRebaseModeInWrite": "LEGACY",
                "spark.hadoop.fs.s3a.endpoint": f"{minio_endpoint}",
                "spark.hadoop.fs.s3a.access.key": f"{minio_access_key}",
                "spark.hadoop.fs.s3a.secret.key": f"{minio_secret_key}",
                "spark.hadoop.fs.s3a.path.style.access": "true",
                "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
                "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            },
            java_class='org.apache.spark.examples.SparkPi',
            jars=f"{general_config['jar_file_path']['postgresql']},{general_config['jar_file_path']['hadoop_aws']},{general_config['jar_file_path']['minio']},{general_config['jar_file_path']['aws_java_sdk']}",
            execution_timeout=timedelta(minutes=30),
            application_args = [
                f'--tableName', config['source_table_name'],
                f'--host', pg_host,
                f'--port', pg_port,
                f'--username', pg_user,
                f'--password', pg_password,
                f'--database', config['source_db_name'],
                f'--schema', config['source_schema_name'],
                f'--generalConfig', json.dumps(general_config),
                f'--minioConfig', json.dumps(minio_config)
                ],
            dag=dag
            )
    elif tier == "tier-data-curation":
        
        minio_config = {
            "endpoint": minio_endpoint,
            "access_key": minio_access_key,
            "secret_key": minio_secret_key,
            "minio_bucket": general_config['minio_bucket'],
            "minio_path": general_config['minio_path'],
            "destination_path": config['destination_path']
        }
        
        return SparkSubmitOperator(
            task_id=f"{tier}_{config['name']}_job",
            application=general_config['spark_job_script_path'],
            conn_id='spark_default',
            env_vars = {
                "HADOOP_CONF_DIR":"/etc/hadoop/conf"
            },
            conf={
                "spark.driver.memory": "1G",
                "spark.executor.memory": "1G",
                "spark.executor.cores": "2",
                "spark.sql.parquet.int96RebaseModeInWrite": "CORRECTED",
                "spark.sql.parquet.datetimeRebaseModeInWrite": "LEGACY",
                "spark.hadoop.fs.s3a.endpoint": f"{minio_endpoint}",
                "spark.hadoop.fs.s3a.access.key": f"{minio_access_key}",
                "spark.hadoop.fs.s3a.secret.key": f"{minio_secret_key}",
                "spark.hadoop.fs.s3a.path.style.access": "true",
                "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
                "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            },
            java_class='org.apache.spark.examples.SparkPi',
            jars=f"{general_config['jar_file_path']['postgresql']},{general_config['jar_file_path']['hadoop_aws']},{general_config['jar_file_path']['minio']},{general_config['jar_file_path']['aws_java_sdk']}",
            execution_timeout=timedelta(minutes=30),
            application_args = [
                f'--configs', json.dumps(config),
                f'--minioConfig', json.dumps(minio_config)
                ],
            dag=dag
            )
    elif tier == "tier-druid-publishing":
        
        task_id=f"{tier}_{config['name']}_job"
        schema_file = general_config['schema_file_path']
        destination_table_name = config['destination_table_name']
        
        minio_config = {
            "endpoint": minio_endpoint,
            "access_key": minio_access_key,
            "secret_key": minio_secret_key,
            "minio_bucket": general_config['minio_bucket'],
            "minio_path": general_config['minio_path'],
            "region_name": "us-east-1",
            "parquet_file_dir": config['parquet_file_dir']
        }
        
        with open(schema_file, "rt") as schema:
            
            schema_json = schema.read()
            
        return PythonOperator(
            task_id=task_id,
            python_callable=druid_publishing,
            op_kwargs={
                'druid_host': druid_host,
                'destination_table_name': destination_table_name,
                'druid_schema': schema_json,
                'minio_configs': minio_config
            },
            dag=dag
        )
            
def config_reader(config_path):
    
    with open(config_path, "rt") as config_file:
        
        config_data = json.loads(config_file.read())
        
    task_group_name = f"{config_data['general']['module_name']}_{config_data['general']['tier']}"
        
    with TaskGroup(group_id=task_group_name) as task_group:
        
        for config in config_data['tasks']:
            
            job_creator(config, config_data['general'], dag)
            
        return task_group
    
with DAG(dag_id="transaction_analysis", default_args=default_args, schedule_interval=None, catchup=False, max_active_runs=1, tags=["transactions"] ) as dag:
    
    start = EmptyOperator(task_id="start_job")
    
    data_ingestion = config_reader("/opt/airflow/dags/configs/data_ingestion.json")
    data_curation = config_reader("/opt/airflow/dags/configs/curated_job.json")
    druid_publish = config_reader("/opt/airflow/dags/configs/druid_publish.json")
    
    end = EmptyOperator(task_id="end_job")
    
    start >> data_ingestion >> data_curation >> druid_publish >> end