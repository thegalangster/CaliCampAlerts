"""Server for CaliCamp."""

from flask import (Flask, render_template, request, flash, session, redirect)
from twilio.twiml.messaging_response import MessagingResponse
from model import connect_to_db
from jinja2 import StrictUndefined
from celery import Celery
import collect, crud, server, message
from datetime import datetime

# Need to seperate celery and flask

app = Flask(__name__)
app.secret_key = 'aimee'
app.jinja_env.undefined = StrictUndefined

celery = Celery('tasks', broker_url = 'amqp://admin:password@localhost:5672/myvhost')
celery.conf.timezone = 'America/Los_Angeles'

# Performed once celery app is up
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
        sender.add_periodic_task(15.0, collect_and_alert.s(), expires=60.0)

@celery.task
def collect_and_alert(alerts=None):
    with app.app_context():
        connect_to_db(app)
        # Periodic check to run on all existing alerts
        if alerts is None:
            alerts = crud.get_all_alerts()
        for alert in alerts:
            # Collect and check availability based on alert requirements
            if collect.check_availability(alert=alert):
                # Send text or email
                if alert.phone_enabled:
                    message.send_text(phone_number=alert.user.phone, campground_code=alert.campground.code)
                if alert.email_enabled:
                    message.send_email(email=alert.user.email, campground_code=alert.campground.code)
                # Delete alert for now
                # Need to implement updating user on new availability
                crud.delete_alert(alert)

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/create_alert')
def create_alert():
    '''Hardcoded for now'''

    user = {
    "name": "Aimee Jane Galang",
    "username": "aimeejgalang",
    "password": "password",
    "email": "aimeejgalang@gmail.com",
    "phone": 7024982047,
    }

    alert = {
        "email_enabled": "True",
        "phone_enabled": "True",
        "date_start": "2021-12-01",
        "date_stop": "2021-12-30",
        "day": "1111111",
        "min_length": 1
    }

    campground = crud.get_campground_by_code("232502")


    # Format date start/stop to datetime object
    date_start = datetime.strptime(alert['date_start'], "%Y-%m-%d")
    date_stop = datetime.strptime(alert['date_stop'], "%Y-%m-%d")
    now = datetime.now()

    new_user = crud.create_user(name=user['name'], username=user['username'], password=user['password'], email=user['email'], phone=user['phone'], created_at=now, updated_at=now)
    new_alert = crud.create_alert(email_enabled=(alert['email_enabled'] == 'True'), phone_enabled=(alert['phone_enabled'] == 'True'), date_start=date_start, date_stop=date_stop, day=alert['day'], min_length=alert['min_length'], campground=campground, user=new_user, created_at=now, updated_at=now)

    # Add task
    collect_and_alert.s(new_alert)

    return render_template('create_alert.html')


#     *** Need to have application reachable publicly for Twilio to send a webhook ***
#     Reference: https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python

# @app.route("/sms", methods=['GET', 'POST'])
# def sms_reply():
#     """Delete user and alert is user responds with STOP"""

#     if request.method == "POST" and request.POST['Body'] == "STOP":
#         crud.delete_alert(alert)

#     # Start our TwiML response
#     resp = MessagingResponse()

#     # Add a message
#     resp.message("Thank you for using CaliCamp alerts. Unsubscribed")

#     return str(resp)

if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
