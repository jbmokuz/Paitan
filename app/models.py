from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin,db.Model):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))

    def get_id(self):
        return self.user_id
    
    def __repr__(self):
        return '<User {}>'.format(self.user_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Club(db.Model):
    club_id = db.Column(db.Integer, primary_key=True,nullable=False)
    club_name = db.Column(db.String(80), unique=False, nullable=True)
    tenhou_room = db.Column(db.String(120), unique=False, nullable=True)
    tenhou_rules = db.Column(db.String(120), unique=False, nullable=True)
    mjsoul_room = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<Club %r>' % self.club_name


class ClubManagement(db.Model):
    id = db.Column(db.Integer, primary_key=True,nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    

"""
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Tourney(db.Model):
    tourney_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=True)
    tenhou_room = db.Column(db.String(120), unique=False, nullable=True)
    tenhou_rules = db.Column(db.String(120), unique=False, nullable=True)
    mjsoul_room = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<Tourney %r>' % self.name

class Tourney_Signup(db.Model):
    tourney_signup_id = db.Column(db.Integer, primary_key=True)
    tourney_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, primary_key=True)
    #player = db.relationship('Player', uselist=False)
    
    def __repr__(self):
        return '<Tourney Signup %d>' % self.tourney_signup_id


class Club(db.Model):
    club_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=True)
    tenhou_room = db.Column(db.String(120), unique=False, nullable=True)
    tenhou_rules = db.Column(db.String(120), unique=False, nullable=True)
    mjsoul_room = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<Club %r>' % self.name


class Club_Signup(db.Model):
    club_signup_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, primary_key=True)
    
    def __repr__(self):
        return '<Club Signup %d>' % self.club_signup_id


class Player(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=True)
    discord_name = db.Column(db.String(80), unique=False, nullable=True)
    tenhou_id = db.Column(db.String(120), unique=False, nullable=True)
    mjsoul_id = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<Player %r>' % self.name

"""
