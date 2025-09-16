from app.config.db import db_pool, get_connection
import secrets
import string
from app.utils.security import hash_password
from psycopg2.extras import RealDictCursor


def generate_alphanumeric_id(length=12):
    """Generate a random alphanumeric ID"""
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def generate_random_password(length=12):
    """Generate a random secure password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


def get_admin_by_id(id):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ta.id, ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.role, ta.is_active, ta.created_at, ta.updated_at, t.tenant_name, t.schema_id
                FROM matrix ta
                JOIN tenants t ON ta.tenant_id = t.tenant_id
                WHERE ta.id = %s
                """,
                (id,),
            )
            result = cur.fetchone()
            if result:
                return {
                    "id": result[0],
                    "user_id": result[1],
                    "tenant_id": result[2],
                    "full_name": result[3],
                    "email": result[4],
                    "role": result[5],
                    "is_active": result[6],
                    "created_at": result[7],
                    "updated_at": result[8],
                    "tenant_name": result[9],
                    "schema_id": result[10],
                }
            return None
    finally:
        db_pool.putconn(conn)


def get_admins_login_by_email(email: str):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT ta.id, ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.password, ta.role,
                       ta.is_active,t.tenant_name, t.schema_id
                FROM matrix ta
                JOIN tenants t ON ta.tenant_id = t.tenant_id
                WHERE ta.email = %s
                """,
                (email,),
            )
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)


def get_admins_login_by_tenant(tenant_id: str, email: str = None, phone: str = None):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if email:
                cur.execute(
                    """
                    SELECT ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.phone_no, ta.password, ta.role,
                           ta.is_active, t.tenant_name, t.schema_id
                    FROM matrix ta
                    JOIN tenants t ON ta.tenant_id = t.tenant_id
                    WHERE ta.tenant_id = %s AND ta.email = %s
                    """,
                    (tenant_id, email),
                )
            elif phone:
                cur.execute(
                    """
                    SELECT ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.phone_no, ta.password, ta.role,
                           ta.is_active, t.tenant_name, t.schema_id
                    FROM matrix ta
                    JOIN tenants t ON ta.tenant_id = t.tenant_id
                    WHERE ta.tenant_id = %s AND ta.phone_no = %s
                    """,
                    (tenant_id, phone),
                )
            else:
                cur.execute(
                    """
                    SELECT ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.phone_no, ta.password, ta.role,
                           ta.is_active, t.tenant_name, t.schema_id
                    FROM matrix ta
                    JOIN tenants t ON ta.tenant_id = t.tenant_id
                    WHERE ta.tenant_id = %s
                    """,
                    (tenant_id,),
                )
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)


def get_admins_login(email: str = None, phone: str = None):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if email:
                cur.execute(
                    """
                    SELECT ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.phone_no, ta.password, ta.role,
                           ta.is_active, t.tenant_name, t.schema_id
                    FROM matrix ta
                    JOIN tenants t ON ta.tenant_id = t.tenant_id
                    WHERE ta.email = %s
                    """,
                    (email,),
                )
            elif phone:
                cur.execute(
                    """
                    SELECT ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.phone_no, ta.password, ta.role,
                           ta.is_active, t.tenant_name, t.schema_id
                    FROM matrix ta
                    JOIN tenants t ON ta.tenant_id = t.tenant_id
                    WHERE ta.phone_no = %s
                    """,
                    (phone,),
                )
            return cur.fetchall()
    finally:
        db_pool.putconn(conn)


def get_admin_email(email):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT ta.id, ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.password, ta.role,
                       ta.is_active, ta.created_at, ta.updated_at, t.tenant_name, t.schema_id
                FROM matrix ta
                JOIN tenants t ON ta.tenant_id = t.tenant_id
                WHERE ta.email = %s
                LIMIT 1
                """,
                (email,),
            )
            return cur.fetchone()
    finally:
        db_pool.putconn(conn)


def get_all_admins(page: int, limit: int, tenant_id: int | None, role: str | None):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT ta.id, ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.role,
                       ta.is_active, ta.created_at, ta.updated_at, t.tenant_name, t.schema_id
                FROM matrix ta
                JOIN tenants t ON ta.tenant_id = t.tenant_id
                WHERE 1=1
            """
            params = []

            # Apply filters
            if tenant_id:
                query += " AND ta.tenant_id = %s"
                params.append(tenant_id)

            if role:
                query += " AND ta.role ILIKE %s"
                params.append(role)

            # Count total before pagination
            count_query = f"SELECT COUNT(*) FROM ({query}) AS sub"
            cur.execute(count_query, params)
            total = cur.fetchone()[0]

            # Pagination (page starts from 0)
            query += " ORDER BY ta.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, page * limit])

            cur.execute(query, params)
            results = cur.fetchall()

            admins = [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "tenant_id": row[2],
                    "full_name": row[3],
                    "email": row[4],
                    "role": row[5],
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "tenant_name": row[9],
                    "schema_id": row[10],
                }
                for row in results
            ]
            return admins, total
    finally:
        db_pool.putconn(conn)


def get_admins_by_tenant(tenant_id: str, page: int, limit: int):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Count total
            cur.execute(
                """
                SELECT COUNT(*) 
                FROM matrix ta
                JOIN tenants t ON ta.tenant_id = t.tenant_id
                WHERE ta.tenant_id = %s
                """,
                (tenant_id,),
            )
            total = cur.fetchone()[0]

            # Fetch with pagination
            cur.execute(
                """
                SELECT ta.id, ta.user_id, ta.tenant_id, ta.full_name, ta.email, ta.role, 
                       ta.is_active, ta.created_at, ta.updated_at, t.tenant_name, t.schema_id
                FROM matrix ta
                JOIN tenants t ON ta.tenant_id = t.tenant_id
                WHERE ta.tenant_id = %s
                ORDER BY ta.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (tenant_id, limit, page * limit),
            )
            results = cur.fetchall()

            admins = [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "tenant_id": row[2],
                    "full_name": row[3],
                    "email": row[4],
                    "role": row[5],
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "tenant_name": row[9],
                    "schema_id": row[10],
                }
                for row in results
            ]
            return admins, total
    finally:
        db_pool.putconn(conn)


def create_admin(
    tenant_id,
    full_name,
    email,
    hashed_password=None,
    role="ADMIN",
    user_id=None,
    phone_no=None,
):
    if user_id is None:
        user_id = generate_alphanumeric_id()
    password = hashed_password
    plain_password = None
    if hashed_password is None:
        plain_password = generate_random_password()
        password = hash_password(plain_password)

    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO matrix (user_id, tenant_id, full_name, email, password, role, phone_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, tenant_id, full_name, email, password, role, phone_no),
            )
            conn.commit()
            admin_id = cur.fetchone()[0]
            return admin_id, plain_password
    finally:
        db_pool.putconn(conn)


def update_admin_password(id, new_hashed_password):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE matrix SET password = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_hashed_password, id),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


# -----------------We have to delete this functions------------------
def update_admin_email(id, new_email):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE matrix SET email = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_email, id),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


def update_admin_role(id, new_role):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE matrix SET role = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_role, id),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


def update_admin(id, full_name=None, role=None, is_active=None):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            updates = []
            params = []

            if full_name is not None:
                updates.append("full_name = %s")
                params.append(full_name)

            if role is not None:
                updates.append("role = %s")
                params.append(role)

            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)

            if not updates:
                return False  # Nothing to update

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(id)

            query = f"UPDATE matrix SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


# ---------------------------------------------------------------
##Update Admin IN matrix table


def update_admin_in_matrix(user_id, tenant_id, full_name, is_active):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE matrix
                SET full_name = %s,
                    is_active = %s
                WHERE user_id = %s AND tenant_id = %s
            """,
                (full_name, is_active, user_id, tenant_id),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"[ERROR] Failed to update matrix user: {e}")
        return False
    finally:
        db_pool.putconn(conn)


##Delete Admin from matrix table


def delete_admin_in_matrix(user_id, tenant_id):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM matrix
                WHERE user_id = %s AND tenant_id = %s
            """,
                (user_id, tenant_id),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"[ERROR] Matrix delete failed: {e}")
        return False
    finally:
        db_pool.putconn(conn)


def get_user_details_from_matrix(user_id):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT tenant_id FROM matrix WHERE user_id = %s
            """,
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {"tenant_id": row[0]}
    finally:
        db_pool.putconn(conn)


def delete_admin(id):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM matrix WHERE id = %s", (id,))
            conn.commit()
            return cur.rowcount > 0
    finally:
        db_pool.putconn(conn)


def lookup_existing_user_details(email, phone):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT m.password, m.tenant_id, t.tenant_name
                FROM matrix m
                JOIN tenants t ON m.tenant_id = t.tenant_id
                WHERE m.email = %s OR m.phone_no = %s
                LIMIT 1
            """,
                (email, phone),
            )

            result = cur.fetchone()
            if result:
                password, tenant_id, tenant_name = result
                return password, tenant_name, tenant_id, True
            else:
                return None, None, None, False
    finally:
        db_pool.putconn(conn)


def save_user_in_matrix_table_with_password(
    user_id, tenant_id, full_name, email, phone, password, role
):
    # conn = db_pool.getconn()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO matrix (user_id, tenant_id, full_name, email, phone_no, password,role)
                VALUES (%s, %s, %s, %s, %s, %s,%s)
            """,
                (user_id, tenant_id, full_name, email, phone, password, role),
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving user in matrix table: {e}")
        return False
    finally:
        db_pool.putconn(conn)
