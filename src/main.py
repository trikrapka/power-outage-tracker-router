import logging
from telegram.ext import Application, CommandHandler
from config import TG_BOT_TOKEN, MONITORING_INTERVAL
from user_manager import UserManager
from bot_handlers import start, set_url, set_ip, list_urls, list_ips, delete_url, delete_ip
from monitoring import monitor_power
from database import Session, init_db

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def main() -> None:
    try:
        init_db()

        session = Session()
        user_manager = UserManager(session)

        application = Application.builder().token(TG_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", lambda update, context: start(update, context, user_manager)))
        application.add_handler(CommandHandler("set_url", lambda update, context: set_url(update, context, user_manager)))
        application.add_handler(CommandHandler("set_ip", lambda update, context: set_ip(update, context, user_manager)))
        application.add_handler(CommandHandler("list_urls", lambda update, context: list_urls(update, context, user_manager)))
        application.add_handler(CommandHandler("list_ips", lambda update, context: list_ips(update, context, user_manager)))
        application.add_handler(CommandHandler("delete_url", lambda update, context: delete_url(update, context, user_manager)))
        application.add_handler(CommandHandler("delete_ip", lambda update, context: delete_ip(update, context, user_manager)))

        job_queue = application.job_queue
        job_queue.run_repeating(lambda context: monitor_power(context, user_manager), interval=MONITORING_INTERVAL, first=10)

        application.run_polling()
    except Exception as e:
        logging.error(f"Unhandled exception in main function: {e}", exc_info=True)


if __name__ == '__main__':
    main()