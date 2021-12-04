"""Server for CaliCamp."""

from flask import (Flask, render_template, request, flash, session, redirect, jsonify)
from twilio.twiml.messaging_response import MessagingResponse
from model import connect_to_db
from jinja2 import StrictUndefined
from celery import Celery
import collect, crud, server, message, os
from datetime import datetime
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from forms import Signup, Login
from flask_wtf.csrf import CSRFProtect
from model import db, User


# Import MapBox key

mapbox_access_token = os.environ.get('MAPBOX_API_KEY')

# Need to seperate celery and flask

csrf = CSRFProtect()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
csrf.init_app(app)
app.jinja_env.undefined = StrictUndefined

login_manager = LoginManager()
login_manager.init_app(app)


celery = Celery('tasks', broker_url = 'amqp://admin:password@localhost:5672/myvhost')
celery.conf.timezone = 'America/Los_Angeles'

# Performed once celery app is up
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
        sender.add_periodic_task(240.0, collect_and_alert.s(), expires=60.0)

@celery.task
def collect_and_alert(alert_id=None):
    print("***** ALERT TASK RUNNING *****")
    with app.app_context():
        connect_to_db(app)
        # Periodic check to run on all existing alerts
        if alert_id is None:
            alerts = crud.get_all_alerts()
        else:
            alerts = [crud.get_alert_by_id(alert_id)]
        for alert in alerts:
            # Collect and check availability based on alert requirements
            if not alert.is_available:
                if collect.check_availability(alert=alert):
                    alert.is_available = True
            # Send text or email
            if alert.is_available:
                if alert.phone_enabled and not alert.is_sent_phone:
                    if message.send_text(phone_number=alert.user.phone, campground_code=alert.campground.code):
                        alert.is_sent_phone = True
                if alert.email_enabled and not alert.is_sent_email:
                    if message.send_email(email=alert.user.email, campground_code=alert.campground.code):
                        alert.is_sent_email = True
                db.session.commit()

@app.route('/')
def index():
    campgrounds = crud.get_all_campgrounds()
    return render_template('homepage.html', mapbox_access_token=mapbox_access_token, campgrounds=convert_to_geojson(campgrounds))

def convert_to_geojson(campgrounds):
    campgrounds_geojson = []
    for campground in campgrounds:
        if campground.lat_long["long"] == 0 and campground.lat_long["lat"] == 0:
            continue
        campgrounds_geojson.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [campground.lat_long["long"], campground.lat_long["lat"]]
                },
                "properties": {
                    "name": campground.name,
                    "park_name": campground.park_name,
                    "code": campground.code
                }
            }
        )
    return campgrounds_geojson

@app.route("/campground.json")
def get_campground():
    """Return campground information"""
    code = request.args.get("code")

    campground = crud.get_campground_by_code(code)

    campground_att = {}
    campground_att['name'] = campground.name
    campground_att['parkName'] = campground.park_name
    campground_att['description'] = campground.description
    campground_att['imageUrl'] = campground.image

    return jsonify(campground_att)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = Login(request.form)
    if form.validate_on_submit():
        user = crud.get_user_by_username(form.username.data)
        if user and user.check_password(password=form.password.data):
            login_user(user)
            return redirect('/')
        flash('Invalid username or password')
        return redirect('/login')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Signup(request.form)
    if form.validate_on_submit():
        user = crud.get_user_by_username(form.username.data)
        if user is None:
            user = crud.create_user(name=form.name.data, username=form.username.data, password=form.password.data, email=form.email.data, phone=form.phone.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            login_user(user)  # Login as user
            return redirect('/')
        flash("Username already exists")
    return render_template('signup.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None

@app.route('/create_alert', methods=['POST'])
@login_required
def create_alert():
    datefilter = request.form.get("datefilter").split(' - ')
    datefilter_start = datetime.strptime(datefilter[0], "%B %d, %Y")
    datefilter_stop = datetime.strptime(datefilter[1], "%B %d, %Y")
    email = request.form.get("email")
    text = request.form.get("text")
    campground = crud.get_campground_by_code(request.form.get("campground_code"))
    print("CAMPGROUND *******")
    print(campground)
    user = crud.get_user_by_id(current_user.get_id())
    print("USE *******")
    print(user)

    time_delta = datefilter_stop - datefilter_start

    alert = {
        "email_enabled": bool(email),
        "phone_enabled": bool(text),
        "date_start": datefilter_start,
        "date_stop": datefilter_stop,
        "day": "1111111",
        "min_length": time_delta.days,
        "campground": campground,
        "user": user
    }

    now = datetime.now()
    new_alert = crud.create_alert(is_available=False, is_sent_email=False, is_sent_phone=False, email_enabled=alert['email_enabled'], phone_enabled=alert['phone_enabled'], date_start=alert['date_start'], date_stop=alert['date_stop'], day=alert['day'], min_length=alert['min_length'], campground=campground, user=user, created_at=now, updated_at=now)
    print("CREATE ALERT 1")
    print(new_alert)

    alert_id = new_alert.alert_id
    server.collect_and_alert.s(alert_id=alert_id).apply_async()
    campgrounds = crud.get_all_campgrounds()
    print("CREATE ALERT")
    print(new_alert)
    return render_template('homepage.html', mapbox_access_token=mapbox_access_token, campgrounds=convert_to_geojson(campgrounds))

@app.route('/show_alert')
@login_required
def show_alert():

    return render_template('alerts.html', codes=codes)


@app.route('/delete_alert', methods=['POST'])
def delete_alert():
    alert_id = request.form.get("alert_id")
    alert = crud.get_alert_by_id(alert_id)
    crud.delete_alert(alert)

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
