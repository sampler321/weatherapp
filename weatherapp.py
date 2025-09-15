import json
import smtplib
import os
import datetime
import pytz # We're adding the pytz library to handle time zones

from email.message import EmailMessage
from buienradar.buienradar import get_data
from buienradar.constants import CONTENT, SUCCESS

# Email account information
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
APP_PASSWORD = os.environ.get('APP_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

def send_email(subject, body):
    """Sends an email with the given subject and body."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def get_temperature():
    """Fetches the current temperature for Rotterdam."""
    latitude = 51.9244
    longitude = 4.4777
    result = get_data(latitude=latitude, longitude=longitude)
    if result.get(SUCCESS):
        raw_data_content = json.loads(result[CONTENT])
        for station in raw_data_content['actual']['stationmeasurements']:
            if station['stationname'] == 'Meetstation Rotterdam':
                return station['temperature']
    return None

# The main part that runs the whole script
if __name__ == "__main__":
    temperature = get_temperature()

    # Get the current time and adjust for the time zone in Rotterdam
    local_tz = pytz.timezone('Europe/Amsterdam')
    current_time = datetime.datetime.now(local_tz)
    current_hour = current_time.strftime("%I %p").lstrip('0')

    if temperature is not None:
        subject = "Daily Weather Report"
        body = f"The temperature today at {current_hour} is {temperature} °C. Have a great day!"
        send_email(subject, body)
    else:
        print("Could not get temperature data.")
