from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------- MODELS ------------------------
class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    teams = db.relationship('Team', backref='sport', lazy=True)
    matches = db.relationship('Match', backref='sport', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    short_name = db.Column(db.String(10))
    logo_color = db.Column(db.String(10))
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    players = db.relationship('Player', backref='team', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    position = db.Column(db.String(50))
    jersey_number = db.Column(db.Integer)
    nationality = db.Column(db.String(50))
    matches_played = db.Column(db.Integer, default=0)
    # Sport-specific stats
    runs = db.Column(db.Integer, default=0)
    wickets = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    raid_points = db.Column(db.Integer, default=0)
    tackle_points = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    smashes = db.Column(db.Integer, default=0)
    aces = db.Column(db.Integer, default=0)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team1_score = db.Column(db.String(20), default='0')
    team2_score = db.Column(db.String(20), default='0')
    match_details = db.Column(db.String(100))
    venue = db.Column(db.String(50))
    match_date = db.Column(db.DateTime, default=datetime.utcnow)
    match_time = db.Column(db.String(10))
    status = db.Column(db.String(20), default='upcoming')
    is_live = db.Column(db.Boolean, default=False)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])

# ---------------------- SAMPLE DATA ------------------------
def create_sample_data():
    db.drop_all()
    db.create_all()

    # Sports
    cricket = Sport(name='Cricket')
    football = Sport(name='Football')
    hockey = Sport(name='Hockey')
    kabaddi = Sport(name='Kabaddi')
    badminton = Sport(name='Badminton')
    db.session.add_all([cricket, football, hockey, kabaddi, badminton])
    db.session.commit()

    # Teams
    teams = [
        Team(name='Mumbai Indians', short_name='MI', logo_color='#1f77b4', sport_id=cricket.id),
        Team(name='Chennai Super Kings', short_name='CSK', logo_color='#ff7f0e', sport_id=cricket.id),
        Team(name='India Football', short_name='IND-F', logo_color='#2ca02c', sport_id=football.id),
        Team(name='Brazil Football', short_name='BRA', logo_color='#d62728', sport_id=football.id),
        Team(name='India Hockey', short_name='IND-H', logo_color='#9467bd', sport_id=hockey.id),
        Team(name='Australia Hockey', short_name='AUS', logo_color='#8c564b', sport_id=hockey.id),
        Team(name='Patna Pirates', short_name='PP', logo_color='#e377c2', sport_id=kabaddi.id),
        Team(name='U Mumba', short_name='UM', logo_color='#7f7f7f', sport_id=kabaddi.id),
        Team(name='PBL Stars', short_name='PBL', logo_color='#bcbd22', sport_id=badminton.id),
        Team(name='Smashers', short_name='SM', logo_color='#17becf', sport_id=badminton.id)
    ]
    db.session.add_all(teams)
    db.session.commit()

    # Players (some sample)
    players = [
        Player(name='Rohit Sharma', team_id=1, position='Batsman', jersey_number=45, nationality='India', matches_played=120, runs=4500, wickets=50),
        Player(name='MS Dhoni', team_id=2, position='Wicketkeeper', jersey_number=7, nationality='India', matches_played=200, runs=4800, wickets=0),
        Player(name='Cristiano Ronaldo', team_id=4, position='Forward', jersey_number=7, nationality='Portugal', matches_played=150, goals=100, assists=30),
        Player(name='Sunil Chhetri', team_id=3, position='Forward', jersey_number=11, nationality='India', matches_played=130, goals=75, assists=20),
        Player(name='Anup Kumar', team_id=7, position='Raider', jersey_number=5, nationality='India', matches_played=100, raid_points=800, tackle_points=100, points=900),
        Player(name='P.V. Sindhu', team_id=9, position='Shuttler', jersey_number=1, nationality='India', matches_played=80, smashes=200, aces=50)
    ]
    db.session.add_all(players)
    db.session.commit()

    # Matches (live, upcoming, completed)
    matches = [
        Match(sport_id=cricket.id, team1_id=1, team2_id=2, team1_score='180/3', team2_score='175/5', match_details='IPL Match 5', venue='Wankhede Stadium', match_date=datetime.now(), match_time='15:30', status='live', is_live=True),
        Match(sport_id=football.id, team1_id=3, team2_id=4, team1_score='2', team2_score='1', match_details='Friendly Match', venue='Mumbai Stadium', match_date=datetime.now()-timedelta(days=1), match_time='18:00', status='completed', is_live=False),
        Match(sport_id=hockey.id, team1_id=5, team2_id=6, team1_score='3', team2_score='3', match_details='Hockey League', venue='Delhi Stadium', match_date=datetime.now()+timedelta(days=1), match_time='16:00', status='upcoming', is_live=False),
        Match(sport_id=kabaddi.id, team1_id=7, team2_id=8, team1_score='42', team2_score='38', match_details='Pro Kabaddi', venue='Patna Arena', match_date=datetime.now(), match_time='20:00', status='live', is_live=True),
        Match(sport_id=badminton.id, team1_id=9, team2_id=10, team1_score='21-15, 19-21, 21-18', team2_score='', match_details='PBL Match', venue='Bangalore Indoor', match_date=datetime.now()+timedelta(days=2), match_time='14:00', status='upcoming', is_live=False)
    ]
    db.session.add_all(matches)
    db.session.commit()

# ---------------------- ROUTES ------------------------
@app.route('/')
def index():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')

    live_matches = Match.query.filter_by(is_live=True).all()
    upcoming_matches = Match.query.filter_by(status='upcoming').all()
    recent_matches = Match.query.filter_by(status='completed').all()

    return render_template('index.html', sports=sports, selected_sport=selected_sport,
                           live_matches=live_matches, upcoming_matches=upcoming_matches,
                           recent_matches=recent_matches)

@app.route('/players')
def players():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')
    if selected_sport == 'all':
        players = Player.query.all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        players = Player.query.join(Team).filter(Team.sport_id==sport.id).all()
    return render_template('players.html', players=players, sports=sports, selected_sport=selected_sport)

@app.route('/schedule')
def schedule():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')
    if selected_sport == 'all':
        matches = Match.query.all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        matches = Match.query.filter_by(sport_id=sport.id).all()
    return render_template('schedule.html', matches=matches, sports=sports, selected_sport=selected_sport)

@app.route('/admin')
def admin():
    sports = Sport.query.all()
    matches = Match.query.all()
    return render_template('admin.html', sports=sports, matches=matches)

# API endpoints for live scores
@app.route('/api/live-scores')
def api_live_scores():
    matches = Match.query.filter_by(is_live=True).all()
    data = []
    for m in matches:
        data.append({
            'id': m.id,
            'team1_score': m.team1_score,
            'team2_score': m.team2_score,
            'match_details': m.match_details
        })
    return jsonify(data)

# ---------------------- RUN ------------------------
if __name__ == '__main__':
    create_sample_data()
    app.run(debug=True)
