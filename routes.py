from flask import request,redirect,url_for,render_template,session
from werkzeug.security import generate_password_hash,check_password_hash
from models import db,User

def init_routes(app):

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
            # フォームから送信されたログイン情報を取得
            username = request.form.get("username")
            password = request.form.get("password")

            # 入力されたユーザー名でデータベースを検索
            user = User.query.filter_by(username=username).first()

            #　ユーザーが存在しない場合
            if not user:
                error = "存在しないユーザーです"
        
            #　パスワードの検証(ハッシュ化された値と比較)
            elif not check_password_hash(user.password,password):
                error = "パスワード間違いました"
            
            else:
                #　ログイン成功時、ユーザーIDをセッションに保存
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
