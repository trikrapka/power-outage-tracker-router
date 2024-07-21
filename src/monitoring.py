import subprocess
from datetime import datetime, timedelta
import requests
from telegram.ext import ContextTypes
from user_manager import UserManager
from config import PING_TIMEOUT, REQUEST_TIMEOUT
from database import Session, User


def check_connection(identifier: str, identifier_type: str) -> bool:
    if identifier_type == 'ips':
        try:
            subprocess.check_output(['ping', '-c', '1', identifier], stderr=subprocess.STDOUT, timeout=PING_TIMEOUT)
            return True
        except   (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    else:
        try:
            response = requests.get(identifier, timeout=REQUEST_TIMEOUT)
            return response.status_code == 200
        except requests.RequestException:
            return False


def format_timedelta(td: timedelta) -> str:
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds"


async def monitor_power(context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    current_time = datetime.now()
    session = Session()
    try:
        users = session.query(User).all()
        for user in users:
            chat_id = user.chat_id
            for identifier_type in ['urls', 'ips']:
                identifiers = user_manager.get_identifiers(chat_id, identifier_type)
                for identifier in identifiers:
                    power_outage_start = user_manager.get_power_outage_start(chat_id, identifier, identifier_type)

                    if check_connection(identifier, identifier_type):
                        if power_outage_start:
                            outage_duration = current_time - power_outage_start
                            user_manager.save_outage_data(chat_id, identifier, identifier_type, power_outage_start, current_time)
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=f"⚡ Electricity is back on for {identifier}! "
                                     f"There was no electricity for: {format_timedelta(outage_duration)}. "
                                     f"Outage started at: {power_outage_start}."
                            )
                            user_manager.set_power_outage_start(chat_id, identifier, identifier_type, None)
                    else:
                        if not power_outage_start:
                            user_manager.set_power_outage_start(chat_id, identifier, identifier_type, current_time)
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=f"🚫 Electricity is down for {identifier}"
                            )

            if current_time.weekday() == 6 and current_time.hour == 23 and current_time.minute == 59:
                weekly_report = user_manager.generate_weekly_report(chat_id)
                for identifier, report_data in weekly_report.items():
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"Weekly report for {identifier}:\n"
                             f"Number of shutdowns: {report_data['shutdown_count']}\n"
                             f"Average shutdown length: {format_timedelta(report_data['average_shutdown_length'])}\n"
                             f"Longest shutdown: {format_timedelta(report_data['longest_shutdown'])}\n"
                             f"Shortest shutdown: {format_timedelta(report_data['shortest_shutdown'])}\n"
                             f"Total downtime: {format_timedelta(report_data['total_duration'])}\n"
                    )
    finally:
        session.close()