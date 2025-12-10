import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sports-management-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Sport(db.Model):
    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(50))
    scoring_type = db.Column(db.String(50))
    matches = db.relationship('Match', backref='sport', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    logo_color = db.Column(db.String(20), default='#3498db')
    sport = db.relationship('Sport', backref='teams')

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
    team = db.relationship('Team', backref='players')

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

# Routes
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
            live_matches, recent_matches, upcoming_matches = [], [], []
    
    return render_template('index.html', sports=sports, selected_sport=selected_sport,
                         live_matches=live_matches, recent_matches=recent_matches,
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
            team_ids = [t.id for t in Team.query.filter_by(sport_id=sport.id).all()]
            all_players = Player.query.filter(Player.team_id.in_(team_ids)).all()
        else:
            all_players = []
    
    return render_template('players.html', sports=sports, players=all_players, selected_sport=selected_sport)

@app.route('/schedule')
def schedule():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')
    
    if selected_sport == 'all':
        all_matches = Match.query.order_by(Match.match_date).all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        if sport:
            all_matches = Match.query.filter_by(sport_id=sport.id).order_by(Match.match_date).all()
        else:
            all_matches = []
    
    return render_template('schedule.html', sports=sports, matches=all_matches, selected_sport=selected_sport)

@app.route('/admin')
def admin():
    sports = Sport.query.all()
    teams = Team.query.all()
    matches = Match.query.order_by(Match.created_at.desc()).all()
    players = Player.query.all()
    return render_template('admin.html', sports=sports, teams=teams, matches=matches, players=players)

# API Endpoints
@app.route('/api/matches', methods=['GET'])
def get_matches():
    matches = Match.query.all()
    result = []
    for match in matches:
        result.append({
            'id': match.id,
            'sport': match.sport.name,
            'team1': match.team1.name,
            'team2': match.team2.name,
            'team1_score': match.team1_score,
            'team2_score': match.team2_score,
            'status': match.status,
            'is_live': match.is_live,
            'venue': match.venue,
            'match_details': match.match_details,
            'match_date': match.match_date.isoformat() if match.match_date else None,
            'match_time': match.match_time,
            'tournament': match.tournament
        })
    return jsonify(result)

@app.route('/api/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    return jsonify({
        'id': match.id,
        'sport_id': match.sport_id,
        'sport': match.sport.name,
        'team1_id': match.team1_id,
        'team2_id': match.team2_id,
        'team1': match.team1.name,
        'team2': match.team2.name,
        'team1_score': match.team1_score,
        'team2_score': match.team2_score,
        'status': match.status,
        'is_live': match.is_live,
        'venue': match.venue,
        'match_details': match.match_details,
        'match_date': match.match_date.isoformat() if match.match_date else None,
        'match_time': match.match_time,
        'tournament': match.tournament
    })

@app.route('/api/matches', methods=['POST'])
def create_match():
    data = request.json
    match_date = datetime.fromisoformat(data['match_date']) if data.get('match_date') else datetime.utcnow()
    match = Match(
        sport_id=data['sport_id'],
        team1_id=data['team1_id'],
        team2_id=data['team2_id'],
        venue=data.get('venue', ''),
        match_details=data.get('match_details', ''),
        status=data.get('status', 'upcoming'),
        is_live=data.get('is_live', False),
        match_date=match_date,
        match_time=data.get('match_time', ''),
        tournament=data.get('tournament', '')
    )
    db.session.add(match)
    db.session.commit()
    return jsonify({'success': True, 'id': match.id})

@app.route('/api/matches/<int:match_id>/score', methods=['PUT'])
def update_score(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.json
    
    if 'team1_score' in data:
        match.team1_score = data['team1_score']
    if 'team2_score' in data:
        match.team2_score = data['team2_score']
    if 'status' in data:
        match.status = data['status']
        match.is_live = (data['status'] == 'live')
    if 'match_details' in data:
        match.match_details = data['match_details']
    
    match.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/live-scores')
def live_scores():
    live_matches = Match.query.filter_by(is_live=True).all()
    result = []
    for match in live_matches:
        result.append({
            'id': match.id,
            'sport': match.sport.name,
            'team1': match.team1.name,
            'team1_short': match.team1.short_name,
            'team2': match.team2.name,
            'team2_short': match.team2.short_name,
            'team1_score': match.team1_score,
            'team2_score': match.team2_score,
            'match_details': match.match_details
        })
    return jsonify(result)

@app.route('/api/teams/<int:sport_id>')
def get_teams(sport_id):
    teams = Team.query.filter_by(sport_id=sport_id).all()
    return jsonify([{'id': t.id, 'name': t.name, 'short_name': t.short_name} for t in teams])

with app.app_context():
    db.create_all()
    init_sample_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
