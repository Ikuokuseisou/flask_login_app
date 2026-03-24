from flask import Flask
from models import  db
from routes import init_routes
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db.init_app(app)

init_routes(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)