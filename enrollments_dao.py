import sqlite3

import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guild.db")



def new_enrollment (p_user_id, p_session_id, p_class, p_places):

    query = "INSERT INTO enrollments (user_id, session_id, class, places) VALUES (?, ?, ?, ?)"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(query, (p_user_id, p_session_id, p_class, p_places))

    conn.commit()
    cursor.close()
    conn.close()


def get_enrollments_by_user(p_user_id):
    query = """
            SELECT e.*, s.day, s.start_time, s.location, 
                q.title, q.description, q.duration_min, q.quest_type, q.difficulty, q.quest_img
            FROM enrollments e 
            JOIN quest_sessions s ON e.session_id = s.id
            JOIN quests q ON s.quest_id = q.id
            WHERE e.user_id = ?
            ORDER BY 
                CASE s.day
                    WHEN 'monday' THEN 1
                    WHEN 'tuesday' THEN 2
                    WHEN 'wednesday' THEN 3
                    WHEN 'thursday' THEN 4
                    WHEN 'friday' THEN 5
                    WHEN 'saturday' THEN 6
                    WHEN 'sunday' THEN 7
                END,
                s.start_time
            """
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_user_id,))
    enrollments = cursor.fetchall()
    cursor.close()
    conn.close()
    return enrollments

def get_enrollment_for_user_session(p_user_id, p_session_id):
    query = """
        SELECT * FROM enrollments
        WHERE user_id = ? AND session_id = ?
        """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_user_id, p_session_id))
    enrollment = cursor.fetchone()
    cursor.close()
    conn.close()
    return enrollment

def get_places_taken(p_session_id):
    query = """
        SELECT class, SUM(places) as places
        FROM enrollments
        WHERE session_id = ?
        GROUP BY class
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_session_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    places = {"warrior": 0, "mage": 0, "healer": 0}
    for r in rows:
        places[r["class"]] = r["places"]
    return places


def get_enrollment_by_id(p_id):
    query = "SELECT * FROM enrollments WHERE id = ?"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_id,))
    enrollment = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return enrollment

def get_all_enrollments():
    query = "SELECT * FROM enrollments"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    enrollments = cursor.fetchall()
    cursor.close()
    conn.close()
    return enrollments

def update_enrollment(p_id, p_class, p_places):
    query = "UPDATE enrollments SET class = ?, places = ? WHERE id = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_class, p_places, p_id))
    conn.commit()
    cursor.close()
    conn.close()


def delete_enrollment(p_id):
    query = "DELETE FROM enrollments WHERE id = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_id,))
    conn.commit()
    cursor.close()
    conn.close()






