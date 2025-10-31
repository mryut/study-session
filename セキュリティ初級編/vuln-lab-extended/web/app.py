
from flask import Flask, request, g, render_template_string, redirect, url_for, session
import sqlite3
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_in_production")

DB_PATH = "data/app.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Home - links to modules
@app.route('/')
def index():
    return """
    <h2>Vuln Lab (Minimal)</h2>
    <ul>
      <li><a href="/module_sql">SQL Injection (vulnerable)</a> | <a href="/module_sql/secure">secure</a></li>
      <li><a href="/module_xss">Reflected XSS (vulnerable)</a> | <a href="/module_xss/secure">secure</a></li>
      <li><a href="/admin">Admin page (no auth)</a> | <a href="/admin/secure">secure</a></li>
      <li><a href="/module_ssrf">SSRF demo (vulnerable)</a> | <a href="/module_ssrf/secure">secure</a></li>
    </ul>
    <p>Note: This environment is for local learning only.</p>
    """

# --- SQLi vulnerable route ---
@app.route('/module_sql', methods=['GET','POST'])
def module_sql():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name','')
        # vulnerable: direct string interpolation into SQL
        query = "SELECT id, name, email FROM users WHERE name = '%s';" % (name)
        try:
            rows = c.execute(query).fetchall()
        except Exception as e:
            rows = [("ERROR", str(e))]
        out = "<h3>検索 - 脆弱版</h3>"
        out += '<form method="post">名前: <input name="name"><input type="submit" value="検索"></form>'
        out += "<pre>%s</pre>" % (rows,)
        return out
    return """
    <h3>検索 - 脆弱版</h3>
    <form method="post">名前: <input name="name"><input type="submit" value="検索"></form>
    """

# --- SQLi secure route ---
@app.route('/module_sql/secure', methods=['GET','POST'])
def module_sql_secure():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name','')
        # secure: parameterized query
        rows = c.execute("SELECT id, name, email FROM users WHERE name = ?;", (name,)).fetchall()
        return "<h3>検索 - 対策版</h3><form method='post'>名前: <input name='name'><input type='submit' value='検索'></form><pre>%s</pre>" % (rows,)
    return "<h3>検索 - 対策版</h3><form method='post'>名前: <input name='name'><input type='submit' value='検索'></form>"

# --- XSS vulnerable route ---
@app.route('/module_xss', methods=['GET','POST'])
def module_xss():
    if request.method == 'POST':
        comment = request.form.get('comment','')
        # reflected XSS: output without escaping (vulnerable)
        return "<h3>コメント（脆弱版）</h3><form method='post'>コメント: <input name='comment'><input type='submit' value='送信'></form><p>表示: %s</p>" % (comment,)
    return "<h3>コメント（脆弱版）</h3><form method='post'>コメント: <input name='comment'><input type='submit' value='送信'></form>"

# --- XSS secure route ---
@app.route('/module_xss/secure', methods=['GET','POST'])
def module_xss_secure():
    if request.method == 'POST':
        comment = request.form.get('comment','')
        # secure: use render_template_string with autoescape or manual escape
        safe = render_template_string("{{c}}", c=comment)
        return "<h3>コメント（対策版）</h3><form method='post'>コメント: <input name='comment'><input type='submit' value='送信'></form><p>表示: %s</p>" % (safe,)
    return "<h3>コメント（対策版）</h3><form method='post'>コメント: <input name='comment'><input type='submit' value='送信'></form>"

# --- Admin page (no server-side auth) ---
@app.route('/admin')
def admin():
    # vulnerable: no auth check
    return "<h3>管理画面（脆弱版）</h3><p>重要な管理情報がここにある。</p>"

# --- Admin secure (simple session check) ---
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pw')
        # demo auth: use fixed credentials (instructor sets these)
        if user == 'admin' and pw == 'password123':
            session['is_admin'] = True
            return redirect(url_for('admin_secure'))
        return "認証失敗", 403
    return "<form method='post'>ユーザ: <input name='user'> パス: <input name='pw' type='password'><input type='submit'></form>"

@app.route('/admin/secure')
def admin_secure():
    if not session.get('is_admin'):
        return "Forbidden", 403
    return "<h3>管理画面（対策版）</h3><p>管理情報。</p>"

# --- SSRF vulnerable demo ---
@app.route('/module_ssrf', methods=['GET','POST'])
def module_ssrf():
    if request.method == 'POST':
        url = request.form.get('url','')
        # vulnerable: directly fetch user-supplied URL (DANGEROUS in real world)
        try:
            r = requests.get(url, timeout=3)
            content = r.text[:1000]
        except Exception as e:
            content = "ERROR: " + str(e)
        return "<h3>SSRF デモ（脆弱版）</h3><form method='post'>URL: <input name='url'><input type='submit' value='取得'></form><pre>%s</pre>" % (content,)
    return "<h3>SSRF デモ（脆弱版）</h3><form method='post'>URL: <input name='url'><input type='submit' value='取得'></form>"

# --- SSRF secure demo (whitelist) ---
ALLOWED_HOSTS = ['example.com', 'localhost', '127.0.0.1']
from urllib.parse import urlparse
@app.route('/module_ssrf/secure', methods=['GET','POST'])
def module_ssrf_secure():
    if request.method == 'POST':
        url = request.form.get('url','')
        parsed = urlparse(url)
        host = parsed.hostname or ''
        if host not in ALLOWED_HOSTS:
            return "許可されていないホストです", 400
        try:
            r = requests.get(url, timeout=3)
            content = r.text[:1000]
        except Exception as e:
            content = "ERROR: " + str(e)
        return "<h3>SSRF デモ（対策版）</h3><form method='post'>URL: <input name='url'><input type='submit' value='取得'></form><pre>%s</pre>" % (content,)
    return "<h3>SSRF デモ（対策版）</h3><form method='post'>URL: <input name='url'><input type='submit' value='取得'></form>"

if __name__ == '__main__':
    # ensure DB exists and simple table populated
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT);')
        c.execute("INSERT INTO users (name,email) VALUES ('alice','alice@example.com');")
        c.execute("INSERT INTO users (name,email) VALUES ('bob','bob@example.com');")
        conn.commit()
        conn.close()
    app.run(host='0.0.0.0', port=8080, debug=False)
