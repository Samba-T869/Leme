import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    
    # Payments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            whatsapp_number TEXT NOT NULL,
            user_name TEXT, 
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'pending',
            confirmation_token TEXT,
            payment_method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP,
            confirmed_at TIMESTAMP,
            admin_notified INTEGER DEFAULT 0
        )
    ''')
    
    # Admin table for invitation links
    c.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp_number TEXT UNIQUE,
            invitation_link TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            joined INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def add_payment(transaction_id, whatsapp_number, amount, confirmation_token, status='pending'):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO payments (transaction_id, whatsapp_number, amount, confirmation_token, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (transaction_id, whatsapp_number, amount, confirmation_token, status))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_payment_by_transaction(transaction_id):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute('''
        SELECT whatsapp_number, amount, status, confirmation_token, user_name, paid_at
        FROM payments 
        WHERE transaction_id = ?
    ''', (transaction_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'whatsapp_number': row[0],
            'amount': row[1],
            'status': row[2],
            'confirmation_token': row[3],
            'user_name': row[4],
            'paid_at': row[5]
        }
    return None

def update_payment_status(transaction_id, status, payment_method=None):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    
    if status == 'completed':
        c.execute('''
            UPDATE payments 
            SET status = ?, paid_at = CURRENT_TIMESTAMP, payment_method = ?
            WHERE transaction_id = ?
        ''', (status, payment_method, transaction_id))
    else:
        c.execute('''
            UPDATE payments 
            SET status = ?, payment_method = ?
            WHERE transaction_id = ?
        ''', (status, payment_method, transaction_id))
    
    conn.commit()
    conn.close()

def update_user_name(transaction_id, user_name):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute('''
        UPDATE payments 
        SET user_name = ?, confirmed_at = CURRENT_TIMESTAMP
        WHERE transaction_id = ?
    ''', (user_name, transaction_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute('''
        SELECT user_name, whatsapp_number, amount, paid_at, payment_method, status
        FROM payments 
        WHERE status = 'completed' 
        ORDER BY paid_at DESC
    ''')
    users = c.fetchall()
    conn.close()
    return users

def get_paid_users():
    """Get only users who have confirmed their token"""
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute('''
        SELECT user_name, whatsapp_number, amount, paid_at, payment_method
        FROM payments 
        WHERE status = 'completed' AND user_name IS NOT NULL
        ORDER BY paid_at DESC
    ''')
    users = c.fetchall()
    conn.close()
    return users

def add_invitation(whatsapp_number, invitation_link):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR REPLACE INTO invitations (whatsapp_number, invitation_link)
            VALUES (?, ?)
        ''', (whatsapp_number, invitation_link))
        conn.commit()
        return True
    finally:
        conn.close()