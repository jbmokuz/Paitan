from app import app
from flask import render_template, flash, redirect,  url_for
from flask_login import current_user, login_user, logout_user
from app.models import User, Club
from app.forms import LoginForm, PasswordForm, TenhouForm
from app import db
from database import *

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return "YOU ARE IN!"#redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if current_user.is_authenticated:
        clubs = getClubsForUser(current_user.user_id)
        pass_form = PasswordForm()
        if pass_form.validate_on_submit():
            print("password")
            current_user.set_password(pass_form.password.data)
            current_user.user_name
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('settings.html', title='Register',pass_form=pass_form, clubs=clubs)
    return redirect(url_for('index'))

@app.route("/club_settings/<path:club_id>", methods=['GET','POST'])
def club_settings(club_id):
    if current_user.is_authenticated:

        tenhou_form = TenhouForm()

        try:
            club_id = int(club_id)
            if club_id in [i.club_id for i in getClubsForUser(current_user.user_id)]:

                club = getClub(club_id)
                if tenhou_form.validate_on_submit():
                        club.tenhou_room = tenhou_form.admin_page.data.split("?")[-1]
                        club.tenhou_rules = tenhou_form.rules.data
                        db.session.commit()
                        print("tenhou")
                        return redirect(url_for('club_settings',club_id=club_id))
                return render_template('club_settings.html',club=club, tenhou_form=tenhou_form)
        except:
            pass
        
    return redirect(url_for('index'))
