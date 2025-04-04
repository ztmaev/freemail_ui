import sqlite3
from config import db_name


# users
# id, uid, username, email, password, avatar_url, is_active, is_await_delete, is_deleted, created_at, updated_at, deleted_at

def create_db():
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            username TEXT,
            role TEXT,
            email TEXT,
            password TEXT,
            avatar_url TEXT,
            is_active INTEGER,
            has_2fa INTEGER,
            is_await_delete INTEGER,
            is_deleted INTEGER,
            created_at TEXT,
            updated_at TEXT,
            deleted_at TEXT
        )
        """)
        conn.commit()

        c.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT,
                theme TEXT,
                timezone TEXT,
                email_notifications TEXT,
                marketing_emails TEXT,
                security_alerts TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS auth_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT,
                code TEXT,
                code_type TEXT,
                session_token TEXT,
                created_at
            )
        """)

        conn.commit()

        c.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT,
                source TEXT,
                title TEXT,
                message TEXT,
                is_seen INTEGER,
                url TEXT,
                seen_at TEXT,
                created_at                
            )""")

        conn.commit()

        c.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT,
                title TEXT,
                message TEXT,
                time TEXT           
            )""")

        conn.commit()

        c.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            api_key TEXT,
            is_active INTEGER,
            created_at TEXT,
            updated_at TEXT
        )
        """)

        conn.commit()
        c.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            api_key TEXT,
            email_type TEXT,
            is_template TEXT,
            template_id TEXT,
            sender_name TEXT,
            receiver_email TEXT,
            email_subject TEXT,
            message_content TEXT,
            footer TEXT,
            is_sent INTEGER,
            error TEXT,
            created_at TEXT
        )
        """)

        conn.close()

        return True, None
    except Exception as e:
        print(e)
        return False, e


if __name__ == '__main__':
    create_db()
