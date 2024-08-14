import asyncio
import sys

import aiosqlite
from config import DATABASE_PATH
from utils.chatgpt_api import get_chatgpt_response, return_prompt

async def create_schedule(db_path: str, user_id: int, user_text: str) -> None:
    """Создаёт расписание на день для пользователя на основании его предпочтений и пожеланий на день (user_text)."""

    schedule_text = get_chatgpt_response(return_prompt('create_schedule', user_text))

    return schedule_text

async def create_user(db_path: str, user_id: int) -> None:
    """Создаёт нового пользователя с user_id."""

    insert_user_query = """
    INSERT INTO user_info (user_id) VALUES (?);
    """

    async with aiosqlite.connect(db_path) as db:
        await db.execute(insert_user_query, (user_id,))
        await db.commit()

async def fill_user(db_path: str, user_id: int, **user_data) -> None:
    """Заполняет оставшиеся колонки пользователя на основе user_id."""

    # Create the SET clause of the SQL statement dynamically
    set_clause = ", ".join([f"{key} = ?" for key in user_data.keys()])
    update_user_query = f"""
    UPDATE user_info SET {set_clause} WHERE user_id = ?;
    """

    async with aiosqlite.connect(db_path) as db:
        await db.execute(update_user_query, list(user_data.values()) + [user_id])
        await db.commit()

async def delete_user(db_path: str, user_id: int) -> None:
    """Удаляет пользователя по его user_id."""

    delete_user_query = """
    DELETE FROM user_info WHERE user_id = ?
    """

    async with aiosqlite.connect(db_path) as db:
        await db.execute(delete_user_query, (user_id, ))
        await db.commit()


async def get_user_params(db_path: str, user_id: int) -> str:
    """Выводит информацию о пользователе в виде строки по user_id."""

    select_query = """
    SELECT * FROM user_info WHERE user_id = ?;
    """

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(select_query, (user_id,)) as cursor:
            row = await cursor.fetchone()

            column_names = [description[0] for description in cursor.description]
            user_info = "\n".join(f"{column}: {value}" for column, value in zip(column_names, row))

            return user_info

async def get_all_users(db_path: str) -> list:
    """Выводит список всех user_id."""

    select_query = """
    SELECT user_id FROM user_info;
    """

    user_ids = []

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(select_query) as cursor:
            rows = await cursor.fetchall()

            for row in rows:
                user_ids.append(row[0])

    return user_ids



async def main():
    print(await get_user_params(DATABASE_PATH, 831653918))

if __name__ == '__main__':
    asyncio.run(main())