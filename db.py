import base64
import datetime
import random
import sqlite3
import uuid

import bcrypt

from config import db_name, url_hash_secret_key


def encode_url(text: str) -> str:
    combined_text = text + url_hash_secret_key
    encoded_bytes = base64.b64encode(combined_text.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


def decode_url(encoded_text: str) -> str:
    decoded_bytes = base64.b64decode(encoded_text)
    decoded_text = decoded_bytes.decode('utf-8')
    original_text = decoded_text.replace(url_hash_secret_key, '')
    return original_text


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def generate_uid():
    return str(uuid.uuid4())


def generate_2fa_code():
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    length = 6
    code = ''.join(random.choice(chars) for _ in range(length))
    return code


def generate_api_key():
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    length = 16
    code = ''.join(random.choice(chars) for _ in range(length))
    return code


def current_time():
    time = datetime.datetime.now()
    formated_time = time.strftime("%Y-%m-%d %H:%M:%S")
    return formated_time


def compare_timestamps(ts1: str, ts2: str):
    fmt = "%Y-%m-%d %H:%M:%S"
    time1 = datetime.datetime.strptime(ts1, fmt)
    time2 = datetime.datetime.strptime(ts2, fmt)

    diff = abs(time1 - time2)

    return diff.seconds


def days_active(account_created: str, current_time_now: str = current_time()) -> int:
    """Returns the number of days a user has been active based on their creation time."""
    fmt = "%Y-%m-%d %H:%M:%S"
    account_time = datetime.datetime.strptime(account_created, fmt)
    current_time = datetime.datetime.strptime(current_time_now, fmt)
    delta = current_time - account_time
    return delta.days


def get_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor


def fetch_user(input_value, value_type):
    conn, cursor = get_db()
    if value_type == 'email':
        cursor.execute("SELECT * FROM users WHERE email = ?", (input_value,))
    elif value_type == 'username':
        cursor.execute("SELECT * FROM users WHERE username = ?", (input_value,))
    elif value_type == 'uid':
        cursor.execute("SELECT * FROM users WHERE uid = ?", (input_value,))

    else:
        # print(value_type)
        return None
    # return userinfo
    userdata = cursor.fetchone()
    conn.close()

    # parse
    if userdata:
        userinfo = {
            'uid': userdata[1],
            'username': userdata[2],
            'role': userdata[3],
            'email': userdata[4],
            'password': userdata[5],
            'avatar_url': userdata[6],
            'is_active': userdata[7],
            'has_2fa': userdata[8],
            'is_await_delete': userdata[9],
            'is_deleted': userdata[10],
            'created_at': userdata[11],
            'updated_at': userdata[12],
            'deleted_at': userdata[13]
        }

        return userinfo

    return None


def save_user(user_info):
    try:
        conn, cursor = get_db()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            None, user_info['uid'], user_info['username'], user_info['role'], user_info['email'], user_info['password'],
            user_info['avatar_url'], user_info['is_active'], user_info['has_2fa'], user_info['is_await_delete'],
            user_info['is_deleted'], current_time(), current_time(), user_info['deleted_at']
        ))
        conn.commit()

        conn.close()

        return True, None

    except Exception as e:
        print(e)
        return False, e


def update_user(user_id, updated_info):
    conn, cursor = get_db()

    # Create SET clause dynamically based on provided fields
    set_clause = ", ".join(f"{field} = ?" for field in updated_info.keys())
    values = list(updated_info.values())
    values.append(user_id)  # Append user_id for WHERE clause

    # Construct and execute the SQL query
    sql_query = f"UPDATE users SET {set_clause} WHERE uid = ?"
    cursor.execute(sql_query, tuple(values))

    # update updated_at
    cursor.execute("UPDATE users SET updated_at = ? WHERE uid = ?", (current_time(), user_id))

    conn.commit()
    conn.close()


def fetch_user_preferences(uid):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM user_preferences WHERE uid =?", (uid,))
    preferences = cursor.fetchone()
    conn.close()
    if preferences:
        preferences_info = {
            'id': preferences[0],
            'uid': preferences[1],
            'theme': preferences[2],
            'timezone': preferences[3],
            'email_notifications': preferences[4],
            'marketing_emails': preferences[5],
            'security_alerts': preferences[6],
            'created_at': preferences[7],
            'updated_at': preferences[8]
        }

        return preferences_info

    return None


def update_user_preferences(uid, preferences):
    conn, cursor = get_db()

    # Check if the user already has a preferences entry
    cursor.execute("SELECT COUNT(*) FROM user_preferences WHERE uid = ?", (uid,))
    exists = cursor.fetchone()[0]

    if exists:
        # Create SET clause dynamically based on provided fields
        set_clause = ", ".join(f"{field} = ?" for field in preferences.keys())
        values = list(preferences.values()) + [current_time(), uid]

        # Update existing entry
        sql_query = f"UPDATE user_preferences SET {set_clause}, updated_at = ? WHERE uid = ?"
        cursor.execute(sql_query, tuple(values))
    else:
        # Convert dict_keys to list before concatenation
        columns = ", ".join(list(preferences.keys()) + ["uid", "updated_at"])
        placeholders = ", ".join(["?"] * (len(preferences) + 2))
        values = list(preferences.values()) + [uid, current_time()]

        # Insert new row
        sql_query = f"INSERT INTO user_preferences ({columns}) VALUES ({placeholders})"
        cursor.execute(sql_query, tuple(values))

    conn.commit()
    conn.close()


def save_auth_code(uid, code, code_type, session_token=None):
    conn, cursor = get_db()

    # check if code already exists
    cursor.execute("SELECT * FROM auth_codes WHERE uid = ? AND code_type = ?", (uid, code_type))
    if cursor.fetchone():
        # replace the code if it already exists
        cursor.execute("DELETE FROM auth_codes WHERE uid = ? AND code_type = ?", (uid, code_type))

    cursor.execute("INSERT INTO auth_codes VALUES (?, ?, ?, ?, ?, ?)",
                   (None, uid, code, code_type, session_token, current_time()))
    conn.commit()
    conn.close()


def fetch_auth_code(uid, code_type):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM auth_codes WHERE uid = ? AND code_type = ?", (uid, code_type))
    auth_code = cursor.fetchone()
    conn.close()

    if not auth_code:
        return None

    code_info = {
        'code': auth_code[2],
        'session_token': auth_code[4],
        'created_at': auth_code[5]
    }

    return code_info


def delete_auth_code(uid, code_type):
    conn, cursor = get_db()
    cursor.execute("DELETE FROM auth_codes WHERE uid = ? AND code_type = ?", (uid, code_type))
    conn.commit()
    conn.close()


def delete_user_registration(email_username):
    conn, cursor = get_db()
    cursor.execute("DELETE FROM users WHERE email = ?", (email_username,))
    conn.commit()
    conn.close()


def add_notification(uid, source, title, message, url=None):
    conn, cursor = get_db()
    cursor.execute("INSERT INTO notifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (None, uid, source, title, message, 0, url, current_time(), current_time()))
    conn.commit()
    conn.close()


def fetch_notifications(uid):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM notifications WHERE uid = ?", (uid,))
    notifications = cursor.fetchall()
    conn.close()

    notifs = []

    for notif in notifications:
        notifs.append({
            'id': notif[0],
            'source': notif[2],
            'title': notif[3],
            'message': notif[4],
            'is_seen': notif[5],
            'url': notif[6],
            'seen_at': notif[7],
            'created_at': notif[8]
        })

    if notifs:
        # reverse the list
        notifs.reverse()

    return notifs


def notif_mark_as_seen(uid, notif_id):
    conn, cursor = get_db()
    cursor.execute("UPDATE notifications SET is_seen = 1 , seen_at = ? WHERE uid = ? AND id = ?",
                   (current_time(), uid, notif_id))
    conn.commit()
    conn.close()


def clear_all_notifications(uid):
    try:
        conn, cursor = get_db()
        cursor.execute("UPDATE notifications SET is_seen = 1 , seen_at = ? WHERE uid = ?", (current_time(), uid))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


# logs
def add_log(uid, log_content):
    conn, cursor = get_db()
    cursor.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?)",
                   (None, uid, log_content['title'], log_content['message'], current_time()))
    conn.commit()
    conn.close()


def fetch_logs(uid):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM logs WHERE uid = ?", (uid,))
    logs = cursor.fetchall()
    conn.close()

    logs_data = []

    for log in logs:
        logs_data.append({
            'id': log[0],
            'title': log[2],
            'message': log[3],
            'time': log[4]
        })

    if logs_data:
        # reverse the list
        logs_data.reverse()

        return logs_data
    else:
        return None


def fetch_api_key(uid):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM api_keys WHERE uid = ?", (uid,))
    api_key = cursor.fetchone()
    conn.close()

    if api_key:
        return api_key[2]
    else:
        return None


def verify_api_key(api_key):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM api_keys WHERE api_key = ?", (api_key,))
    api_key_info = cursor.fetchone()
    conn.close()
    if not api_key_info:
        return False, 'Invalid API key'

    is_active = api_key_info[3]

    if api_key_info:
        if is_active == 0 or is_active == '0' or is_active == '':
            return False, 'Activate your API key in account settings'
        else:
            return True, 'Active API key'
    else:
        return False, 'Invalid API key'


def add_api_key(uid, api_key):
    try:
        conn, cursor = get_db()
        cursor.execute("INSERT INTO api_keys VALUES (?, ?, ?, ?, ?, ?)",
                       (None, uid, api_key, 1, current_time(), current_time()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def enable_api_key(uid, api_key):
    try:
        conn, cursor = get_db()
        cursor.execute("UPDATE api_keys SET is_active = 1, updated_at = ? WHERE uid = ? AND api_key = ?",
                       (current_time(), uid, api_key))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def disable_api_key(uid, api_key):
    try:
        conn, cursor = get_db()
        cursor.execute("UPDATE api_keys SET is_active = 0, updated_at = ? WHERE uid = ? AND api_key = ?",
                       (current_time(), uid, api_key))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def delete_api_key(uid, api_key):
    try:
        conn, cursor = get_db()
        cursor.execute("DELETE FROM api_keys WHERE uid = ? AND api_key = ?", (uid, api_key))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def fetch_uid(api_key):
    conn, cursor = get_db()
    cursor.execute("SELECT uid FROM api_keys WHERE api_key = ?", (api_key,))
    uid = cursor.fetchone()
    conn.close()
    if uid:
        return uid[0]
    else:
        return None


def save_email_log(receiver_email, sender_name, email_subject, message_content, email_type, api_key, is_template=False,
                   template_id=None, is_sent=1, error=None, footer=None):
    conn, cursor = get_db()
    uid = fetch_uid(api_key)
    cursor.execute("INSERT INTO email_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        None, uid, api_key, email_type, is_template, template_id, sender_name, receiver_email,
        email_subject, message_content, footer, is_sent, error, current_time()))
    conn.commit()
    conn.close()


def fetch_user_email_log(uid, number_of_items=None, page=None, search_query=None, status=None, date_from=None,
                         date_to=None):
    conn, cursor = get_db()

    try:
        # Base query to fetch logs for the specific user
        query = "SELECT * FROM email_logs WHERE uid = ?"
        params = [uid]

        # Add search filters if provided
        if search_query:
            query += " AND (receiver_email LIKE ? OR email_subject LIKE ? OR sender_name LIKE ?)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term])

        # Filter by status if provided
        if status:
            if status == 'delivered':
                query += " AND is_sent = 1"
            elif status == 'failed':
                query += " AND is_sent = 0 AND error IS NOT NULL"
            elif status == 'pending':
                query += " AND is_sent = 0 AND error IS NULL"

        # Filter by date range if provided
        if date_from:
            query += " AND created_at >= ?"
            params.append(date_from)
        if date_to:
            query += " AND created_at <= ?"
            params.append(date_to)

        # Add ordering
        query += " ORDER BY created_at DESC"

        # If pagination is requested
        if number_of_items is not None and page is not None:
            # Validate inputs
            if number_of_items <= 0 or page <= 0:
                raise ValueError("number_of_items and page must be positive integers")

            # Calculate offset for pagination
            offset = (page - 1) * number_of_items
            query += " LIMIT ? OFFSET ?"
            params.extend([number_of_items, offset])
            cursor.execute(query, tuple(params))
        else:
            # Fetch all logs if no pagination specified
            cursor.execute(query, tuple(params))

        logs = cursor.fetchall()

        # Convert logs to list of dictionaries
        email_logs = []
        for log in logs:
            email_logs.append({
                'id': log[0],
                'email_type': log[3],
                'is_template': log[4],
                'template_id': log[5],
                'sender_name': log[6],
                'receiver_email': log[7],
                'subject': log[8],
                'content': log[9],
                'footer': log[10],
                'is_sent': log[11],
                'error': log[12],
                'created_at': log[13]
            })

        return email_logs if email_logs else None

    except Exception as e:
        # Log the error or handle it appropriately
        # print(f"Error fetching email logs: {e}")
        return None

    finally:
        # Ensure connection is closed
        conn.close()
