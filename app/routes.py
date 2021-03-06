from app import app
from flask import render_template, flash, redirect,  url_for
from flask_login import current_user, login_user, logout_user
from app.models import *
from app.forms import *
from app import db
from database import *
from functions import *


MOKU_USERID = 119046709983707136

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
        if current_user.user_id == MOKU_USERID:
            clubs = getAllClubs()
        else:
            clubs = getClubsForUser(current_user.user_id)
            
        tenhou_name_form = TenhouNameForm()
        pass_form = PasswordForm()

        if tenhou_name_form.validate_on_submit():
            print("tenhou name")
            current_user.tenhou_name = tenhou_name_form.tenhouName.data
            db.session.commit()
            return redirect(url_for('index'))
        
        if pass_form.validate_on_submit():
            print("password")
            current_user.set_password(pass_form.password.data)
            db.session.commit()
            flash("Password Updated")
            return redirect(url_for('index'))
        
        return render_template('settings.html', title='Register',pass_form=pass_form, clubs=clubs, tenhou_name_form=tenhou_name_form)
    return redirect(url_for('index'))

@app.route("/club_settings/<path:club_id>", methods=['GET','POST'])
def club_settings(club_id):

    global MOKU_USERID
    
    if current_user.is_authenticated:

        tenhou_form = TenhouForm()
        rate_form = RateForm()
        print(rate_form)
        
        #try:
        club_id = int(club_id)
        if club_id in [i.club_id for i in getClubsForUserManage(current_user.user_id)] or current_user.user_id == MOKU_USERID:

            club = getClub(club_id)
            
            try:
                rules = int(club.tenhou_rules,16)
            except:
                rules = 0
                
            if tenhou_form.validate_on_submit():
                    club.tenhou_room = tenhou_form.admin_page.data.split("?")[-1]
                    rules = 1
                    if not tenhou_form.aka.data == True:
                        rules = rules | 2
                    if not tenhou_form.kuitan.data == True:
                        rules = rules | 4
                    if tenhou_form.hanchan.data == True:
                        rules = rules | 8
                    if tenhou_form.sanma.data == True:
                        rules = rules | 0x10
                    if tenhou_form.threefive.data == True:
                        rules = rules | 0x40                        
                    if tenhou_form.tsumogiri.data == True:
                        rules = rules | 0x100
                    if tenhou_form.shugi2000.data == True:
                        rules = rules | 0x200
                    if tenhou_form.shugi5000.data == True:
                        rules = rules | 0x400
                            
                    club.tenhou_rules = hex(rules)[2:].zfill(4).upper()
                    db.session.commit()
                    print("tenhou")
                    return redirect(url_for('club_settings',club_id=club_id))

            if rate_form.validate_on_submit():
                club.tenhou_rate = rate_form.rate.data.strip()
                db.session.commit()
                print("New rate ",rate_form.rate.data.strip())
                return redirect(url_for('club_settings',club_id=club_id))                
                
            return render_template('club_settings.html',club=club, tenhou_form=tenhou_form, rate_form=rate_form,aka=(rules&2)==0,kuitan=(rules&4)==0,hanchan=(rules&8)!=0,sanma=(rules&0x10)!=0,threefive=(rules&0x40)!=0,tsumogiri=(rules&0x100)!=0,shugi2=(rules&0x200)!=0,shugi5=(rules&0x500)!=0)
        #except:
        #    pass
        
    return redirect(url_for('index'))

@app.route("/clubs", methods=['GET'])
def clubs():
    return render_template('club_list.html',clubs=getClubs())


@app.route("/club_standings/<path:clubId>", methods=['GET'])
def club_standings(clubId):
    try:
        clubId = int(clubId)
    except:
        flash("Bad club ID")
        return redirect(url_for('index'))

    club = getClub(clubId)
    if club == None:
        flash("No such club")
        return redirect(url_for('index'))

    standings = getStandings(clubId)
    gamesRaw = getGamesForClub(clubId)
    games = {}

    print(gamesRaw)
    
    for game in gamesRaw:
        if not game.round_number in games:
            games[game.round_number] = []
        games[game.round_number].append(game)
        
    
    return render_template('club_standings.html',club=club, standings=standings, games=games)



"""
@app.route("/tourney", methods=['GET'])
def tourney():
    return render_template('tourney_list.html',tourneys=getTourneys())

@app.route("/tourney_standings/<path:tourneyId>", methods=['GET'])
def tourney_standings(tourneyId):
    try:
        tourneyId = int(tourneyId)
    except:
        flash("Bad tourney ID")
        return redirect(url_for('index'))

    tourney = getTourney(tourneyId)
    if tourney == None:
        flash("No such tourney")
        return redirect(url_for('index'))

    standings = getStandings(tourneyId)

    tablesRaw = getTablesForRoundTourney(tourneyId,tourney.current_round)
    tables = []
    for t in tablesRaw:
        table = []
        if t.ton == None or getUser(t.ton) == None:
            table.append(None)
        else:
            u = getUser(t.ton)
            table.append(u.user_name+f" ({u.tenhou_name})")                        


        if t.nan==None or getUser(t.nan) == None:
            table.append(None)
        else:
            u = getUser(t.nan)
            table.append(u.user_name+f" ({u.tenhou_name})")            

        if t.xia == None or getUser(t.xia) == None:
            table.append(None)
        else:
            u = getUser(t.xia)
            table.append(u.user_name+f" ({u.tenhou_name})")                        

        if t.pei == None or getUser(t.pei) == None:
            table.append(None)
        else:
            u = getUser(t.pei)
            table.append(u.user_name+f" ({u.tenhou_name})")                        
        table.append(t.finished)
        tables.append(table)

    gamesRaw = getGamesForTourney(tourneyId)
    games = {}

    print(gamesRaw)
    
    for game in gamesRaw:
        if not game.round_number in games:
            games[game.round_number] = []
        games[game.round_number].append(game)
        
    
    print(f"tables: {tables}")
    
    return render_template('tourney_standings.html',tourney=tourney, standings=standings, tables=tables, games=games)
"""

                            
        


