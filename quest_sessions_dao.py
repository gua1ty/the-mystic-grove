import sqlite3

import enrollments_dao   
import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guild.db")


def new_session(p_quest_id, p_day, p_start_time, p_location):
    query = "INSERT INTO quest_sessions (quest_id, day, start_time, location) VALUES (?, ?, ?, ?)"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_quest_id, p_day, p_start_time, p_location))
    conn.commit()
    cursor.close()
    conn.close()


        
def get_all_sessions():
    query = """
        SELECT qs.*, q.title, q.description, q.duration_min, q.quest_type, q.difficulty, q.quest_img
        FROM quest_sessions qs
        JOIN quests q ON qs.quest_id = q.id
        ORDER BY 
            CASE qs.day
                WHEN 'monday' THEN 1
                WHEN 'tuesday' THEN 2
                WHEN 'wednesday' THEN 3
                WHEN 'thursday' THEN 4
                WHEN 'friday' THEN 5
                WHEN 'saturday' THEN 6
                WHEN 'sunday' THEN 7
            END,
            qs.start_time
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sessions



def get_sessions_by_id(p_id):
    
    query_session = """
        SELECT qs.*, q.title, q.description, q.duration_min, q.quest_type, q.difficulty, q.quest_img
        FROM quest_sessions qs
        JOIN quests q ON qs.quest_id = q.id
        WHERE qs.id = ?  
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query_session, (p_id,))
    db_session = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not db_session:
        return None
    
    session_data = dict(db_session)
    session_data["places"] = enrollments_dao.get_places_taken(p_id)

    return session_data


def get_sessions_by_quest_id(p_quest_id):
    query = """
        SELECT * FROM quest_sessions 
        WHERE quest_id = ?
        ORDER BY 
            CASE day
                WHEN 'monday' THEN 1
                WHEN 'tuesday' THEN 2
                WHEN 'wednesday' THEN 3
                WHEN 'thursday' THEN 4
                WHEN 'friday' THEN 5
                WHEN 'saturday' THEN 6
                WHEN 'sunday' THEN 7
            END,
            start_time
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_quest_id,))
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sessions


def get_sessions_by_location(p_location):
    query = "SELECT * FROM quest_sessions WHERE location = ?"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_location,))
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sessions


def update_session(p_id, p_day, p_start_time, p_location):
    query = "UPDATE quest_sessions SET day = ?, start_time = ?, location = ? WHERE id = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_day, p_start_time, p_location, p_id))
    conn.commit()
    cursor.close()
    conn.close()


def delete_session(p_id):
    query = "DELETE FROM quest_sessions WHERE id = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_id,))
    conn.commit()
    cursor.close()
    conn.close()


