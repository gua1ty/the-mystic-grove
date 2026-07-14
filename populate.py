import sqlite3
from werkzeug.security import generate_password_hash

def populate_db():
    conn = sqlite3.connect('guild.db')
    cursor = conn.cursor()

    # 1. WIPE EXISTING DATA
    cursor.execute('DELETE FROM enrollments')
    cursor.execute('DELETE FROM quest_sessions')
    cursor.execute('DELETE FROM quests')
    cursor.execute('DELETE FROM users')
    
    # Resettiamo l'autoincremento per tutte le tabelle
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('enrollments', 'quest_sessions', 'quests', 'users')")
    except sqlite3.OperationalError:
        pass

    # 2. USERS (Guild Master + Players)
    # Generiamo le password criptate per poter fare il login correttamente
    users_data = [
        # ID 1: Il Guild Master (non registrabile dal sito)
        ('GuildMaster', 'master@guild.com', generate_password_hash('master123'), 'guild_master'),

        
        # ID 2, 3, 4, 5: I giocatori necessari per la tabella enrollments
        ('Zephyr', 'zephyr@windsong.com', generate_password_hash('password'), 'adventurer'), 
        ('Lyra', 'lyra@moonglow.com', generate_password_hash('password'), 'adventurer'), 
        ('Sylas', 'sylas@deepwoods.com', generate_password_hash('password'), 'adventurer'), 
        ('Cami', 'cami@burri.com', generate_password_hash('password'), 'adventurer'),
        
        ('GuildCouncil', 'council@guild.com', generate_password_hash('council123'), 'guild_council'),
     
    ]
    cursor.executemany('''
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    ''', users_data)

    # 3. QUESTS (6 missions)
    quests_data = [
        ('Echo of the Ancient Woods', 90, 'exploration', 'easy', 
         'A strange melody echoes through the ancient trees. Explore the forgotten paths to find the source of this magic before it fades.', 'images/quest_imgs/echo_woods.jpg'),
         
        ('Awakening of the Goblin King', 120, 'combat', 'medium', 
         'The mines have been invaded. Prepare your weapons and delve into the darkness to defeat the Goblin King and free the prisoners.', 'images/quest_imgs/goblin_king.jpg'),
         
        ('Blizzard on Crystal Peak', 180, 'survival', 'hard', 
         'An unnatural storm has blocked the mountain pass. Survive the deadly frost and find shelter before the ice wolves catch your scent.', 'images/quest_imgs/crystal_peak.jpg'),
         
        ('Secret of the Sunken Temple', 60, 'puzzle', 'medium', 
         'The waters have receded, revealing an ancient temple. Solve the stone puzzles to unlock the sanctuary before the tide rises again.', 'images/quest_imgs/sunken_temple.jpg'),
         
        ('Theft of the Ash Eye', 45, 'stealth', 'hard', 
         'A priceless ruby is guarded in the lava fortress. Infiltrate without being detected by the fire guards and steal the gem.', 'images/quest_imgs/ash_eye.jpg'),
         
        ('The Archmage\'s Curse', 60, 'magic', 'legendary', 
         'A spell went wrong and the library floats in chaos. Stop the mana storm before the entire guild is destroyed.', 'images/quest_imgs/archmage_curse.jpg')
    ]
    
    cursor.executemany('''
        INSERT INTO quests (title, duration_min, quest_type, difficulty, description, quest_img)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', quests_data)

    # 4. SESSIONS (2 per day)
    sessions_data = [
        (1, 'monday',    '10:00', 'Dungeon Hall'),
        (2, 'monday',    '15:00', 'Enchanted Forest'),
        (3, 'tuesday',   '09:00', 'Wizard Tower'),
        (4, 'tuesday',   '16:00', 'Dungeon Hall'),
        (5, 'wednesday', '11:00', 'Enchanted Forest'),
        (6, 'wednesday', '18:00', 'Wizard Tower'),
        (1, 'thursday',  '14:00', 'Dungeon Hall'),
        (2, 'thursday',  '20:00', 'Enchanted Forest'),
        (3, 'friday',    '10:00', 'Wizard Tower'),
        (4, 'friday',    '17:00', 'Dungeon Hall'),
        (5, 'saturday',  '15:00', 'Enchanted Forest'),
        (6, 'saturday',  '21:00', 'Wizard Tower'),
        (1, 'sunday',    '08:00', 'Dungeon Hall'),
        (5, 'sunday',    '17:00', 'Wizard Tower')
    ]
    cursor.executemany('''
        INSERT INTO quest_sessions (quest_id, day, start_time, location)
        VALUES (?, ?, ?, ?)
    ''', sessions_data)

    # 5. ENROLLMENTS
    enrollments_data = [
        # Warrior completely full in session 1 (4/4)
        (2, 1, 'warrior', 2),  # aragorn (ID 2)
        (3, 1, 'warrior', 2),  # gandalf (ID 3)
        # Mage in session 2
        (4, 2, 'mage', 1),     # legolas (ID 4)
        # Healer in session 3
        (5, 3, 'healer', 1),   # gimli (ID 5)
    ]
    cursor.executemany('''
        INSERT INTO enrollments (user_id, session_id, class, places)
        VALUES (?, ?, ?, ?)
    ''', enrollments_data)

    conn.commit()
    conn.close()
    print("Database successfully cleared and repopulated with Guild Master!")

if __name__ == '__main__':
    populate_db()