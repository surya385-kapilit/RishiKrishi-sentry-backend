# import os
# from psycopg2 import pool
# from dotenv import load_dotenv

# load_dotenv()

# try:
#     db_pool = pool.SimpleConnectionPool(
#         1,
#         10,
#         dsn=os.getenv("DATABASE_URL")
#     )
    
#     # Test connection
#     conn = db_pool.getconn()
#     if conn:
#         print("Database connection pool established successfully.")
#         db_pool.putconn(conn)
#     else:
#         raise Exception("Failed to retrieve a connection from the pool.")
        
# except Exception as e:
#     print(f"Database connection failed")
#     print(e)

import os
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

try:
    db_pool = pool.SimpleConnectionPool(
        1,   # min connections
        10,  # max connections
        dsn=os.getenv("DATABASE_URL")
    )

    # Test connection
    conn = db_pool.getconn()
    if conn:
        print("✅ Database connection pool established successfully.")
        db_pool.putconn(conn)
    else:
        raise Exception("Failed to retrieve a connection from the pool.")

except Exception as e:
    print("❌ Database connection failed")
    print(e)


def get_connection():
    """
    Safely fetch a connection from the pool and validate it.
    Returns a healthy psycopg2 connection.
    """
    conn = db_pool.getconn()
    try:
        if conn.closed != 0:  # Connection is closed
            conn = db_pool.getconn()
        else:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")  # Simple health check
    except Exception:
        # If validation fails, get a new connection
        conn = db_pool.getconn()
    return conn