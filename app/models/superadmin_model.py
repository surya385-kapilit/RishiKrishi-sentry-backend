from app.config.db import db_pool, get_connection
import secrets
import string


def generate_alphanumeric_id(length=12):
    """Generate a random alphanumeric ID"""
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def get_superadmin_by_email(email):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT email, password, role, full_name FROM superadmins WHERE email = %s",
                (email,),
            )
            return cur.fetchone()
    finally:
        db_pool.putconn(conn)


def get_superadmin_by_id(superadmin_id):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT superadmin_id, email, role, full_name, created_at FROM superadmins WHERE superadmin_id = %s",
                (superadmin_id,),
            )
            return cur.fetchone()
    finally:
        db_pool.putconn(conn)


def get_all_superadmins():
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT superadmin_id, email, role, full_name, created_at FROM superadmins ORDER BY created_at DESC"
            )
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)


def create_superadmin(email, hashed_password, role="SUPERADMIN", full_name=None):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO superadmins (email, password, role, full_name)
                VALUES (%s, %s, %s, %s)
                RETURNING superadmin_id
                """,
                (email, hashed_password, role.upper(), full_name),
            )
            superadmin_id = cur.fetchone()[0]
            conn.commit()
            return superadmin_id
    finally:
        db_pool.putconn(conn)


def update_superadmin_fullname(superadmin_id, full_name):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE superadmins SET full_name = %s WHERE superadmin_id = %s",
                (full_name, superadmin_id),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


def delete_superadmin(superadmin_id):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM superadmins WHERE superadmin_id = %s", (superadmin_id,)
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


# Get Dashboard
def get_superadmin_dashboard_stats():
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Total tenants
            cur.execute("SELECT COUNT(*) FROM tenants")
            total_tenants = cur.fetchone()[0]

            # Active tenants
            cur.execute("SELECT COUNT(*) FROM tenants WHERE is_active = TRUE")
            active_tenants = cur.fetchone()[0]

            # Total tenant users
            cur.execute("SELECT COUNT(*) FROM matrix")
            total_users = cur.fetchone()[0]

            return {
                "total_tenants": total_tenants,
                "active_tenants": active_tenants,
                "total_users": total_users,
            }
    finally:
        db_pool.putconn(conn)
