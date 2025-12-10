from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# ----- Sports -----
sports = [
    {"id": 1, "name": "Cricket"},
    {"id": 2, "name": "Football"},
    {"id": 3, "name": "Kabaddi"}
]

# ----- Teams -----
teams = {
    1: [  # Cricket IPL teams
        {"id": 1, "name": "Chennai Super Kings", "short_name": "CSK", "logo_color": "#f4c430"},
        {"id": 2, "name": "Mumbai Indians", "short_name": "MI", "logo_color": "#1e90ff"},
        {"id": 3, "name": "Royal Challengers Bangalore", "short_name": "RCB", "logo_color": "#ff0000"},
        {"id": 4, "name": "Kolkata Knight Riders", "short_name": "KKR", "logo_color": "#4b0082"},
    ],
    2: [  # Football ISL teams
        {"id": 5, "name": "Bengaluru FC", "short_name": "BFC", "logo_color": "#00bfff"},
        {"id": 6, "name": "ATK Mohun Bagan", "short_name": "ATKMB", "logo_color": "#228b22"},
    ],
    3: [  # Kabaddi teams
        {"id": 7, "name": "Jaipur Pink Panthers", "short_name": "JPP", "logo_color": "#ff69b4"},
        {"id": 8, "name": "Patna Pirates", "short_name": "PP", "logo_color": "#ff8c00"},
    ],
}

# ----- Matches -----
matches = [
    # Cricket
    {
        "id": 1,
        "sport": sports[0],
        "team1": teams[1][0],
        "team2": teams[1][1],
        "team1_score": "185/4",
        "team2_score": "142/6",
        "match_date": datetime.now(),
        "match_time": "19:30",
        "status": "live",
        "is_live": True,
        "tournament": "IPL 2025",
        "venue": "M.A. Chidambaram Stadium",
        "match_details": "Match 7, Semi-Final"
    },
    {
        "id": 2,
        "sport": sports[0],
        "team1": teams[1][2],
        "team2": teams[1][3],
        "team1_score": "210/6",
        "team2_score": "198/7",
        "match_date": datetime.now() + timedelta(days=1),
        "match_time": "16:00",
        "status": "upcoming",
        "is_live": False,
        "tournament": "IPL 2025",
        "venue": "M. Chinnaswamy Stadium",
        "match_details": "Match 8"
    },
    # Football
    {
        "id": 3,
        "sport": sports[1],
        "team1": teams[2][0],
        "team2": teams[2][1],
        "team1_score": "2",
        "team2_score": "1",
        "match_date": datetime.now(),
        "match_time": "18:00",
        "status": "completed",
        "is_live": False,
        "tournament": "Indian Super League",
        "venue": "Sree Kanteerava Stadium",
        "match_details": "Semi-Final"
    },
    # Kabaddi
    {
        "id": 4,
        "sport": sports[2],
        "team1": teams[3][0],
        "team2": teams[3][1],
        "team1_score": "35",
        "team2_score": "28",
        "match_date": datetime.now() + timedelta(days=2),
        "match_time": "20:00",
        "status": "upcoming",
        "is_live": False,
        "tournament": "Pro Kabaddi League",
        "venue": "Sawai Mansingh Stadium",
        "match_details": "Match 12"
    },
]

# ----- Players -----
players = [
    # Cricket players
    {"name": "MS Dhoni", "team": "CSK", "jersey": 7, "position": "Batsman", "nationality": "India", "sport": "Cricket", "runs": 478, "wickets": 0, "matches": 7},
    {"name": "Rohit Sharma", "team": "MI", "jersey": 45, "position": "Batsman", "nationality": "India", "sport": "Cricket", "runs": 512, "wickets": 0, "matches": 7},
    # Football players
    {"name": "Sunil Chhetri", "team": "BFC", "jersey": 11, "position": "Forward", "nationality": "India", "sport": "Football", "goals": 6, "assists": 2, "matches": 5},
    {"name": "Roy Krishna", "team": "ATKMB", "jersey": 9, "position": "Forward", "nationality": "Fiji", "sport": "Football", "goals": 5, "assists": 3, "matches": 5},
]

# ----------------- ROUTES -----------------

@app.route("/")
def index():
    live_matches = [m for m in matches if m["is_live"]]
    return render_template("index.html", matches=live_matches, sports=sports)

@app.route("/schedule")
def schedule():
    sport_filter = request.args.get("sport", "all")
    if sport_filter != "all":
        filtered = [m for m in matches if m["sport"]["name"] == sport_filter]
    else:
        filtered = matches
    return render_template("schedule.html", matches=filtered, sports=sports, selected_sport=sport_filter)

@app.route("/players")
def player_stats():
    return render_template("players.html", players=players)

@app.route("/admin")
def admin_panel():
    return render_template("admin.html", matches=matches, sports=sports)

# ----- API for teams -----
@app.route("/api/teams/<int:sport_id>")
def api_teams(sport_id):
    return jsonify(teams.get(sport_id, []))

# ----- API to create/update/delete match (dummy) -----
@app.route("/api/matches", methods=["POST"])
def create_match():
    return jsonify({"success": True})

@app.route("/api/matches/<int:match_id>")
def get_match(match_id):
    match = next((m for m in matches if m["id"] == match_id), None)
    return jsonify(match)

@app.route("/api/matches/<int:match_id>/score", methods=["PUT"])
def update_score(match_id):
    return jsonify({"success": True})

@app.route("/api/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
