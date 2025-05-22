from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)




class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True, autoincrement = True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String, nullable=False, unique=True)

class Post(db.Model):
    id_post = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.String, nullable=False)

@app.route('/')
def redirecting():
    return redirect("/index")

@app.route('/index')
def index():
    logged_in = session.get("logged_in", False)
    posts = Post.query.order_by(Post.id_post.desc()).all()
    return render_template('index.html', logged_in=logged_in, posts=posts)

@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    logged_in = session.get("logged_in", False)
    if not logged_in:
        return redirect(url_for("login/create_post"))
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_name = session.get("user_name", None)  
        post = Post(title=title, content=content, user_name=user_name)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))
    else:
        return render_template("create_post.html")

@app.route("/login/<path:return_link>", methods=["GET", "POST"])
def login(return_link):
    error = ""
    logged_in = session.get("logged_in", False)
    if not logged_in:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            global user_name
            user_name = request.form.get("user_name")
            user = User.query.filter_by(email=email, password=password).first()
            if user:
                session["logged_in"] = True
                session["user_name"] = user.user_name
                return redirect("/" + return_link)
            else:
                error = "Invalid email or password"
                return render_template("login.html", error=error, return_link=return_link)
        else:
            return render_template("login.html", error=error, return_link=return_link)
    else:
        return redirect("/" + return_link)
    
@app.route("/test")
def test():
    user_name = "test"
    email = "test@test"
    password = "test"
    user = User(user_name=user_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return "User added"

@app.route("/dashboard")
def dashboard():
    logged_in = session.get("logged_in", False)
    if not logged_in:
        return redirect(url_for("login", return_link="dashboard"))
    user_name = session.get("user_name", None)
    posts = Post.query.filter_by(user_name=user_name).all()
    return render_template("dashboard.html", posts=posts)

@app.route("/delete_post/<int:id_post>")
def delete_post(id_post):
    logged_in = session.get("logged_in", False)
    if not logged_in:
        return redirect(url_for("login", return_link=f"delete_post/{id_post}"))
    post = Post.query.get(id_post)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/edit_post/<int:id_post>", methods=["GET", "POST"])
def edit_post(id_post):
    logged_in = session.get("logged_in", False)
    if not logged_in:
        return redirect(url_for("login", return_link=f"edit_post/{id_post}"))
    post = Post.query.get(id_post)
    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("edit_post.html", post=post)

@app.route("/registration/<path:return_link>", methods=["GET", "POST"])
def registration(return_link):
    error = ""
    logged_in = session.get("logged_in", False)
    if logged_in:
        return redirect("/" + return_link)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_name = request.form.get("user_name")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = "Email already exists"
            return render_template(f"registration.html", return_link=return_link, error=error)
        new_user = User(email=email, password=password, user_name=user_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for(return_link))
    else:
        return render_template("registration.html", return_link=return_link, error=error)
    
@app.route("/logout")
def logout():
    session.pop("logged_in", False)
    session.pop("user_name", None)
    return redirect("/index")

app.run(debug=True)
