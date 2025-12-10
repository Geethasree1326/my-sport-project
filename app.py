import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ---------------------- FIXED DATABASE ------------------------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sports-management-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sports.db'   # LOCAL SQLITE DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------- MODELS ------------------------
class Sport(db.Model):
    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(50))
    scoring_type = db.Column(db.String(50))
    matches = db.relationship('Match', backref='sport', lazy=True)
    teams = db.relationship('Team', backref='sport_rel', lazy=True)


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    logo_color = db.Column(db.String(20), default='#3498db')
    players = db.relationship('Player', backref='team', lazy=True)


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    position = db.Column(db.String(50))
    jersey_number = db.Column(db.Integer)
    nationality = db.Column(db.String(50))
    matches_played = db.Column(db.Integer, default=0)
    runs = db.Column(db.Integer, default=0)
    wickets = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    raid_points = db.Column(db.Integer, default=0)
    tackle_points = db.Column(db.Integer, default=0)
    smashes = db.Column(db.Integer, default=0)
    aces = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team1_score = db.Column(db.String(50), default='0')
    team2_score = db.Column(db.String(50), default='0')
    match_details = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    match_date = db.Column(db.DateTime, default=datetime.utcnow)
    match_time = db.Column(db.String(20))
    status = db.Column(db.String(20), default='upcoming')
    is_live = db.Column(db.Boolean, default=False)
    tournament = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])


# ---------------------- ROUTES ------------------------
@app.route('/')
def index():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')

    if selected_sport == 'all':
        live_matches = Match.query.filter_by(is_live=True).all()
        recent_matches = Match.query.filter_by(status='completed').order_by(Match.updated_at.desc()).limit(6).all()
        upcoming_matches = Match.query.filter_by(status='upcoming').order_by(Match.match_date).limit(6).all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        if sport:
            live_matches = Match.query.filter_by(sport_id=sport.id, is_live=True).all()
            recent_matches = Match.query.filter_by(sport_id=sport.id, status='completed').order_by(Match.updated_at.desc()).limit(6).all()
            upcoming_matches = Match.query.filter_by(sport_id=sport.id, status='upcoming').order_by(Match.match_date).limit(6).all()
        else:
            live_matches = []
            recent_matches = []
            upcoming_matches = []

    return render_template('index.html',
                           sports=sports,
                           selected_sport=selected_sport,
                           live_matches=live_matches,
                           recent_matches=recent_matches,
                           upcoming_matches=upcoming_matches)


@app.route('/players')
def players():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')

    if selected_sport == 'all':
        all_players = Player.query.all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        if sport:
            team_ids = [t.id for t in Team.query.filter_by(sport_id=sport.id)]
            all_players = Player.query.filter(Player.team_id.in_(team_ids)).all()
        else:
            all_players = []

    return render_template('players.html',
                           sports=sports,
                           players=all_players,
                           selected_sport=selected_sport)


@app.route('/schedule')
def schedule():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')

    if selected_sport == 'all':
        all_matches = Match.query.order_by(Match.match_date).all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        all_matches = Match.query.filter_by(sport_id=sport.id).order_by(Match.match_date).all() if sport else []

    return render_template('schedule.html',
                           sports=sports,
                           matches=all_matches,
                           selected_sport=selected_sport)


@app.route('/admin')
def admin():
    sports = Sport.query.all()
    teams = Team.query.all()
    matches = Match.query.order_by(Match.created_at.desc()).all()
    players = Player.query.all()
    return render_template('admin.html',
                           sports=sports,
                           teams=teams,
                           matches=matches,
                           players=players)


# ---------------------- API ------------------------
@app.route('/api/matches')
def get_matches():
    matches = Match.query.all()
    result = [
        {
            'id': m.id,
            'sport': m.sport.name,
            'team1': m.team1.name,
            'team2': m.team2.name,
            'team1_score': m.team1_score,
            'team2_score': m.team2_score,
            'status': m.status,
            'is_live': m.is_live,
            'venue': m.venue,
            'match_details': m.match_details,
            'match_date': m.match_date.isoformat(),
            'match_time': m.match_time,
            'tournament': m.tournament
        }
        for m in matches
    ]
    return jsonify(result)


@app.route('/api/matches/<int:match_id>')
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    return jsonify({
        'id': match.id,
        'sport': match.sport.name,
        'team1': match.team1.name,
        'team2': match.team2.name,
        'team1_score': match.team1_score,
        'team2_score': match.team2_score,
        'status': match.status,
        'is_live': match.is_live
    })


# ---------------------- INITIALIZE DB ------------------------
with app.app_context():
    db.create_all()   # No sample data function


# ---------------------- RUN ------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
