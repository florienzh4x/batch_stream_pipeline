import requests
import json
import time
from minio import Minio

def list_minio_files(minio_configs):
    
    s3 = Minio(
        endpoint=minio_configs['endpoint'],
        access_key=minio_configs['access_key'],
        secret_key=minio_configs['access_key'],
        secure=False
    )
    
    response = s3.list_objects(bucket_name=minio_configs['minio_bucket'], prefix=f"{minio_configs['minio_path']}/{minio_configs['parquet_file_dir']}/")
    
    files = []
    
    for obj in response:
        if obj.object_name.endswith('.parquet'):
            files.append(f"s3://{minio_configs['minio_bucket']}/{obj.object_name}")
        
    print(files)
    return files
    
def load_schema(druid_schema, destination_table_name, minio_configs):
    
    schema = json.loads(druid_schema)
    
    schema['spec']['ioConfig']['inputSource']['uris'] = list_minio_files(minio_configs)
    schema['spec']['ioConfig']['inputSource']['properties']['endpoint'] = f"http://{minio_configs['endpoint']}"
    schema['spec']['ioConfig']['inputSource']['properties']['accessKey'] = minio_configs['access_key']
    schema['spec']['ioConfig']['inputSource']['properties']['secretKey'] = minio_configs['secret_key']
    schema['spec']['ioConfig']['inputSource']['properties']['region'] = minio_configs['region_name']
    schema['spec']['dataSchema']['dataSource'] = destination_table_name
    
    print(schema)
    
    return schema
    
def druid_publishing(druid_host, destination_table_name, druid_schema, minio_configs):
    
    druid_schema_local = druid_schema
    
    json_schema = load_schema(druid_schema_local, destination_table_name, minio_configs)
    json_schema = json.dumps(json_schema)

    url = f'{druid_host}/druid/indexer/v1/task'
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json_schema, headers=headers)
    
    print(response)
    print(response.json())
    
    task_id = response.json()['task']
    while True:
        url = f'{druid_host}/druid/indexer/v1/task/{task_id}/status'
        response = requests.get(url)
        data = response.json()
        if data['status']['status'] == 'SUCCESS':
            break
        if data['status']['status'] == 'FAILED':
            raise Exception(f'Task {task_id} failed. Error: {data["status"]["errorMessage"]}')
        print(f'Task {task_id} status: {data["status"]["status"]}. Sleeping for 2 seconds...')
        time.sleep(2)

    print(f'Successfully run json task {task_id}')