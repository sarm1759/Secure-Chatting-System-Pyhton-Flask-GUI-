import sqlite3
from datetime import datetime

def connect_db():
    """Database file se connect karta hai aur cursor return karta hai."""
    conn = sqlite3.connect('users.db')
    return conn

def create_tables():
    """Application ki shuruat mein tables bananay ke liye."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Users Table
    # role: 'admin' ya 'user'
    # is_blacklisted: 0 (False) ya 1 (True)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_blacklisted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Admin account agar pehle se nahi hai toh bana deta hai
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ('admin', 'admin123', 'admin'))
    except sqlite3.IntegrityError:
        pass # Admin pehle se mojood hai
        
    conn.commit()
    conn.close()

# --- User Functionalities ---

def signup_user(username, password):
    """Naye user ko register karne ke liye."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True, "Signup Successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    finally:
        conn.close()

def login_user(username, password):
    """User login check aur blacklist check."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_blacklisted FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        role, is_blacklisted = user
        if is_blacklisted == 1:
            return False, "Your account is blacklisted!", None
        return True, "Login Successful!", role
    else:
        return False, "Invalid username or password!", None

# --- Admin Functionalities ---

def get_all_users():
    """Admin ke liye tamam users ki list."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, is_blacklisted FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def update_blacklist_status(username, status):
    """Admin kisi user ko blacklist (1) ya un-blacklist (0) kar sakta hai."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blacklisted = ? WHERE username = ?", (status, username))
    conn.commit()
    conn.close()
    return True

def remove_user(username):
    """Admin kisi user ko delete kar sakta hai."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True

# Program pehli baar chalte waqt table bananay ke liye
if __name__ == "__main__":
    create_tables()
    print("Database and Tables created successfully!")