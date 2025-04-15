import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from airflow.models import Variable

fake = Faker()

# Database connection
pg_host = Variable.get("PG_HOST")
pg_port = Variable.get("PG_PORT")
pg_user = Variable.get("PG_USER")
pg_password = Variable.get("PG_PASSWORD")
pg_dbname = Variable.get("PG_DBNAME")

db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_dbname}"
engine = create_engine(db_url)

# Generate products table
def generate_products(n=10000, stores=None):
    
    brand_cat = {
        'Samsung': ['Electronics', 'Computer & Laptop', 'Gadget'],
        'HOUSE OF SMITH': ['Clothing'],
        'informa': ['Furniture', 'Home & Kitchen', 'Garden'],
        'RandzInc': ['Electronics', 'Clothing'],
        'Florienzh': ['Home & Kitchen', 'Sports'],
        'BallBoy': ['Toys'],
        'Baracuda': ['Fishing'],
        'BlackCat': ['Animal', 'Lifestyle'],
        'DeroOps': ['Electronics', 'Clothing'],
    }
    
    data = []
    for i in range(n):
        
        brand = random.choice(list(brand_cat.keys()))
        
        data.append({
            "product_id": f"P{i+1}",
            "store_id": random.choice(stores["store_id"].tolist()),
            "product_name": fake.word().capitalize(),
            "category": random.choice(brand_cat[brand]),
            "brand": brand,
            "price": round(random.uniform(10, 1000), 2)
        })
    
    return pd.DataFrame(data)

# Generate customers table
def generate_customers(n=5000):
    province_city = {
        'DKI Jakarta': ['Jakarta Utara', 'Jakarta Timur', 'Jakarta Barat', 'Jakarta Selatan', 'Jakarta Pusat'],
        'Jawa Barat': ['Bandung', 'Bekasi', 'Cirebon', 'Depok', 'Sukabumi', 'Tasikmalaya', 'Bogor', 'Ciamis', 'Garut'],
        'Jawa Tengah': ['Semarang', 'Surakarta', 'Pekalongan', 'Salatiga', 'Magelang', 'Tegal', 'Banyumas', 'Wonogiri', 'Klaten', 'Karanganyar'],
        'Jawa Timur': ['Surabaya', 'Sidoarjo', 'Mojokerto', 'Pasuruan', 'Kediri', 'Blitar', 'Madiun', 'Malang', 'Banyuwangi', 'Jombang'],
        'DI Yogyakarta': ['Yogyakarta'],
        'Banten': ['Serang', 'Tangerang', 'Pandeglang', 'Lebak', 'Tangerang Selatan', 'Tangerang Utara'],
    }
    
    data = []
    for i in range(n):
        
        province = random.choice(list(province_city.keys()))
        city = random.choice(province_city[province])
        
        data.append({
            "customer_id": f"C{i+1}",
            "customer_name": fake.name(),
            "gender": random.choice(['Male', 'Female']),
            "age": random.randint(18, 70),
            "province": province,
            "city": city
        })
    
    return pd.DataFrame(data)

# Generate stores table
def generate_stores(n=500):
    
    province_city = {
        'DKI Jakarta': ['Jakarta Utara', 'Jakarta Timur', 'Jakarta Barat', 'Jakarta Selatan', 'Jakarta Pusat'],
        'Jawa Barat': ['Bandung', 'Bekasi', 'Cirebon', 'Depok', 'Sukabumi', 'Tasikmalaya', 'Bogor', 'Ciamis', 'Garut'],
        'Jawa Tengah': ['Semarang', 'Surakarta', 'Pekalongan', 'Salatiga', 'Magelang', 'Tegal', 'Banyumas', 'Wonogiri', 'Klaten', 'Karanganyar'],
        'Jawa Timur': ['Surabaya', 'Sidoarjo', 'Mojokerto', 'Pasuruan', 'Kediri', 'Blitar', 'Madiun', 'Malang', 'Banyuwangi', 'Jombang'],
        'DI Yogyakarta': ['Yogyakarta'],
        'Banten': ['Serang', 'Tangerang', 'Pandeglang', 'Lebak', 'Tangerang Selatan', 'Tangerang Utara'],
    }
    
    data = []
    for i in range(n):
        
        province = random.choice(list(province_city.keys()))
        city = random.choice(province_city[province])
        
        data.append({
            "store_id": f"S{i+1}",
            "store_name": fake.company(),
            "location": city
        })
    
    return pd.DataFrame(data)

# Generate payments table
def generate_payments(n=10000):
    statuses = ['Completed', 'Failed']
    
    data = []
    for i in range(n):
        data.append({
            "payment_id": f"PMT{i+1}",
            "payment_method": random.choice(["Credit", "Debit", "eWallet"]),
            "payment_status": random.choice(statuses)
        })
    
    return pd.DataFrame(data)

# Generate orders table
def generate_orders(n=10000, customers=None, stores=None):
    data = []
    for i in range(n):
        data.append({
            "order_id": f"O{i+1}",
            "customer_id": random.choice(customers["customer_id"].tolist()),
            "store_id": random.choice(stores["store_id"].tolist()),
            "order_date": fake.date_between(start_date="-1y", end_date="today"),
            "order_status": random.choice(["Pending", "Completed", "Cancelled"])
        })
    
    return pd.DataFrame(data)

# Generate transactions table
def generate_transactions(n=10000, products=None, customers=None, stores=None, payments=None, orders=None):
    data = []
    for _ in range(n):
        data.append({
            "transaction_id": fake.uuid4(),
            "order_id": random.choice(orders["order_id"].tolist()),
            "product_id": random.choice(products["product_id"].tolist()),
            "customer_id": random.choice(customers["customer_id"].tolist()),
            "store_id": random.choice(stores["store_id"].tolist()),
            "payment_id": random.choice(payments["payment_id"].tolist()),
            "transaction_date": fake.date_between(start_date="-1y", end_date="today"),
            "quantity": random.randint(1, 5),
            "total_price": round(random.uniform(10, 5000), 2),
            "discount": round(random.uniform(0, 50), 2),
            "tax_amount": round(random.uniform(1, 200), 2),
            "is_refunded": random.choice([True, False]),
            "inserted_at": datetime.now()
        })
    
    return pd.DataFrame(data)

def generate(start: int, end: int):
    randddd = random.randint(start, end)

    # Generate datasets
    df_stores = generate_stores(n=randddd)
    df_products = generate_products(stores=df_stores, n=randddd)
    df_customers = generate_customers(n=randddd)
    df_payments = generate_payments(n=randddd)
    df_orders = generate_orders(n=randddd, customers=df_customers, stores=df_stores)
    df_transactions = generate_transactions(n=randddd, products=df_products, customers=df_customers, stores=df_stores, payments=df_payments, orders=df_orders)

    # Store data to PostgreSQL using batch insert
    df_products.to_sql("products", con=engine, if_exists="replace", index=False, method="multi")
    df_customers.to_sql("customers", con=engine, if_exists="replace", index=False, method="multi")
    df_stores.to_sql("stores", con=engine, if_exists="replace", index=False, method="multi")
    df_payments.to_sql("payments", con=engine, if_exists="replace", index=False, method="multi")
    df_orders.to_sql("orders", con=engine, if_exists="replace", index=False, method="multi")
    df_transactions.to_sql("transactions", con=engine, if_exists="replace", index=False, method="multi")

    print("Raw data ingestion to PostgreSQL completed with enhanced complexity!")