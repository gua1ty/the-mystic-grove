import sqlite3


def new_user(p_username, p_email, p_password, p_role):

    query = "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)"

    conn = sqlite3.connect("guild.db")
    cursor = conn.cursor()

    cursor.execute(query, (p_username, p_email, p_password, p_role))

    conn.commit()
    cursor.close()
    conn.close()
        


def get_user_by_id(p_id):
    query = "SELECT * FROM users WHERE id = ?"

    conn = sqlite3.connect("guild.db")
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

    conn = sqlite3.connect("guild.db")
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
    
    conn = sqlite3.connect("guild.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

