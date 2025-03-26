import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
app = Flask(__name__)
app.jinja_env.filters["usd"] = usd
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///project.db")
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
@app.route("/")
@login_required
def inbox():
    userId = session["user_id"]
    usernameDB = db.execute("SELECT username FROM users WHERE id = ?", userId)
    username = usernameDB[0]["username"]
    emails = db.execute("SELECT * FROM emails WHERE recipient = ?", username)
    return render_template("index.html", emails = emails)
@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    if request.method == "GET":
        user_Id = session["user_id"]
        senderDB = db.execute("SELECT username FROM users WHERE id = ?", user_Id)
        sender = senderDB[0]["username"]
        return render_template("compose.html", sender = sender)
    else:
        sender = request.form.get("sender")
        recipient = request.form.get("recipient")
        subject = request.form.get("subject")
        body = request.form.get("body")
        file = request.form.get("file")
        if not sender or not recipient or not subject or not body:
            return apology("No Empty Fields")
        db.execute("INSERT INTO emails (sender, recipient, subject, body, file) VALUES (?, ?, ?, ?, ?)", sender, recipient, subject, body, file)
        return redirect("/sent")
@app.route("/sent")
@login_required
def sent():
    userId = session["user_id"]
    usernameDB = db.execute("SELECT username FROM users WHERE id = ?", userId)
    username = usernameDB[0]["username"]
    emails = db.execute("SELECT * FROM emails WHERE sender = ?", username)
    return render_template("index.html", emails = emails)
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
@app.route("/email", methods=["POST"])
@login_required
def email():
    if request.method == "POST":
        emailId = request.form.get("emailId")
        emailDetailDB = db.execute("SELECT * FROM emails WHERE id = ?", emailId)
        emailDetail = emailDetailDB[0]
        return render_template("email.html", emailDetail = emailDetail)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not email or not password or not confirm:
            return apology("No Empty Fields")
        if password != confirm:
            return apology("Passwords Do Not Match")
        if len(password) < 8:
            return apology("password must be at least 8 characters")
        hash = generate_password_hash(password)
        try:
            newUser = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", email, hash)
        except:
            return apology("Username Already Taken")
        session["user_id"] = newUser
        return redirect("/")
@app.route("/reply", methods=["POST"])
@login_required
def reply():
    if request.method == "POST":
        userId = session["user_id"]
        usernameDB = db.execute("SELECT username FROM users WHERE id = ?", userId)
        username = usernameDB[0]["username"]
        emailDetails = db.execute("SELECT * FROM emails WHERE recipient = ?", username)
        return render_template("reply.html", emailDetails = emailDetails)
