import os
import secrets

from flask import Flask,request,redirect,render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(80),unique=True, nullable=False)
    password = db.Column(db.String(120),nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean,default=False,nullable=False)   
    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id"),
                        nullable=False)
    priority = db.Column(db.Integer,default=2,nullable=False)

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            user =User(
                username = username,
                password = generate_password_hash(password) 
                )
            db.session.add(user)
            db.session.commit()
            
            flash("登録しました")
            return redirect("/login")
        
        else:
            flash("ユーザーは存在します")
            return redirect("/register")
    
    return render_template("register.html")

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        username =request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password,password):
            session["user_id"] = user.id
        
            flash("ログインしました")
            return redirect("/mypage")
        
        flash("ユーザー名またはパスワードが間違っています")
        return redirect("/login")
    
    return render_template("login.html")

@app.route("/mypage")
def mypage():
    if "user_id" not in session:
        return redirect("/login")

    user  = User.query.filter_by(id=session["user_id"]).first()

    keyword =request.args.get("keyword","")

    if keyword:
        todos = Todo.query.filter(
            Todo.user_id == session["user_id"],
            Todo.title.contains(keyword)
        ).order_by(Todo.completed,
                   Todo.priority.desc(),
                   Todo.created_at.desc()
                  ).all()
    
    else:
        todos = Todo.query.filter_by(user_id = session["user_id"]).order_by(Todo.completed,
                                                                            Todo.priority.desc(),
                                                                            Todo.created_at.desc()).all()

    return render_template("mypage.html",user=user,todos=todos,keyword=keyword)

@app.route("/todo/add",methods = ["POST"])
def todo_add():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title","").strip()

    print("タイトル:",repr(title))

    if not title:
        flash("タイトルがないです")
        return redirect("/mypage")

    priority = int(request.form.get("priority",2))

    todo = Todo(
        priority=priority,
        title = title ,
        user_id = session["user_id"]
    )

    db.session.add(todo)
    db.session.commit()

    return redirect("/mypage")

@app.route("/todo/<int:todo_id>/toggle", methods=["POST"])
def todo_toggle(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    todo = Todo.query.filter_by(
        id = todo_id ,
        user_id = session["user_id"]
    ).first()

    if not todo:
        return redirect("/mypage")

    todo.completed = not todo.completed

    db.session.commit()

    return redirect("/mypage")

@app.route("/todo/<int:todo_id>/delete",methods=["POST"])
def todo_delete(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    
    todo = Todo.query.filter_by(
        id = todo_id ,
        user_id = session["user_id"]
    ).first()

    if not todo:
        return redirect("/mypage") 

    db.session.delete(todo)
    db.session.commit()

    flash("削除しました。","success")

    return redirect("/mypage")

@app.route("/todo/<int:todo_id>/edit",methods=["POST","GET"])
def todo_edit(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    todo = Todo.query.filter_by(
        id = todo_id,
        user_id = session["user_id"]
    ).first()

    if not todo :
        return redirect("/mypage")


    if request.method == "POST":
        todo.title = request.form.get("title")
        db.session.commit()

        return redirect("/mypage")

    return render_template("todo_edit.html",todo=todo)

@app.route("/logout")
def logout():
    session.pop("user_id",None)

    return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   
        
    app.run(debug=False)