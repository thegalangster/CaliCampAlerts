from datetime import datetime
import crud, os, model, json, random, server

# https://www.recreation.gov/camping/campgrounds/232502

os.system('dropdb calicamp')
os.system('createdb calicamp')
model.connect_to_db(server.app)
model.db.create_all()

"""

user = {
    "name": "Aimee Galang",
    "username": "aimeegalang",
    "password": "password",
    "email": "aimeegalang@gmail.com",
    "phone": 7024982047,
}

alert = {
    "email_enabled": "True",
    "phone_enabled": "True",
    "date_start": "2021-10-28",
    "date_stop": "2021-12-30",
    "day": "1111111",
    "min_length": 1
}

campground = {
    "name": "Aimee's Test",
    "code": 232502, 
    "park_type": "federal", 
    "park_name": "Channel Islands National Park",
    "lat_long": {"lat": 35.9916667, "long": -121.4941667},
    "description": "Once visitors have scaled the rugged cliffs using the stairwell from the Landing Cove, they will be rewarded with a campground perched on the bluffs with magnificent coastal views.",
    "image": "https://cdn.recreation.gov/public/2018/08/07/01/05/b06b2294-25a0-4501-937a-62cdee4e63bc_1600.jpg"
}

now = datetime.now()

new_user = crud.create_user(name=user['name'], username=user['username'], password=user['password'], email=user['email'], phone=user['phone'], created_at=now, updated_at=now)
new_campground = crud.create_campground(name=campground['name'], code=campground['code'], park_type=campground['park_type'], park_name=campground['park_name'], lat_long=campground['lat_long'], description=campground['description'], image=campground['image'], created_at=now, updated_at=now)

# Format date start/stop to datetime object
date_start = datetime.strptime(alert['date_start'], "%Y-%m-%d")
date_stop = datetime.strptime(alert['date_stop'], "%Y-%m-%d")

new_alert = crud.create_alert(email_enabled=(alert['email_enabled'] == 'True'), phone_enabled=(alert['phone_enabled'] == 'True'), date_start=date_start, date_stop=date_stop, day=alert['day'], min_length=alert['min_length'], campground=new_campground, user=new_user, created_at=now, updated_at=now)
"""