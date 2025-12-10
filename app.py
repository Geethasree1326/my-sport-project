from datetime import timedelta, datetime

@app.route('/')
def index():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')

    now = datetime.utcnow()

    def get_live_status(match):
        match_start = match.match_date
        match_end = match.match_date + timedelta(hours=3)  # adjust duration as needed
        if match_start <= now <= match_end:
            return True, 'live'
        elif now > match_end:
            return False, 'completed'
        else:
            return False, 'upcoming'

    # Get matches depending on sport selection
    if selected_sport == 'all':
        all_matches = Match.query.all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        all_matches = Match.query.filter_by(sport_id=sport.id).all() if sport else []

    live_matches, recent_matches, upcoming_matches = [], [], []

    for m in all_matches:
        is_live, status = get_live_status(m)
        m.is_live = is_live  # dynamic
        m.status = status    # dynamic
        if is_live:
            live_matches.append(m)
        elif status == 'completed':
            recent_matches.append(m)
        else:
            upcoming_matches.append(m)

    recent_matches = sorted(recent_matches, key=lambda x: x.updated_at, reverse=True)[:6]
    upcoming_matches = sorted(upcoming_matches, key=lambda x: x.match_date)[:6]

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
    now = datetime.utcnow()

    def get_live_status(match):
        match_start = match.match_date
        match_end = match.match_date + timedelta(hours=3)
        if match_start <= now <= match_end:
            return True, 'live'
        elif now > match_end:
            return False, 'completed'
        else:
            return False, 'upcoming'

    if selected_sport == 'all':
        all_players = Player.query.all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        if sport:
            team_ids = [t.id for t in Team.query.filter_by(sport_id=sport.id)]
            all_players = Player.query.filter(Player.team_id.in_(team_ids)).all()
        else:
            all_players = []

    # Optionally, attach live match info to players if needed
    for player in all_players:
        player_matches = Match.query.filter(
            ((Match.team1_id == player.team_id) | (Match.team2_id == player.team_id))
        ).all()
        player.live_matches = [m for m in player_matches if get_live_status(m)[0]]

    return render_template('players.html',
                           sports=sports,
                           players=all_players,
                           selected_sport=selected_sport)


@app.route('/schedule')
def schedule():
    sports = Sport.query.all()
    selected_sport = request.args.get('sport', 'all')
    now = datetime.utcnow()

    def get_live_status(match):
        match_start = match.match_date
        match_end = match.match_date + timedelta(hours=3)
        if match_start <= now <= match_end:
            return True, 'live'
        elif now > match_end:
            return False, 'completed'
        else:
            return False, 'upcoming'

    if selected_sport == 'all':
        all_matches = Match.query.order_by(Match.match_date).all()
    else:
        sport = Sport.query.filter_by(name=selected_sport).first()
        all_matches = Match.query.filter_by(sport_id=sport.id).order_by(Match.match_date).all() if sport else []

    # Update status dynamically
    for m in all_matches:
        is_live, status = get_live_status(m)
        m.is_live = is_live
        m.status = status

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
    now = datetime.utcnow()

    def get_live_status(match):
        match_start = match.match_date
        match_end = match.match_date + timedelta(hours=3)
        if match_start <= now <= match_end:
            return True, 'live'
        elif now > match_end:
            return False, 'completed'
        else:
            return False, 'upcoming'

    # Update matches dynamically
    for m in matches:
        m.is_live, m.status = get_live_status(m)

    return render_template('admin.html',
                           sports=sports,
                           teams=teams,
                           matches=matches,
                           players=players)


# ---------------------- API ------------------------
@app.route('/api/matches')
def get_matches():
    now = datetime.utcnow()
    matches = Match.query.all()
    result = []

    def get_live_status(match):
        match_start = match.match_date
        match_end = match.match_date + timedelta(hours=3)
        if match_start <= now <= match_end:
            return True, 'live'
        elif now > match_end:
            return False, 'completed'
        else:
            return False, 'upcoming'

    for m in matches:
        is_live, status = get_live_status(m)
        result.append({
            'id': m.id,
            'sport': m.sport.name,
            'team1': m.team1.name,
            'team2': m.team2.name,
            'team1_score': m.team1_score,
            'team2_score': m.team2_score,
            'status': status,
            'is_live': is_live,
            'venue': m.venue,
            'match_details': m.match_details,
            'match_date': m.match_date.isoformat(),
            'match_time': m.match_time,
            'tournament': m.tournament
        })

    return jsonify(result)
