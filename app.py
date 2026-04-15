from flask import Flask
from flask_cors import CORS
from routes.groups import groups_bp
from routes.goals import goals_bp
from routes.nudges import nudges_bp

app = Flask(__name__)
CORS(app)

# Register route blueprints
app.register_blueprint(groups_bp, url_prefix="/groups")
app.register_blueprint(goals_bp, url_prefix="/goals")
app.register_blueprint(nudges_bp, url_prefix="/nudges")

@app.route("/")
def health():
    return {"status": "Catch backend running ✓"}, 200

if __name__ == "__main__":
    app.run(debug=True)
