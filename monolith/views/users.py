from flask import Blueprint, render_template
from monolith.database import db, User
from monolith.forms import UserForm

users = Blueprint('users', __name__)


@users.route("/users")
def user_list():
    users = db.session.query(User)
    return render_template("users.html", users=users)


@users.route("/create_user", methods=["GET", "POST"])
def create_user():
    form = UserForm()
    if request.method == "POST":
        new_user = User()
        form.populate_obj(new_user)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/users")
    return render_template("create_user.html", form=form)
