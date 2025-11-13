# app_legit_csrf.py
from flask import Flask, request, session, redirect, render_template_string, g,  send_from_directory, render_template
import sqlite3, os, secrets

DB = "users.db"
app = Flask(__name__)
app.secret_key = "dev-secret-key"  # SOLO para pruebas locales; en prod usar secreto seguro

# --- DB helpers (reuse same DB) ---
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

# --- CSRF token helpers ---
def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]

def rotate_csrf_token():
    session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]

# --- Routes ---
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/profile")
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
            # generate csrf token on login
            get_csrf_token()
            return redirect("/profile")
        return "Credenciales inválidas", 401
    return send_from_directory('static/vulnerable', 'login.html')

@app.route("/profile", methods=["GET"])
def profile():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    r = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    token = get_csrf_token()
    # include hidden csrf token
    return render_template_string("""
      <h2>Perfil (parcheado)</h2>
      <p>Usuario: {{u}}</p>
      <p>Email actual: {{e}}</p>
      <form action="/change-email" method="POST">
        <input name="new_email" value="{{e}}">
        <input type="hidden" name="csrf_token" value="{{token}}">
        <button>Cambiar Email</button>
      </form>
      <p><a href="/logout">Logout</a></p>
    """, u=r["username"], e=r["email"], token=token)

@app.route("/change-email", methods=["POST"])
def change_email():
    if "user_id" not in session:
        return "No autenticado", 401
    sent = request.form.get("csrf_token","")
    if not sent or sent != session.get("csrf_token"):
        app.logger.warning(f"[CSRF BLOCK] token invalid. got={sent} expected={session.get('csrf_token')}")
        return "CSRF token inválido", 403
    new = request.form.get("new_email","")
    db = get_db()
    db.execute("UPDATE users SET email=? WHERE id=?", (new, session["user_id"]))
    db.commit()
    app.logger.info(f"[PATCHED] change-email called for user {session['user_id']} -> {new}")
    # optional: rotate token after successful use
    rotate_csrf_token()
    return f"Email cambiado a {new}"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---- same-origin "evil" route for demo (will be blocked by CSRF patch) ----
@app.route("/evil", methods=["GET"])
def evil_page():
    return '''
    <!doctype html>
    <html>
    <head><meta charset="utf-8"><title>evil same-origin demo</title></head>
    <body>
      <h3>evil (same-origin demo)</h3>
      <p>Esta página se sirve desde el mismo host/puerto que la app legítima.</p>
      <form id="f" action="/change-email" method="POST">
        <input name="new_email" value="evil@attacker.com">
      </form>
      <script>
        document.addEventListener('DOMContentLoaded', function() {
          var form = document.getElementById('f');
          if (form) form.submit();
        });
      </script>
    </body>
    </html>
    '''

if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
