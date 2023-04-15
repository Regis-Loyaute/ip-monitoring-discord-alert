#!/usr/bin/env python3
import time
import requests
import logging
from datetime import datetime
from ping3 import ping

ip_address = "10.0.0.2"
webhook_url = "https://discord.com/api/webhooks/1096581762450210976/B1v-ofdsfsdf3yPMy_GYfsdfgsdfdsfsdngj44CXDT3AaR5454534534uk2DzSD_FWAmWJ1twt_4Wy59aCx"
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

while True:
    try:
        response_time = ping(ip_address)
    except OSError as e:
        logger.error(f"Ping error: {e}")
        response_time = None

    if response_time is not None:
        if not is_up:
            now = datetime.now()
            downtime = now - last_ping_time
            downtime_seconds = downtime.total_seconds()
            message = f"{ip_address} is up! It was down for {downtime_seconds:.2f} seconds."
            logger.info(message)
            send_webhook_message(message)
            is_up = True
        last_ping_time = datetime.now()
    else:
        if is_up:
            last_ping_time = datetime.now()
            is_up = False
            logger.warning(f"{ip_address} is down")

    time.sleep(10)