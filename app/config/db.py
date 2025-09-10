import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

try:
    db_pool = pool.SimpleConnectionPool(
        1,
        10,
        dsn=os.getenv("DATABASE_URL")
    )
    
    # Test connection
    conn = db_pool.getconn()
    if conn:
        print("Database connection pool established successfully.")
        db_pool.putconn(conn)
    else:
        raise Exception("Failed to retrieve a connection from the pool.")
        
except Exception as e:
    print(f"Database connection failed")
    print(e)