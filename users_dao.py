import sqlite3

import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guild.db")

def new_user(p_username, p_email, p_password, p_role):

    query = "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(query, (p_username, p_email, p_password, p_role))

    conn.commit()
    cursor.close()
    conn.close()
        


def get_user_by_id(p_id):
    query = "SELECT * FROM users WHERE id = ?"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id,))

    db_user = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return db_user


def get_user_by_email(p_email):
    query = "SELECT * FROM users WHERE email = ?"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_email,))

    db_user = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return db_user


def get_all_adventurers():

    query = "SELECT * FROM users WHERE role = 'adventurer'"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    db_users = cursor.fetchall()

    cursor.close()
    conn.close()
    return db_users

