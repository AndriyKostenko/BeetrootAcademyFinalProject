from app import db


# initializing the database
class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String)
    surname = db.Column(db.String)
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    pulse = db.Column(db.Integer)
    arterial_pressure = db.Column(db.Integer)
    preferable_sport = db.Column(db.String)
    date = db.Column(db.String)


class Trainings(db.Model):
    __tablename__ = 'trainings'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.Integer, nullable=False)
    running = db.Column(db.Integer)
    push_ups = db.Column(db.Integer)
    sit_ups = db.Column(db.Integer)
    date = db.Column(db.Integer)


