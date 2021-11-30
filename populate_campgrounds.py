import requests, crud, os, re
from datetime import datetime
from server import app
from model import connect_to_db

api_key = os.environ['REC_GOV_API_KEY']

more_data = True
offset = 0
url = "https://ridb.recreation.gov/api/v1/facilities"

while more_data:
    payload = {'apikey': api_key}
    payload["limit"] = 50
    payload["offset"] = offset
    payload["full"] = "true"
    payload["activity"] = "CAMPING"
    payload["state"] = "CA"
    res = requests.get(url, params=payload)
    data = res.json()

    rec_data = data["RECDATA"]
    if not rec_data:
        break
    for campground in rec_data:
        if campground["Reservable"] == "false":
            rec_data.remove(campground)
        else:
            try:
                park_name = campground["RECAREA"][0]["RecAreaName"]
            except IndexError:
                park_name = "None"
            try:
                image = campground["MEDIA"][0]["URL"]
            except IndexError:
                    image = ""
            with app.app_context():
                connect_to_db(app)

                # Sanitize campground name
                name = campground["FacilityName"].title()
                name = re.split("[.?!()\-,]", name)[0]

                crud.create_campground(name=name,
                                    code=campground["FacilityID"], 
                                    park_type="federal", 
                                    park_name=park_name.title(), 
                                    lat_long={"lat": campground["FacilityLatitude"], "long": campground["FacilityLongitude"]}, 
                                    description=campground["FacilityDescription"], 
                                    image=image,
                                    created_at=datetime.now(), 
                                    updated_at=datetime.now())
    offset += 50



