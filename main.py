from flask import Flask, jsonify, request, g, request_finished
from flask.signals import signals_available
from werkzeug.routing import BaseConverter, ValidationError
import yaml


if not signals_available:
    raise RuntimeError("pip install blinker")


_USERS = {"1": "Vasya", "2": "Petya"}
_IDS = {val: id for id, val in _USERS.items()}


class RegisteredUser(BaseConverter):

    def to_python(self, value):
        if value in _USERS:
            return _USERS[value]
        raise ValidationError()

    def to_url(self, value):
        return _IDS[value]


def yamlify(data, status=200, headers=None):
    _headers = {"Content-Type": "Application/x-yaml"}
    if headers is not None:
        _headers.update(headers)
    return yaml.safe_dump(data), status, _headers


app = Flask(__name__)
app.url_map.converters["registered"] = RegisteredUser


def finished(sender, response, **extra):
    print("About to send a Response")
    print(response)


request_finished.connect(finished)


@app.before_request
def authenticate():
    if request.authorization:
        g.user = request.authorization["username"]
    else:
        g.user = "Anonymous"


@app.route("/")
def auth():
    print("The raw Authorization header")
    print(request.environ["HTTP_AUTHORIZATION"])
    print("Flask's authorization header")
    print(request.authorization)
    return ""


@app.route("/api", methods=["POST", "DELETE", "GET"])
def my_microservice():
    print(request)
    print(request.environ)
    # response = yamlify(["Hello", "YAML", "World!"])
    response = jsonify({"Hello": g.user})
    return response


@app.route("/api/person/<registered:name>")
def person(name):
    response = jsonify({"Hello": name})
    return response


if __name__ == "__main__":
    app.run()
