from app.config.db import db_pool
import secrets
import string
import random
from psycopg2.extras import RealDictCursor

def generate_alphanumeric_id(length=12):
    """Generate a random alphanumeric ID"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_tenant(tenant_name, tenant_domain, schema_id):
    tenant_id = generate_alphanumeric_id()
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tenants (tenant_id, tenant_name, tenant_domain, schema_id, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING tenant_id
                """,
                (tenant_id, tenant_name, tenant_domain, schema_id, True)
            )
            conn.commit()
            return cur.fetchone()[0]
    finally:
        db_pool.putconn(conn)


def get_tenant_by_id(tenant_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tenant_id, tenant_name, tenant_domain, schema_id, is_active, created_at FROM tenants WHERE tenant_id = %s",
                (tenant_id,)
            )
            return cur.fetchone()
    finally:
        db_pool.putconn(conn)

def get_tenant_by_domain(tenant_name,tenant_domain):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT tenant_name, tenant_domain 
                FROM tenants 
                WHERE tenant_name = %s OR tenant_domain = %s
                """,
                (tenant_name, tenant_domain)
            )
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)



def get_all_tenants():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tenant_id, tenant_name, tenant_domain, schema_id, is_active, created_at FROM tenants ORDER BY created_at DESC")
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)

## Update Tenant Function

def update_tenant(tenant_id, is_active):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tenants SET is_active = %s WHERE tenant_id = %s",
                (is_active, tenant_id)
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


def delete_tenant(tenant_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM matrix WHERE tenant_id = %s", (tenant_id,))
            cur.execute("DELETE FROM tenants WHERE tenant_id = %s", (tenant_id,))
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)

def create_tenant_admin(tenant_id, full_name, email, hashed_password, role="tenant_admin"):
    user_id = generate_alphanumeric_id()
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tenant_admins (user_id, tenant_id, full_name, email, password, role)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, tenant_id, full_name, email, hashed_password, role)
            )
            conn.commit()
            return cur.fetchone()[0]
    finally:
        db_pool.putconn(conn)
        
def get_admin_by_email(email: str):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, tenant_id, full_name, email, password, role, is_active, created_at, updated_at
                FROM matrix
                WHERE email = %s
                LIMIT 1
                """,
                (email,)
            )
            return cur.fetchone()
    finally:
        db_pool.putconn(conn)


def get_admin_by_email_and_tenant(email: str, tenant_id: str):
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, user_id, tenant_id, full_name, email, password, role, is_active
                FROM matrix
                WHERE email = %s AND tenant_id = %s
                """,
                (email, tenant_id)
            )
            return cur.fetchone()
    finally:
        db_pool.putconn(conn)

##get the tenant schema id

def get_schema_for_tenant(tenant_id: str) -> str:
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT schema_id FROM tenants WHERE tenant_id = %s
            """, (tenant_id,))
            result = cur.fetchone()
            if not result:
                raise ValueError(f"Schema not found for tenant_id: {tenant_id}")
            return result[0]
    except Exception as e:
        print(f"[ERROR] get_schema_for_tenant failed: {e}")
        raise
    finally:
        db_pool.putconn(conn)