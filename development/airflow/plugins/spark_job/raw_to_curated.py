import json
import argparse
import logging
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit


def create_spark_session(minio_configs):

    app_name = "raw_to_curated"
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


def execute_transformation(spark, configs, minio_configs):

    ## READ CONFIG ##
    tables = configs['source_path']
    sql_script_path = configs['sql_script_path']
    destination_path = f"{minio_configs['minio_bucket']}/{minio_configs['minio_path']}/{minio_configs['destination_path']}"


    ## READ SQL FILE ##

    with open(sql_script_path, 'r') as sql_file:

        sql_script = sql_file.read()
        
    for table, source_path in tables.items():

        ## READ PARQUET ##
        parquet_source_path = f"{minio_configs['minio_bucket']}/{source_path}"
        
        df = spark.read.parquet(f"s3a://{parquet_source_path}")
        
        df.createOrReplaceTempView(table)

    result = spark.sql(sql_script)

    print(result.count())

    result.show()

    result.write.mode("overwrite").parquet(f"s3a://{destination_path}/", compression='snappy')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--configs", default="")
    parser.add_argument("--minioConfig", default="")
    
    args = parser.parse_args()

    configs = json.loads(args.configs)
    minio_configs = json.loads(args.minioConfig)

    spark = create_spark_session(minio_configs)

    execute_transformation(spark, configs, minio_configs)
