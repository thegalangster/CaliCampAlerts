import os, crud
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_text(phone_number, campground_code):

    # Authenticate client
    account_sid = os.environ.get('TWILIO_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    # Form message in the text
    text_body = form_text_message(campground_code)

    # Send the text
    try:
        message = client.messages.create(
        to=phone_number, 
        from_="+16413213785",
        body=text_body)
        return True
    except Exception as e:
        print(e.message)
        return False

def send_email(email, campground_code):

    auth_token = os.environ.get('SENDGRID_API_KEY')

    campground_name = crud.get_campground_by_code(campground_code).name.title()
    html_content="Book Here: " + "https://www.recreation.gov/camping/campgrounds/" + str(campground_code)

    message = Mail(
    from_email='fillsblanks@gmail.com',
    to_emails=email,
    subject="New Availability: " + campground_name,
    html_content=html_content)
    try:
        sg = SendGridAPIClient(auth_token)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(e.message)
        return False


def form_text_message(campground_code):
    # Form message
    campground_name = crud.get_campground_by_code(campground_code).name.title()
    url = "https://www.recreation.gov/camping/campgrounds/" + str(campground_code)
    return "Availability at " + campground_name + "\n Book Here: " + url


def initial_text_message():
    "Subscribed to CaliCamp Alerts\nText STOP to unsubscribe to all alerts"
    # Need to add detail on the reservation filters
