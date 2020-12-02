from app import app
from flask import render_template, flash, redirect,  url_for
from flask_login import current_user, login_user, logout_user
from app.models import User, Club
from app.forms import LoginForm, PasswordForm, TenhouForm
from app import db

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
        user = User.query.filter_by(username=form.username.data).first()
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
        club = db.session.query(Club).filter(Club.club_id==current_user.club_id).first()
        if club:
            print("CLUB NAME:",club.name,club.tenhou_room,club.tenhou_rules)
            #club.name = "foo"
            #db.session.commit()
        pass_form = PasswordForm()
        tenhou_form = TenhouForm()
        if pass_form.validate_on_submit():
            print("password")
            current_user.set_password(pass_form.password.data)
            current_user.username
            db.session.commit()
            return redirect(url_for('index'))
        if tenhou_form.validate_on_submit():
            if (club):
                import pdb
                pdb.set_trace()
                club.tenhou_room = tenhou_form.admin_page.data
                club.tenhou_rules = tenhou_form.rules.data
                db.session.commit()
            print("tenhou")
            return redirect(url_for('index'))
        return render_template('settings.html', title='Register',club=club, pass_form=pass_form, tenhou_form=tenhou_form)
    return redirect(url_for('index'))

