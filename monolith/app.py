from flask import Flask, render_template
from database import db, User
from forms import UserForm
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
csrf = CsrfProtect()


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


if __name__ == "__main__":
    db.init_app(app)
    csrf.init_app(app)
    db.create_all(app=app)
    app.run()
