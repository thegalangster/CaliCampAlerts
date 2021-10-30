"""CRUD operations."""

from model import db, User, Alert, Campground, Availability, connect_to_db

def create_user(name, username, password, email, phone, created_at, updated_at):
    """Create and return a new user."""

    user = User(name=name, 
                username=username, 
                password=password, 
                email=email,
                phone=phone, 
                created_at=created_at, 
                updated_at=updated_at)
    db.session.add(user)
    db.session.commit()
    return user

def create_alert(email_enabled, phone_enabled, date_start, date_stop, day, min_length, campground, user, created_at, updated_at):
    """Create and return a new alert."""

    alert = Alert(email_enabled=email_enabled, 
                phone_enabled=phone_enabled, 
                date_start=date_start, 
                date_stop=date_stop, 
                day=day, 
                min_length=min_length, 
                campground=campground, 
                user=user, 
                created_at=created_at, 
                updated_at=updated_at)

    db.session.add(alert)
    db.session.commit()
    return alert

def delete_alert(alert):
    db.session.delete(alert)
    db.session.commit()

def create_campground(name, code, park_type, park_name, lat_long, description, image, created_at, updated_at):
    """Create and return a new campground."""

    campground = Campground(
                name=name, 
                code=code, 
                park_type=park_type, 
                park_name=park_name, 
                lat_long=lat_long, 
                description=description, 
                image=image, 
                created_at=created_at, 
                updated_at=updated_at)

    db.session.add(campground)
    db.session.commit()
    return campground

def get_all_alerts():
    return Alert.query.all()

def get_alert_by_id(id):
    return Alert.query.get(id)

def get_campground_by_code(code):
    return Campground.query.filter_by(code=code).first()

if __name__ == '__main__':
    from server import flask_app
    connect_to_db(flask_app)