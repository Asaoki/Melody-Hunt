import sqlite3 
import os 

DB_PATH ="scores.db"

def init_database ():
    """Инициализирует базу данных и создает таблицу, если она не существует"""
    conn =sqlite3 .connect (DB_PATH )
    cursor =conn .cursor ()


    cursor .execute ("SELECT name FROM sqlite_master WHERE type='table' AND name='scores'")
    table_exists =cursor .fetchone ()

    if table_exists :

        cursor .execute ("PRAGMA table_info(scores)")
        columns =[column [1 ]for column in cursor .fetchall ()]

        if 'total_score'not in columns :

            cursor .execute ('ALTER TABLE scores RENAME TO scores_old')
            cursor .execute ('''
                CREATE TABLE scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    easy_score INTEGER NOT NULL DEFAULT 0,
                    medium_score INTEGER NOT NULL DEFAULT 0,
                    hard_score INTEGER NOT NULL DEFAULT 0
                )
            ''')

            cursor .execute ('''
                INSERT INTO scores (id, name, total_score, easy_score, medium_score, hard_score)
                SELECT id, name, score, 0, 0, 0 FROM scores_old
            ''')
            cursor .execute ('DROP TABLE scores_old')
        else :

            pass 
    else :

        cursor .execute ('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                total_score INTEGER NOT NULL DEFAULT 0,
                easy_score INTEGER NOT NULL DEFAULT 0,
                medium_score INTEGER NOT NULL DEFAULT 0,
                hard_score INTEGER NOT NULL DEFAULT 0
            )
        ''')

    conn .commit ()
    conn .close ()

def get_user (name ):
    """Получает пользователя по имени. Возвращает кортеж (name, total_score, easy_score, medium_score, hard_score) или None"""
    conn =sqlite3 .connect (DB_PATH )
    cursor =conn .cursor ()

    cursor .execute ('SELECT name, total_score, easy_score, medium_score, hard_score FROM scores WHERE name = ?',(name ,))
    result =cursor .fetchone ()

    conn .close ()
    return result 

def create_user (name ):
    """Создает нового пользователя с именем и начальными счетами 0. Возвращает True при успехе"""
    try :
        conn =sqlite3 .connect (DB_PATH )
        cursor =conn .cursor ()

        cursor .execute ('INSERT INTO scores (name, total_score, easy_score, medium_score, hard_score) VALUES (?, ?, ?, ?, ?)',
        (name ,0 ,0 ,0 ,0 ))

        conn .commit ()
        conn .close ()
        return True 
    except sqlite3 .IntegrityError :

        conn .close ()
        return False 

def get_or_create_user (name ):
    """Получает пользователя или создает нового. Возвращает кортеж (name, score)"""
    user =get_user (name )
    if user :
        return user 
    else :
        create_user (name )
        return get_user (name )

def update_score (name ,difficulty ,new_score ):
    """Обновляет счет пользователя для определенного уровня сложности и общий счет
    difficulty - уровень сложности: "easy", "medium", "hard"
    new_score - новое количество очков для данного уровня
    """
    conn =sqlite3 .connect (DB_PATH )
    cursor =conn .cursor ()


    score_field =f"{difficulty}_score"


    cursor .execute (f'UPDATE scores SET {score_field} = ? WHERE name = ?',(new_score ,name ))


    cursor .execute ('SELECT easy_score, medium_score, hard_score FROM scores WHERE name = ?',(name ,))
    result =cursor .fetchone ()
    if result :
        easy ,medium ,hard =result 
        total_score =easy +medium +hard 
        cursor .execute ('UPDATE scores SET total_score = ? WHERE name = ?',(total_score ,name ))

    conn .commit ()
    conn .close ()

def update_score_legacy (name ,new_score ):
    """Старая функция для обратной совместимости - обновляет только общий счет"""
    conn =sqlite3 .connect (DB_PATH )
    cursor =conn .cursor ()

    cursor .execute ('UPDATE scores SET total_score = ? WHERE name = ?',(new_score ,name ))

    conn .commit ()
    conn .close ()

def update_best_score (name ,difficulty ,new_score ):
    """Обновляет счет пользователя только если новый счет лучше текущего лучшего
    difficulty - уровень сложности: "easy", "medium", "hard"
    new_score - новое количество очков для данного уровня
    Возвращает True, если счет был обновлен, False если новый счет хуже
    """
    conn =sqlite3 .connect (DB_PATH )
    cursor =conn .cursor ()


    score_field =f"{difficulty}_score"
    cursor .execute (f'SELECT {score_field} FROM scores WHERE name = ?',(name ,))
    result =cursor .fetchone ()

    if result :
        current_best_score =result [0 ]

        if new_score >current_best_score :
            cursor .execute (f'UPDATE scores SET {score_field} = ? WHERE name = ?',(new_score ,name ))


            cursor .execute ('SELECT easy_score, medium_score, hard_score FROM scores WHERE name = ?',(name ,))
            result =cursor .fetchone ()
            if result :
                easy ,medium ,hard =result 
                total_score =easy +medium +hard 
                cursor .execute ('UPDATE scores SET total_score = ? WHERE name = ?',(total_score ,name ))

            conn .commit ()
            conn .close ()
            return True 
        else :
            conn .close ()
            return False 
    else :
        conn .close ()
        return False 

def get_top_scores (limit =10 ):
    """Получает топ игроков по общему счету. Возвращает список кортежей (name, total_score, easy_score, medium_score, hard_score)"""
    conn =sqlite3 .connect (DB_PATH )
    cursor =conn .cursor ()

    cursor .execute ('SELECT name, total_score, easy_score, medium_score, hard_score FROM scores ORDER BY total_score DESC LIMIT ?',(limit ,))
    results =cursor .fetchall ()

    conn .close ()
    return results 
