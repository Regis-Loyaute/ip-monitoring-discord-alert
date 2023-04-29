#!/usr/bin/env python3
import time
import requests
import logging
import configparser
from datetime import datetime
from ping3 import ping

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")
ip_address = config.get("settings", "ip_address")
webhook_url = config.get("settings", "webhook_url")

last_ping_time = datetime.now()
is_up = True

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler('ip_monitor.log')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

def send_webhook_message(content):
    try:
        response = requests.post(webhook_url, json={"content": content})
        if response.status_code == 204:
            logger.info("Webhook sent successfully")
        else:
            logger.warning(f"Error sending webhook: status code {response.status_code}, response text {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending webhook: {e}")

def downtime_seconds(last_ping_time, current_time):
    downtime = current_time - last_ping_time
    return downtime.total_seconds()

def ping_with_retries(ip, max_retries=3, delay_between_retries=2):
    for attempt in range(1, max_retries + 1):
        try:
            response_time = ping(ip)
            return response_time
        except Exception as e:
            logger.debug(f"Ping error on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(delay_between_retries)
            else:
                return None

def main():
    global last_ping_time, is_up
    while True:
        response_time = ping_with_retries(ip_address)

        if response_time is not None:
            if not is_up:
                now = datetime.now()
                downtime_secs = downtime_seconds(last_ping_time, now)
                message = f"{ip_address} is up! It was down for {downtime_secs:.2f} seconds."
                logger.info(message)
                send_webhook_message(message)
                is_up = True
            last_ping_time = datetime.now()
        else:
            if is_up:
                last_ping_time = datetime.now()
                is_up = False
                logger.warning(f"{ip_address} is down")

        time.sleep(10)  # Ping every 10 seconds

if __name__ == '__main__':
    main()
