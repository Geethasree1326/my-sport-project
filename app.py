from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------- Models -------------------

class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    teams = db.relationship('Team', backref='sport', lazy=True)
    matches = db.relationship('Match', backref='sport', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    players = db.relationship('Player', backref='team', lazy=True)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport_id = db.Column(db.Integer, db.ForeignKey('sport.id'), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team1_score = db.Column(db.String(20), default='')
    team2_score = db.Column(db.String(20), default='')
    match_details = db.Column(db.String(100))
    status = db.Column(db.String(20), default='upcoming')
    venue = db.Column(db.String(100))
    is_live = db.Column(db.Boolean, default=False)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    position = db.Column(db.String(20))
    nationality = db.Column(db.String(30))
    matches_played = db.Column(db.Integer, default=0)
    runs_scored = db.Column(db.Integer, default=0)
    wickets_taken = db.Column(db.Integer, default=0)

# ------------------- Sample Data -------------------

def create_sample_data():
    db.drop_all()
    db.create_all()

    # Sports
    cricket = Sport(name='Cricket')
    football = Sport(name='Football')
    db.session.add_all([cricket, football])
    db.session.commit()

    # Teams
    team1 = Team(name='Mumbai Indians', sport=cricket)
    team2 = Team(name='Chennai Super Kings', sport=cricket)
    team3 = Team(name='Manchester United', sport=football)
    team4 = Team(name='Liverpool', sport=football)
    db.session.add_all([team1, team2, team3, team4])
    db.session.commit()

    # Players
    players = [
        Player(name='Rohit Sharma', team=team1, position='Batsman', nationality='India', matches_played=200, runs_scored=9200),
        Player(name='Jasprit Bumrah', team=team1, position='Bowler', nationality='India', matches_played=100, wickets_taken=150),
        Player(name='MS Dhoni', team=team2, position='Wicketkeeper', nationality='India', matches_played=350, runs_scored=10500),
        Player(name='Cristiano Ronaldo', team=team3, position='Forward', nationality='Portugal', matches_played=500, runs_scored=700),
        Player(name='Mohamed Salah', team=team4, position='Forward', nationality='Egypt', matches_played=300, runs_scored=450)
    ]
    db.session.add_all(players)
    db.session.commit()

    # Matches
    match1 = Match(
        sport=cricket, team1=team1, team2=team2, team1_score='185/4', team2_score='142/6',
        match_details='IPL Match 1, Semi-Final', status='live', venue='Wankhede Stadium', is_live=True
    )
    match2 = Match(
        sport=football, team1=team3, team2=team4, team1_score='2', team2_score='1',
        match_details='Premier League Match', status='completed', venue='Old Trafford'
    )
    db.session.add_all([match1, match2])
    db.session.commit()

# ------------------- Routes -------------------

@app.route('/')
def index():
    sports = Sport.query.all()
    matches = Match.query.all()
    return render_template('index.html', sports=sports, matches=matches)

@app.route('/players')
def players_page():
    players = Player.query.all()
    return render_template('player.html', players=players)

@app.route('/schedule')
def schedule_page():
    matches = Match.query.order_by(Match.id).all()
    return render_template('schedule.html', matches=matches)

@app.route('/admin')
def admin_page():
    sports = Sport.query.all()
    matches = Match.query.all()
    return render_template('admin.html', sports=sports, matches=matches)

# ------------------- API Routes -------------------

@app.route('/api/teams/<int:sport_id>')
def get_teams(sport_id):
    teams = Team.query.filter_by(sport_id=sport_id).all()
    return jsonify([{'id': t.id, 'name': t.name} for t in teams])

@app.route('/api/matches', methods=['POST'])
def create_match():
    data = request.get_json()
    match = Match(
        sport_id=data['sport_id'],
        team1_id=data['team1_id'],
        team2_id=data['team2_id'],
        venue=data.get('venue'),
        match_details=data.get('match_details'),
        status=data.get('status', 'upcoming'),
        is_live=data.get('is_live', False)
    )
    db.session.add(match)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/matches/<int:match_id>')
def get_match(match_id):
    match = Match.query.get(match_id)
    return jsonify({
        'id': match.id,
        'team1': match.team1.name,
        'team2': match.team2.name,
        'team1_score': match.team1_score,
        'team2_score': match.team2_score,
        'match_details': match.match_details,
        'status': match.status
    })

@app.route('/api/matches/<int:match_id>/score', methods=['PUT'])
def update_score(match_id):
    data = request.get_json()
    match = Match.query.get(match_id)
    match.team1_score = data.get('team1_score', match.team1_score)
    match.team2_score = data.get('team2_score', match.team2_score)
    match.match_details = data.get('match_details', match.match_details)
    match.status = data.get('status', match.status)
    match.is_live = match.status == 'live'
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    match = Match.query.get(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({'success': True})

# ------------------- Run App -------------------

if __name__ == '__main__':
    with app.app_context():
        create_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
