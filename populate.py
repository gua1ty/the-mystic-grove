import sqlite3
from werkzeug.security import generate_password_hash

def populate_db():
    conn = sqlite3.connect('guild.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM enrollments')
    cursor.execute('DELETE FROM quest_sessions')
    cursor.execute('DELETE FROM quests')
    cursor.execute('DELETE FROM users')
    
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('enrollments', 'quest_sessions', 'quests', 'users')")
    except sqlite3.OperationalError:
        pass

    
    users_data = [
        ('GuildMaster', 'master@guild.com', generate_password_hash('master123'), 'guild_master'),

        
        ('Zephyr', 'zephyr@windsong.com', generate_password_hash('password'), 'adventurer'), 
        ('Lyra', 'lyra@moonglow.com', generate_password_hash('password'), 'adventurer'), 
        ('Sylas', 'sylas@deepwoods.com', generate_password_hash('password'), 'adventurer'), 
        ('Willow', 'willow@sunlitgrove.net', generate_password_hash('password'), 'adventurer'),        
        
        ('GuildCouncil', 'council@guild.com', generate_password_hash('council123'), 'guild_council'),
     
    ]
    cursor.executemany('''
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    ''', users_data)

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

    sessions_data = [
    (1, 'monday',    '10:00', 'Whispering Hollow'),
    (2, 'monday',    '15:00', 'Moonlit Wood'),
    (3, 'tuesday',   '09:00', 'Mystic Tower'),
    (4, 'tuesday',   '16:00', 'Whispering Hollow'),
    (5, 'wednesday', '11:00', 'Moonlit Wood'),
    (6, 'wednesday', '18:00', 'Mystic Tower'),
    (1, 'thursday',  '14:00', 'Whispering Hollow'),
    (2, 'thursday',  '20:00', 'Moonlit Wood'),
    (3, 'friday',    '10:00', 'Mystic Tower'),
    (4, 'friday',    '17:00', 'Whispering Hollow'),
    (5, 'saturday',  '15:00', 'Moonlit Wood'),
    (6, 'saturday',  '21:00', 'Mystic Tower'),
    (1, 'sunday',    '08:00', 'Whispering Hollow'),
    (5, 'sunday',    '17:00', 'Mystic Tower')
]

    cursor.executemany('''
        INSERT INTO quest_sessions (quest_id, day, start_time, location)
        VALUES (?, ?, ?, ?)
    ''', sessions_data)

    enrollments_data = [

    (4, 2, 'warrior', 2),   

    (2, 6, 'mage', 2),      
    (3, 6, 'mage', 1),           
    (2, 4, 'healer', 1),     
    (5, 7, 'healer', 1),      
    ]
    cursor.executemany('''
        INSERT INTO enrollments (user_id, session_id, class, places)
        VALUES (?, ?, ?, ?)
    ''', enrollments_data)

    conn.commit()
    conn.close()
    print("Database successfully cleared and repopulated")

if __name__ == '__main__':
    populate_db()