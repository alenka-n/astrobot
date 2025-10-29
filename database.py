import sqlite3
from datetime import datetime

def init_database():
    """Инициализация базы данных"""
    conn = sqlite3.connect('astrobot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            birth_date TEXT,
            zodiac_sign TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def get_zodiac_sign(day, month):
    """Определение знака зодиака по дате рождения"""
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return 'овен'
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return 'телец'
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return 'близнецы'
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return 'рак'
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return 'лев'
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return 'дева'
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return 'весы'
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return 'скорпион'
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return 'стрелец'
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return 'козерог'
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return 'водолей'
    else:
        return 'рыбы'

def save_user_data(user_id, username, birth_date, zodiac_sign):
    """Сохранение данных пользователя в БД"""
    conn = sqlite3.connect('astrobot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, birth_date, zodiac_sign, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, birth_date, zodiac_sign, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_user_data(user_id):
    """Получение данных пользователя из БД"""
    conn = sqlite3.connect('astrobot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'user_id': result[0],
            'username': result[1],
            'birth_date': result[2],
            'zodiac_sign': result[3],
            'created_at': result[4]
        }
    return None