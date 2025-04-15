database_up:
	docker compose -f development/postgresql/docker-compose.yml up --build -d
database_down:
	docker compose -f development/postgresql/docker-compose.yml down

zookeeper_up:
	docker compose -f development/zookeeper/docker-compose.yml up -d
zookeeper_down:
	docker compose -f development/zookeeper/docker-compose.yml down

trino_up:
	docker compose -f development/trino/docker-compose.yml up --build -d
trino_down:
	docker compose -f development/trino/docker-compose.yml down

warehouse_up:
	docker compose -f development/minio/docker-compose.yml up -d
	docker compose -f development/hive/docker-compose.yml up -d
warehouse_down:
	docker compose -f development/minio/docker-compose.yml down
	docker compose -f development/hive/docker-compose.yml down

airflow_up:
	docker compose -f development/airflow/docker-compose.yml up --build -d
airflow_down:
	docker compose -f development/airflow/docker-compose.yml down

spark_up:
	docker compose -f development/spark/docker-compose.yml up --build -d
spark_down:
	docker compose -f development/spark/docker-compose.yml down

druid_up:
	docker compose -f development/druid/docker-compose.yml up -d
druid_down:
	docker compose -f development/druid/docker-compose.yml down

kafka_up:
	docker compose -f development/kafka/docker-compose.yml up -d
kafka_down:
	docker compose -f development/kafka/docker-compose.yml down

kafka_pubsub_up:
	docker compose -f development/kafka_pubsubs/docker-compose.yml up --build -d
kafka_pubsub_down:
	docker compose -f development/kafka_pubsubs/docker-compose.yml down

run_all:
	docker compose -f development/postgresql/docker-compose.yml up --build -d
	docker compose -f development/minio/docker-compose.yml up -d
	docker compose -f development/zookeeper/docker-compose.yml up -d
	docker compose -f development/spark/docker-compose.yml up --build -d
	docker compose -f development/druid/docker-compose.yml up --build -d
	docker compose -f development/airflow/docker-compose.yml up --build -d
	docker compose -f development/hive/docker-compose.yml up --build -d
	docker compose -f development/trino/docker-compose.yml up --build -d
	docker compose -f development/kafka/docker-compose.yml up -d
	docker compose -f development/kafka_pubsubs/docker-compose.yml up --build -d

down_all:
	docker compose -f development/postgresql/docker-compose.yml down
	docker compose -f development/zookeeper/docker-compose.yml down
	docker compose -f development/trino/docker-compose.yml down
	docker compose -f development/minio/docker-compose.yml down
	docker compose -f development/hive/docker-compose.yml down
	docker compose -f development/airflow/docker-compose.yml down
	docker compose -f development/spark/docker-compose.yml down
	docker compose -f development/druid/docker-compose.yml down
	docker compose -f development/kafka/docker-compose.yml down
	docker compose -f development/kafka_pubsubs/docker-compose.yml down