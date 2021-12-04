"""CaliCamp Alerts Model"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Users"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  
    name = db.Column(db.String)

    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.BigInteger, nullable=True)
  
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def get_id(self):
           return (self.user_id)

    def set_password(self, password):
        """Create a hashed password"""
        self.password = generate_password_hash(
                password,
                method='sha256'
        )

    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User user_id={self.user_id} name={self.name} username={self.username} email={self.email} phone={self.phone}>'

class Alert(db.Model):
    """Alerts"""

    __tablename__ = "alerts"

    alert_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    is_available = db.Column(db.Boolean)
    is_sent_email = db.Column(db.Boolean)
    is_sent_phone = db.Column(db.Boolean)
    email_enabled = db.Column(db.Boolean)
    phone_enabled = db.Column(db.Boolean)

    date_start = db.Column(db.DateTime)
    date_stop = db.Column(db.DateTime)

    day = db.Column(db.String) # bitmap for days of the week
    min_length = db.Column(db.Integer)
  
    campground_id = db.Column(db.Integer, db.ForeignKey('campgrounds.campground_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    campground = db.relationship("Campground", backref="alerts")
    user = db.relationship("User", backref="alerts")

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Alert is_sent_email={self.is_sent_email} is_sent_phone={self.is_sent_phone} is_available={self.is_available} alert_id={self.alert_id} email_enabled={self.email_enabled} phone_enabled={self.phone_enabled} date_start={self.date_start} date_stop={self.date_stop} day={self.day} min_length={self.min_length}>'
 
class Campground(db.Model):
    """Campgrounds"""

    __tablename__ = "campgrounds"

    campground_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    code = db.Column(db.Integer)
    name = db.Column(db.String)

    # Park Information
    park_type = db.Column(db.String)
    park_name = db.Column(db.String)

    # Campground Details
    lat_long = db.Column(db.JSON) # JSON
    description = db.Column(db.String)
    image = db.Column(db.String) 
  
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime) 

    def __repr__(self):
        return f'<Campground campground_id={self.campground_id} code={self.code} name={self.name} park_type={self.park_type} park_name={self.park_name} lat_long={self.lat_long} description={self.description} image={self.image}>'

class Availability(db.Model):
    """Current Campground Availability"""

    __tablename__ = "availability"

    availability_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_start = db.Column(db.DateTime)
    date_stop = db.Column(db.DateTime)
  
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.alert_id'))
    alert = db.relationship("Alert", backref="availability")
  
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User availability_id={self.availability_id} date_start={self.date_start} date_stop={self.date_stop}>'

def connect_to_db(flask_app, db_uri="postgresql:///calicamp", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
