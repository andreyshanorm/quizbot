import aiosqlite

DB_NAME = 'quiz_bot.db'
async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(''' 
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER
            )
        ''')

        await db.execute(''' 
            CREATE TABLE IF NOT EXISTS quiz_results ( 
                user_id INTEGER,
                question_index INTEGER,
                is_correct INTEGER
            )
        ''')

        await db.execute(''' 
            CREATE TABLE IF NOT EXISTS quiz_ratings ( 
                user_id INTEGER,
                user_name VARCHAR,
                best_score INTEGER DEFAULT 0
            )
        ''')

        await db.commit()

async def get_top_rating():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_name, best_score FROM quiz_ratings ORDER BY best_score DESC LIMIT 10',()) as cursor:
            result = await cursor.fetchall()
            return result if result else 0

async def create_user_name(user_id, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO quiz_ratings (user_id, user_name) VALUES (?, ?)
        ''', (user_id, value))
        await db.commit()

async def update_best_score(user_id, score_value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE quiz_ratings 
            SET best_score = ?
            WHERE user_id = ?
        """, (score_value, user_id))
        await db.commit()

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(''' 
            INSERT OR REPLACE INTO quiz_state (user_id, question_index) 
            VALUES (?, ?)
        ''', (user_id, index))
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def save_user_result(user_id, question_index, correct):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(''' 
            INSERT INTO quiz_results (user_id, question_index, is_correct) 
            VALUES (?, ?, ?)
        ''', (user_id, question_index, 1 if correct else 0))
        await db.commit()

async def show_user_statistics(user_id, message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(''' 
            SELECT COUNT(*), COALESCE(SUM(is_correct), 0) 
            FROM quiz_results 
            WHERE user_id = ? 
        ''', (user_id,)) as cursor:
            total_questions, correct_answers = await cursor.fetchone()
        if total_questions != 0:
            await update_best_score(user_id, correct_answers)
        return total_questions, correct_answers

async def start_new_quiz(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM quiz_results WHERE user_id = ?', (user_id,))
        await db.commit()