from kafka import KafkaConsumer
import json
from minio import Minio
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
from io import BytesIO
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# setup environment variables
KAFKA_BOOTSTRAPS_SERVER = os.getenv("KAFKA_BOOTSTRAPS_SERVER", "localhost:19092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "streaming").split(",")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "streaming_group")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ecommerce")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == 'true'


def create_minio_client():
    """Create and return a MinIO client."""
    logging.info(f"Creating MinIO client with endpoint: {MINIO_ENDPOINT}, access_key: {MINIO_ACCESS_KEY}, secure: {MINIO_SECURE}")
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )

def ensure_bucket_exists(minio_client, bucket_name):
    """Ensure the specified bucket exists, create if it doesn't."""
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        logging.info(f"Created bucket: {bucket_name}")
        
def process_message(message, minio_client):
    """Process a Kafka message and store data as parquet in MinIO."""
    try:
        data = json.loads(message.value.decode('utf-8'))
        
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
        file_name = f"data_{timestamp}.parquet"
        
        if data['kind'] == 'update':
            
            old_data = {f"old_{k}": v for k, v in data['old_data'].items()}
            
            data['data'] = {**data['data'], **old_data}
        
        # Ensure data['data'] is a list of dictionaries
        if isinstance(data['data'], dict):
            data_list = [data['data']]  # Wrap single dictionary in a list
        elif isinstance(data['data'], list):
            data_list = data['data']
        else:
            raise ValueError("'data' field must be a dictionary or a list of dictionaries")
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(data_list)
        
        # Convert DataFrame to parquet format in memory
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow')
        parquet_buffer.seek(0)
        
        # Define the object path in MinIO
        object_path = f"{message.topic}/{data['kind']}/{file_name}"
        
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_path,
            data=parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        logging.info(f"Successfully saved parquet to MinIO: {object_path}")
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        
def main():
    """Main function to run the Kafka consumer."""
    logging.info("Starting Kafka consumer for parquet conversion and MinIO storage")
    
    # Initialize MinIO client
    minio_client = create_minio_client()
    ensure_bucket_exists(minio_client, MINIO_BUCKET)
    
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        *KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAPS_SERVER,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='latest',
        enable_auto_commit=True
    )
    
    logging.info(f"Connected to Kafka topic: {KAFKA_TOPIC}")
    
    try:
        for message in consumer:
            logging.info(f"Consume message at: {datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}")
            process_message(message, minio_client)
    except KeyboardInterrupt:
        logging.info("Consumer stopped by user")
    finally:
        consumer.close()
        logging.info("Consumer closed")

if __name__ == "__main__":
    main()