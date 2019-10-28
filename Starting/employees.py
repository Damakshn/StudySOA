from flask import Blueprint, jsonify

teams = Blueprint("teams", __name__)

_DEVS = ["Alice", "Bob"]
_OPS = ["Bill"]
_TEAMS = {1: _DEVS, 2: _OPS}


@teams.route("/teams")
def get_all():
    return jsonify(_TEAMS)


@teams.route("/teams/<int:team_id>")
def get_item(team_id):
    return jsonify(_TEAMS[team_id])
