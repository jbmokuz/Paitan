from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

#Club Managers
class ClubManagement(db.Model):
    id = db.Column(db.Integer, primary_key=True,nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)

#List of all club members
class ClubList(db.Model):
    id = db.Column(db.Integer, primary_key=True,nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    
class User(UserMixin,db.Model):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tenhou_name = db.Column(db.String(64))

    clubmanagement = relationship(ClubManagement, cascade="all,delete", backref="user")
    clublist = relationship(ClubList, cascade="all,delete", backref="user")
    tourneyUserlist = relationship("TourneyUserList", cascade="all,delete", backref="user")    
        
    def get_id(self):
        return self.user_id
    
    def __repr__(self):
        return '<User {}>'.format(self.user_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class Club(db.Model):
    club_id = db.Column(db.Integer, primary_key=True,nullable=False)
    club_name = db.Column(db.String(80), unique=False, nullable=True)
    tenhou_room = db.Column(db.String(120), unique=False, nullable=True)
    tenhou_rules = db.Column(db.String(120), unique=False, nullable=True)
    mjsoul_room = db.Column(db.String(120), unique=False, nullable=True)
    tourney_id = db.Column(db.Integer,db.ForeignKey('tourney.tourney_id'), nullable=True)    
    
    tourneyUserlist = relationship("Tourney", cascade="all,delete", backref="tourney")    

    def __repr__(self):
        return '<Club %r>' % self.club_name

class Tourney(db.Model):
    tourney_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    tourney_name = db.Column(db.String(128), unique=False, nullable=True)

    def __repr__(self):
        return '<Tourney %r>' % self.tourney_name

class TenhouGame(db.Model):
    tenhou_game_id = db.Column(db.Integer, primary_key=True,nullable=False, autoincrement=True)
    replay_id = db.Column(db.String(128), unique=True, nullable=True)
    rate = db.Column(db.String(128), unique=False, nullable=True)
    
    ton = db.Column(db.String(80), unique=False, nullable=True)
    nan = db.Column(db.String(80), unique=False, nullable=True)
    xia = db.Column(db.String(80), unique=False, nullable=True)
    pei = db.Column(db.String(80), unique=False, nullable=True)
    
    ton_score = db.Column(db.Integer ,nullable=True)
    nan_score = db.Column(db.Integer ,nullable=True)
    xia_score = db.Column(db.Integer ,nullable=True)
    pei_score = db.Column(db.Integer ,nullable=True)

    ton_shugi = db.Column(db.Integer ,nullable=True)
    nan_shugi = db.Column(db.Integer ,nullable=True)
    xia_shugi = db.Column(db.Integer ,nullable=True)
    pei_shugi = db.Column(db.Integer ,nullable=True)
    
    ton_payout = db.Column(db.Integer ,nullable=True)
    nan_payout = db.Column(db.Integer ,nullable=True)
    xia_payout = db.Column(db.Integer ,nullable=True)
    pei_payout = db.Column(db.Integer ,nullable=True)

    tourneyGamelist = relationship("TourneyGameList", cascade="all,delete", backref="game")
    
    def __repr__(self):
        return '<TenhouGame %r>' % self.replay_id
    
class TourneyUserList(db.Model):
    id = db.Column(db.Integer, primary_key=True,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    tourney_id = db.Column(db.Integer,db.ForeignKey('tourney.tourney_id'), nullable=False)

class TourneyGameList(db.Model):
    id = db.Column(db.Integer, primary_key=True,nullable=False)
    #@WARNING You need an underscore?!?!?!?!?!?!?
    tenhou_game_id = db.Column(db.Integer, db.ForeignKey('tenhou_game.tenhou_game_id'),nullable=False)
    tourney_id = db.Column(db.Integer,db.ForeignKey('tourney.tourney_id'), nullable=False)
    
