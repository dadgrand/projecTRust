import asyncio
import aiosqlite
from config import DATABASE_PATH

async def create_table(db_path: str) -> None:
    """Создаёт таблицы user_info и user_messages, если не существует."""

    create_info_query = """
    CREATE TABLE IF NOT EXISTS user_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    preferred_name TEXT NULL,
    assistance_preference TEXT NULL,
    age TEXT NULL,
    gender TEXT NULL,
    weight TEXT NULL,
    height TEXT NULL,
    favorite_sports TEXT NULL,
    sports_activity TEXT NULL,
    weekly_sport_hours TEXT NULL,
    injuries TEXT NULL,
    dietary_preferences TEXT NULL,
    wakeup_time TEXT NULL,
    sleep_time TEXT NULL,
    sleep_quality TEXT NULL,
    schedule TEXT NULL,
    desired_income TEXT NULL,
    improvement_areas TEXT NULL,
    motivation TEXT NULL,
    best_quality TEXT NULL,
    worst_quality TEXT NULL,
    shopping_preference TEXT NULL,
    spending_habits TEXT NULL,
    time_management_skill TEXT NULL,
    procrastination_level TEXT NULL,
    daily_social_media_time TEXT NULL,
    daily_screen_time TEXT NULL,
    reduce_phone_time TEXT NULL,
    hobbies_interests TEXT NULL,
    learning_preference TEXT NULL,
    weekly_desired_activities TEXT NULL,
    stress_management TEXT NULL,
    family_friends_time TEXT NULL,
    increase_social_time TEXT NULL,
    communication_frequency TEXT NULL,
    increase_known_people_communication TEXT NULL,
    increase_unknown_people_communication TEXT NULL,
    breathing_techniques TEXT NULL,
    belief_system TEXT NULL,
    receive_motivational_notifications TEXT NULL,
    self_improvement_commitment TEXT NULL,
    schedule_detailedness TEXT NULL,
    communication_style TEXT NULL,
    nightly_survey_participation TEXT NULL,
    progress_reports TEXT NULL,
    live_session_participation TEXT NULL,
    journaling_interest TEXT NULL,
    responsibility TEXT NULL,
    self_improvement_desire TEXT NULL
);
    """

    create_message_query = """
    create table if not exists user_messages (
    id integer PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    schedule text null,
    conversation text null
    )
    """

    create_schedule_query = """
    CREATE TABLE IF NOT EXISTS user_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Уникальный идентификатор задачи
    user_id INTEGER NOT NULL,                  -- Ссылка на пользователя (user_id)
    task_description TEXT,                     -- Описание задачи
    start_time TIME,                           -- Время начала задачи (например, '14:30')
    end_time TIME,                             -- Время окончания задачи (например, '15:30')
    date DATE,                                 -- Дата создания задачи
    reminder_sent BOOLEAN DEFAULT FALSE,       -- Флаг отправленного напоминания
    FOREIGN KEY(user_id) REFERENCES user_info(user_id) ON DELETE CASCADE -- Связь с таблицей users
    )
    
    """

    async with aiosqlite.connect(db_path) as db:
        await db.execute(create_info_query)
        await db.commit()
        await db.execute(create_message_query)
        await db.commit()
        await db.execute(create_schedule_query)
        await db.commit()


async def check_tables(db_path):
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            tables = await cursor.fetchall()
            print("Tables in the database:", tables)


def main():
    asyncio.run(create_table(DATABASE_PATH))

if __name__ == '__main__':
    asyncio.run(check_tables('/Users/pabgrand/Documents/туда сюда/projecTRust/database/users.db'))
    #asyncio.run(create_table(DATABASE_PATH))
    #main()


"""
if __name__ == '__main__':
    main()"""