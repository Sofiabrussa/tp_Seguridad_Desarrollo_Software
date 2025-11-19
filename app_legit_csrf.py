# app_legit_csrf.py
from flask import Flask, request, session, redirect, g, send_from_directory, render_template
import sqlite3
import os
import secrets

DB = "users.db"
app = Flask(__name__)
app.secret_key = "dev-secret-key" 

# --- BASE DE DATOS ---
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

def init_db():
    if os.path.exists(DB):
        return
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
        """
    )
    c.execute(
        "INSERT INTO users (username, password, email) VALUES (?,?,?)",
        ("alice", "password", "alice@example.com"),
    )
    db.commit()
    db.close()

# --- Generar token CSRF ---
def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]

def rotate_csrf_token():
    session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]

# --- Rutas ---
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/inicio")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username", "")
        pw = request.form.get("password", "")
        db = get_db()
        r = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pw)
        ).fetchone()
        if r:
            session["user_id"] = r["id"]
            # genera token CSRF al loguear
            get_csrf_token()
            return redirect("/inicio")
        return send_from_directory("static/vulnerable", "error.html")
    return send_from_directory("static/vulnerable", "login.html")

@app.route("/inicio", methods=["GET"])
def inicio():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return send_from_directory("static/vulnerable", "inicio.html")

@app.route("/cuenta", methods=["GET"])
def cuenta():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    r = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    token = get_csrf_token()

    #Flask envía toda la información al front, incluyendo el token CSRF 
    return render_template(
        "cuenta.html",
        email=r["email"],
        username=r["username"],
        csrf_token=token,
    )

@app.route("/change-email", methods=["POST"])
def change_email():
    if "user_id" not in session:
        return "No autenticado", 401

    sent = request.form.get("csrf_token", "") #Obtener el token que mandó el formulario
    expected = session.get("csrf_token") #Obtener el token verdadero de la sesión

    if not sent or sent != expected:
        app.logger.warning(
            f"[CSRF BLOCK] token inválido. got={sent} expected={expected}"
        )
        return "CSRF token inválido", 403

    new = request.form.get("new_email", "")
    db = get_db()
    db.execute(
        "UPDATE users SET email=? WHERE id=?",
        (new, session["user_id"])
    )
    db.commit()
    app.logger.info(
        f"[PATCHED] change-email called for user {session['user_id']} -> {new}"
    )

    rotate_csrf_token()

    return f"Email cambiado a {new}"

@app.route("/logout")
def logout():
    session.clear()
    resp = redirect("/login")
    # Limpia cookie de sesión 
    resp.set_cookie("session", "", expires=0)
    return resp

# ---- maliciosa ----
@app.route("/evil", methods=["GET"])
def evil_page():
    return send_from_directory('static', 'evil.html')

if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True) 
