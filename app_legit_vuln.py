# app_legit_vuln.py
from flask import Flask, request, session, redirect, render_template_string, g, send_from_directory
import sqlite3
import os

DB = "users.db"
app = Flask(__name__)
app.secret_key = "dev-secret-key"  # SOLO para pruebas locales; en prod usar secreto seguro

# --- DB helpers ---
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    if os.path.exists(DB):
        return
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("""CREATE TABLE users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT UNIQUE,
                   password TEXT,
                   email TEXT
                 )""")
    c.execute("INSERT INTO users (username,password,email) VALUES (?,?,?)",
              ("alice","password","alice@example.com"))
    db.commit()
    db.close()

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

# --- Routes ---
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/inicio")
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username","")
        pw = request.form.get("password","")
        db = get_db()
        r = db.execute("SELECT * FROM users WHERE username=? AND password=?", (user,pw)).fetchone()
        if r:
            session["user_id"] = r["id"]
            return redirect("/")
        return send_from_directory('static/vulnerable','error.html')
    return send_from_directory('static/vulnerable','login.html')


@app.route("/inicio", methods=["GET"])
def inicio():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    r = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return send_from_directory('static/vulnerable','inicio.html')

@app.route("/cuenta", methods=["GET"])
def cuenta():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    r = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return send_from_directory('static/vulnerable','cuenta.html')

@app.route("/change-email", methods=["POST"])
def change_email():
    # VULNERABLE: no valida token CSRF
    if "user_id" not in session:
        return "No autenticado", 401
    new = request.form.get("new_email","")
    db = get_db()
    db.execute("UPDATE users SET email=? WHERE id=?", (new, session["user_id"]))
    db.commit()
    app.logger.info(f"[VULN] change-email called for user {session['user_id']} -> {new}")
    return f"Email cambiado a {new}"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---- Demo same-origin "maliciosa" (solo para laboratorio local) ----
@app.route("/evil", methods=["GET"])
def evil_page():
    return send_from_directory('static','evil.html')

if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
