from flask import Flask, render_template, redirect
from database import db, User
from forms import UserForm, LoginForm
from flask_wtf.csrf import CsrfProtect
from stravalib import Client
from flask_login import LoginManager, login_user, logout_user, login_required
import functools


app = Flask(__name__)
app.config["STRAVA_CLIENT_ID"] = "runnerly-strava-id"
app.config["STRAVA_CLIENT_SECRET"] = "runnerly-strava-secret"
csrf = CsrfProtect()


def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return app.login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required


@app.route("/users")
def users():
    users = db.session.query(User)
    return render_template("users.html", users=users)


@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    form = UserForm()
    if request.method == "POST":
        new_user = User()
        form.populate_obj(new_user)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/users")
    return render_template("create_user.html", form=form)


@app.route("/fetch")
def fetch_runs():
    from monolith.background import fetch_all_runs
    res = fetch_all_runs.delay()
    res.wait()
    return jsonify(res.result)


def get_strava_auth_url():
    client = Client()
    client_id = app.config["STRAVA_CLIENT_ID"]
    redirect = "http://127.0.0.1:5000/strava_auth"
    url = client.authorization_url(client_id=client_id, redirect_uri=redirect)
    return url


@app.route("/strava_auth")
@login_required
def _strava_auth():
    code = request.args.get("code")
    client = Client()
    xc = client.exchange_code_for_token
    access_token = xc(client=app.config["STRAVA_CLIENT_ID"],
                      client_secret=app.config["STRAVA_CLIENT_SECRET"],
                      code=code)
    current_user.strava_token = access_token
    db.session.commit()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect("/")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user


@admin_required
def index_page():
    return render_template("index.html")


if __name__ == "__main__":
    db.init_app(app)
    csrf.init_app(app)
    db.create_all(app=app)
    app.run()
