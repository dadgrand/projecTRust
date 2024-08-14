import asyncio
from telethon import TelegramClient, events, Button, Button
from config import *  # Ensure this is correctly set up with your API keys and tokens
from utils.chatgpt_api import get_chatgpt_response, return_prompt
from database.database_functions import *
from utils.prompts import questions, column_names
import os


# Create a new Telegram client
client = TelegramClient('bot_session', API, API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN)

# Dictionary to track user interaction states
user_states = {}

# Define constants for user states
STATE_ACTIVE = 'active'
STATE_INACTIVE = 'inactive'

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    welcome_message = "Приветствую! С моей помощью Вы сможете составить эффективное расписание на день и сделать свою жизнь лучше."
    photo_path = 'utils/welcome.jpg'  # Replace with your photo path

    await client.send_file(event.chat_id, photo_path, caption=welcome_message)

    user_id = event.sender_id

    # Ensure async function is awaited
    all_users = await get_all_users(DATABASE_PATH)

    if user_id not in all_users:
        newbie_message = """
        Ой! Похоже, вы с нами впервые. Хотите заполнить анкету о себе для лучшего опыта использования бота?
        
        Предупреждаем: заполнение анкеты требует времени!
        """

        # Create inline buttons with callback data
        buttons = [
            [Button.inline('Да, заполнить анкету!', b'fill_survey')],
            [Button.inline('Нет, не нужно', b'do_not_fill')]
        ]

        # Send message with inline keyboard
        await client.send_message(user_id, newbie_message, buttons=buttons)
        await create_user(DATABASE_PATH, user_id)

    else:
        await main_menu(event)

    # Set the initial state to active for the new user
    user_states[user_id] = STATE_ACTIVE

from utils.prompts import questions

@client.on(events.CallbackQuery)
async def callback_handler(event):
    # Get the callback data
    data = event.data

    user_id = event.sender_id

    if data == b'fill_survey':
        await event.answer('Вы выбрали заполнить анкету.')
        user_states[user_id] = STATE_INACTIVE
        user_responses = {}
        current_question = 0
        question_message = None

        async def ask_question():
            nonlocal current_question, question_message
            if current_question < len(questions):
                question_text = f"Вопрос {current_question + 1}/{len(questions)}:\n{questions[current_question]}"
                if question_message:
                    await question_message.edit(question_text)
                else:
                    question_message = await client.send_message(user_id, question_text)
                current_question += 1
            else:
                await finish_survey()

        async def finish_survey():
            nonlocal question_message
            await fill_user(DATABASE_PATH, user_id, **user_responses)
            if question_message:
                await question_message.edit("Спасибо за заполнение анкеты!")
            else:
                await client.send_message(user_id, "Спасибо за заполнение анкеты!")
            user_states[user_id] = STATE_ACTIVE
            await main_menu(event)

        @client.on(events.NewMessage(from_users=user_id))
        async def handle_response(event):
            nonlocal current_question
            if user_states[user_id] == STATE_INACTIVE:
                if current_question <= len(column_names):
                    user_responses[column_names[current_question - 1]] = event.message.text
                    await event.message.delete()
                    await ask_question()
                else:
                    await finish_survey()

        await ask_question()

    if data == b'do_not_fill':
        await event.answer('Вы выбрали не заполнять анкету.')
        user_states[user_id] = STATE_ACTIVE

        await main_menu(event)

    if data == b'schedule':
        buttons = [
            [Button.inline('Составить расписание', b'create_schedule')],
            [Button.inline('Просмотреть своё расписание', b'show_schedule')]
        ]
        await client.send_message(user_id, "test" ,buttons=buttons)

    if data == b'create_schedule':
        user_states[user_id] = STATE_INACTIVE

        user_id = event.sender_id

        await client.send_message(user_id, "test schedule")

        @client.on(events.NewMessage(from_users=user_id))
        async def handle_response(response_event):
            user_text = response_event.message.message

            schedule_text = create_schedule(DATABASE_PATH, user_text)

            await client.send_message(user_id, schedule_text)

            client.remove_event_handler(handle_response)


    print(f"User {user_id} state: {user_states[user_id]}")

async def main_menu(event):
    buttons = [
        [Button.inline('Расписание', b'schedule')],
        [Button.inline('Анкета', b'questionnaire')],
    ]
    await client.send_message(event.chat_id, "🔮", buttons=buttons)

@client.on(events.NewMessage(pattern=r'(?!/start).*'))
async def message_handler(event):
    user_id = event.sender_id

    # Check if the user's state is inactive; if so, ignore the message
    if user_states.get(user_id) == STATE_INACTIVE:
        print(f"Ignoring message from user {user_id} because they are inactive.")
        return

    user_message = event.message.text
    response = get_chatgpt_response(return_prompt('default', user_message))
    await event.reply(response)

def main():
    print('Bot is running...')
    client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())