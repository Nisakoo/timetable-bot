import os

from dotenv import load_dotenv

from app.db.sqlite_db import SqliteDataBase
from app.bot.telegram_bot import TelegramBot


def main():
    load_dotenv()

    db = SqliteDataBase(os.getenv("DB_URL"))
    bot = TelegramBot(os.getenv("BOT_TOKEN"), db, int(os.getenv("ADMIN_ID")))
    bot.run()


if __name__ == "__main__":
    main()