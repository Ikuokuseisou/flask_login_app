from flask import Flask,request,redirect,url_for,render_template,session
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)

@app.route("/register",methods =["GET","POST"])
def register():
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        user = User(username = username , password = hashed_password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods = ["GET","POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user:
            error = "存在しないユーザーです"
        
        elif not check_password_hash(user.password,password):
            error = "パスワード間違いました"
            
        else:
            session["user_id"] = user.id
            return redirect(url_for("index"))
   
    
    return render_template("login.html") 

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    
    return render_template("index.html", user = user)

@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)