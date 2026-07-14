import sqlite3

import sqlite3


def new_quest(p_title, p_duration_min, p_quest_type, p_difficulty, p_description, p_quest_img):
    query = """
        INSERT INTO quests (title, duration_min, quest_type, difficulty, description, quest_img)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    conn = sqlite3.connect("guild.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_title, p_duration_min, p_quest_type, p_difficulty, p_description, p_quest_img))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def get_all_quests():
    query = "SELECT * FROM quests"
    conn = sqlite3.connect("guild.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    quests = cursor.fetchall()
    cursor.close()
    conn.close()
    return quests

def get_most_popular_quest_type():
    query = """
        SELECT q.quest_type, SUM(e.places) as total_enrollments
        FROM quests q
        JOIN quest_sessions qs ON q.id = qs.quest_id
        JOIN enrollments e ON qs.id = e.session_id
        GROUP BY q.quest_type
        ORDER BY total_enrollments DESC
        LIMIT 1
    """
    conn = sqlite3.connect("guild.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_quest_by_id(p_id):
    query = "SELECT * FROM quests WHERE id = ?"
    conn = sqlite3.connect("guild.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_id,))
    quest = cursor.fetchone()
    cursor.close()
    conn.close()
    return quest