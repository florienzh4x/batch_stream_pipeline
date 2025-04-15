import psycopg2
from psycopg2.extras import LogicalReplicationConnection
import json
from datetime import datetime
import pytz
import logging
import os
from kafka import KafkaProducer


logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# setup environment variables
KAFKA_BOOTSTRAPS_SERVER = os.getenv("KAFKA_BOOTSTRAPS_SERVER", "localhost:19092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "streaming")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce")
POSTGRES_REPLICATION_SLOT_NAME = os.getenv("POSTGRES_REPLICATION_SLOT_NAME", "streaming_slot")
POSTGRES_REPLICATION_PLUGIN = os.getenv("POSTGRES_REPLICATION_PLUGIN", "wal2json")
POSTGRES_PUBLICATION_NAME = os.getenv("POSTGRES_PUBLICATION_NAME", "streaming_publication")

def setup_kafka_producer():
    global KAFKA_BOOTSTRAPS_SERVER
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAPS_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None
        )
        logging.info("Connected to Kafka at %s", KAFKA_BOOTSTRAPS_SERVER)
        return producer
    except Exception as e:
        logging.error("Failed to connect to Kafka: %s", e)
        raise

def ensure_replica_identity_full(table_name, schema='public'):
    """Ensure the table has REPLICA IDENTITY FULL set for proper CDC"""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Check current replica identity setting
        cursor.execute(f"""
            SELECT relreplident 
            FROM pg_class c
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = %s AND n.nspname = %s
        """, (table_name, schema))
        
        result = cursor.fetchone()
        if result and result[0] != 'f':  # 'f' means FULL
            # Set REPLICA IDENTITY to FULL for the table
            cursor.execute(f'ALTER TABLE {schema}.{table_name} REPLICA IDENTITY FULL')
            logging.info(f"Set REPLICA IDENTITY FULL for {schema}.{table_name}")
        else:
            logging.info(f"Table {schema}.{table_name} already has appropriate REPLICA IDENTITY")
            
    except Exception as e:
        logging.error(f"Error setting REPLICA IDENTITY: {e}")
    finally:
        cursor.close()
        conn.close()

# Create PostgreSQL publication and replication slot
def setup_postgres_replication():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Check if publication exists, create if not
        cursor.execute(f"SELECT 1 FROM pg_publication WHERE pubname = '{POSTGRES_PUBLICATION_NAME}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE PUBLICATION {POSTGRES_PUBLICATION_NAME} FOR ALL TABLES")
            logging.info("Created publication: %s", POSTGRES_PUBLICATION_NAME)
        else:
            logging.info("Publication %s already exists", POSTGRES_PUBLICATION_NAME)

        # Check if replication slot exists, create if not
        cursor.execute(f"SELECT 1 FROM pg_replication_slots WHERE slot_name = '{POSTGRES_REPLICATION_SLOT_NAME}'")
        if not cursor.fetchone():
            cursor.execute(f"SELECT pg_create_logical_replication_slot('{POSTGRES_REPLICATION_SLOT_NAME}', 'wal2json')")
            logging.info("Created replication slot: %s", POSTGRES_REPLICATION_SLOT_NAME)
        else:
            logging.info("Replication slot %s already exists", POSTGRES_REPLICATION_SLOT_NAME)
            
        # Get all tables in the database
        cursor.execute("""
            SELECT tablename, schemaname 
            FROM pg_tables 
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        """)
        
        tables = cursor.fetchall()
        for table_name, schema in tables:
            ensure_replica_identity_full(table_name, schema)

    except Exception as e:
        logging.error("Error setting up replication: %s", e)
        raise
    finally:
        cursor.close()
        conn.close()

def handle_message(msg, producer):
    """Handle incoming replication messages"""
    logging.info(f"Received message: {msg.payload}")
    
    global KAFKA_TOPIC

    # Process the message payload
    try:
        change_data = json.loads(msg.payload).get('change')
        
        for iter_change_data in change_data:
            
            kind = iter_change_data.get('kind')
            
            if kind == 'insert':
                schema = iter_change_data.get('schema')
                table = iter_change_data.get('table')
                columnname = iter_change_data.get('columnnames')
                columnvalues = iter_change_data.get('columnvalues')
                data = dict(zip(columnname, columnvalues))
                capture_time = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')
            
                data = {
                    "kind":kind,
                    "schema":schema,
                    "table":table,
                    "data":data,
                    "capture_time": capture_time,
                }
            elif kind == 'update':
                schema = iter_change_data.get('schema')
                table = iter_change_data.get('table')
                columnname = iter_change_data.get('columnnames')
                columnvalues = iter_change_data.get('columnvalues')
                data = dict(zip(columnname, columnvalues))
                oldkeys = iter_change_data.get('oldkeys')
                oldkeys_columnname = oldkeys.get('keynames')
                oldkeys_columnvalues = oldkeys.get('keyvalues')
                old_data = dict(zip(oldkeys_columnname, oldkeys_columnvalues))
                capture_time = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')
                
                data = {
                    "kind":kind,
                    "schema":schema,
                    "table":table,
                    "data":data,
                    "old_data":old_data,
                    "capture_time": capture_time,
                }
            elif kind == 'delete':
                schema = iter_change_data.get('schema')
                table = iter_change_data.get('table')
                oldkeys = iter_change_data.get('oldkeys')
                oldkeys_columnname = oldkeys.get('keynames')
                oldkeys_columnvalues = oldkeys.get('keyvalues')
                old_data = dict(zip(oldkeys_columnname, oldkeys_columnvalues))
                capture_time = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')
                
                data = {
                    "kind":kind,
                    "schema":schema,
                    "table":table,
                    "data":old_data,
                    "capture_time": capture_time,
                }
            
            
            producer.send(KAFKA_TOPIC, data)
            producer.flush()

            # Process the data as needed
            logging.info(f"Change detected: {kind} on {schema}.{table} with data: {json.dumps(data)}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise

def start_cdc_process(producer):
    # Connect to PostgreSQL with logical replication
    replication_conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        connection_factory=LogicalReplicationConnection
    )

    # Create cursor for replication
    replication_cursor = replication_conn.cursor()

    try:
        # Start replication
        replication_cursor.start_replication(
            slot_name=POSTGRES_REPLICATION_SLOT_NAME,
            decode = True
        )

        logging.info("Started replication from PostgreSQL to Kafka")

        # Process replication stream
        def consume_stream(msg):
            handle_message(msg, producer)
            msg.cursor.send_feedback(flush_lsn=msg.data_start)

        # Start consuming
        replication_cursor.consume_stream(consume_stream)

    except Exception as e:
        logging.error(f"Replication error: {e}")
        raise
    finally:
        replication_cursor.close()
        replication_conn.close()

producer = setup_kafka_producer()
setup_postgres_replication()

while True:
    try:
        start_cdc_process(producer)
    
    except KeyboardInterrupt:
        logging.info("Consumer stopped by user")
    except:
        logging.error("Error in replication process, restarting...")
        producer.close()
        producer = setup_kafka_producer()
        setup_postgres_replication()
        continue