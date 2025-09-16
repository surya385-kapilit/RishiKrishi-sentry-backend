import uuid
import random
from datetime import datetime

from fastapi import HTTPException
from app.config.db import db_pool

from app.models.admin_model import lookup_existing_user_details
from app.utils.security import hash_password


def create_matrix_user(email, full_name, role, phone_no, tenant_id):
    conn = db_pool.getconn()
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()

    new_password_plain = None  # Default to None
    tenant_name = None
    cursor = conn.cursor()
    cursor.execute("SELECT tenant_name FROM tenants WHERE tenant_id = %s", (tenant_id,))
    result = cursor.fetchone()
    if not result:
        raise Exception(f"Tenant with ID {tenant_id} not found.")
    tenant_name = result[0]
    print(f"Tenant name for ID {tenant_id} is {tenant_name}")

    try:
        # Check if user exists globally
        password, _, _, exists = lookup_existing_user_details(email, phone_no)

        if exists:
            hashed_password = password
            print(f"User '{email}' already exists in matrix. Reusing password.")
        else:
            # Generate new password for new user
            new_password_plain = "".join(
                random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=12)
            )
            hashed_password = hash_password(new_password_plain)
            print(f"User '{email}' is new to matrix. Generated password: {new_password_plain}")

        # Insert user into matrix
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO matrix (
                user_id, tenant_id, full_name, email, role,
                phone_no, password, is_active, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
        """, (user_id, tenant_id, full_name, email, role, phone_no, hashed_password, now, now))
        conn.commit()
        cursor.close()

        return user_id, exists, new_password_plain,tenant_name

    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        raise
    finally:
        db_pool.putconn(conn)
        

def update_matrix_user(user_id, email, full_name, role, phone_no, is_active, tenant_id):
    conn = db_pool.getconn()
    now = datetime.utcnow()

    try:
        cursor = conn.cursor()
        # Check if user exists
        cursor.execute("SELECT 1 FROM matrix WHERE user_id = %s AND tenant_id = %s", (user_id, tenant_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Prepare update query
        query = "UPDATE matrix SET full_name = %s"
        params = [full_name]
        if email:
            query += ", email = %s"
            params.append(email)
        if role:
            query += ", role = %s"
            params.append(role)
        if phone_no:
            query += ", phone_no = %s"
            params.append(phone_no)
        if is_active is not None:
            query += ", is_active = %s"
            params.append(is_active)
        query += ", updated_at = %s WHERE user_id = %s AND tenant_id = %s"
        params.extend([now, user_id, tenant_id])

        cursor.execute(query, params)
        conn.commit()
        cursor.close()

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"[ERROR] Failed to update user: {e}")
        raise
    finally:
        db_pool.putconn(conn)

def delete_matrix_user(user_id, tenant_id):
    conn = db_pool.getconn()

    try:
        cursor = conn.cursor()
        # Check if user exists
        cursor.execute("SELECT 1 FROM matrix WHERE user_id = %s AND tenant_id = %s", (user_id, tenant_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Delete user
        cursor.execute("DELETE FROM matrix WHERE user_id = %s AND tenant_id = %s", (user_id, tenant_id))
        conn.commit()
        cursor.close()

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"[ERROR] Failed to delete user: {e}")
        raise
    finally:
        db_pool.putconn(conn)

def update_user_password_in_db(email, new_hashed_password,tenant_id):
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE matrix SET password = %s, updated_at = %s WHERE email = %s AND tenant_id=%s", 
                       (new_hashed_password, datetime.utcnow(), email,tenant_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        cursor.close()
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"[ERROR] Failed to update user password: {e}")
        raise
    finally:
        db_pool.putconn(conn)
