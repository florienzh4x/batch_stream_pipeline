import json
import argparse
import logging
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit

def create_spark_session(minio_configs):

    app_name = "source_to_raw"
    spark = SparkSession.builder.appName(app_name) \
        .config("spark.master", "spark://spark-master:7077") \
        .config("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED") \
        .config("spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY") \
        .config("spark.hadoop.fs.s3a.endpoint", minio_configs['endpoint']) \
        .config("spark.hadoop.fs.s3a.access.key", minio_configs['access_key']) \
        .config("spark.hadoop.fs.s3a.secret.key", minio_configs['secret_key']) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    return spark

def get_data(spark, jdbc_url:str, minio_configs:dict, properties:dict, table_properties:dict):

    schema = table_properties['schema']
    table_name = table_properties['table_name']
    destination_path = f"{minio_configs['minio_bucket']}/{minio_configs['minio_path']}/{minio_configs['destination_path']}"

    query = f"(SELECT * FROM {schema}.{table_name}) AS table_alias"

    df = spark.read \
        .jdbc(url=jdbc_url, table=query, properties=properties)

    df.show()
    
    try:
        df.write.mode("overwrite").parquet(f"s3a://{destination_path}/", compression='snappy')
    except Exception as e:
        raise e
    
def main(table_properties, jdbc_url, connection_properties, minio_configs):

    spark = create_spark_session(minio_configs)

    get_data(spark, jdbc_url, minio_configs, connection_properties, table_properties)
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--tableName", default="")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", default="")
    parser.add_argument("--username", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="")
    parser.add_argument("--schema", default="")
    parser.add_argument("--generalConfig", default="")
    parser.add_argument("--minioConfig", default="")

    args = parser.parse_args()

    table_name = args.tableName
    host = args.host
    port = args.port
    username = args.username
    password = args.password
    database = args.database
    schema = args.schema
    minio_configs = json.loads(args.minioConfig)
    general_config = json.loads(args.generalConfig)

    table_properties = {
        "schema":schema,
        "table_name":table_name
    }

    jdbc_url = f"jdbc:postgresql://{host}:{str(port)}/{database}"

    connection_properties = {
        "user":username,
        "password":password,
        "driver":"org.postgresql.Driver"
    }

    main(table_properties, jdbc_url, connection_properties, minio_configs)