from flask import Flask, jsonify, request, g, request_finished
from flask.signals import signals_available
from werkzeug.routing import BaseConverter, ValidationError
import yaml
from konfig import Config
from employees import teams


if not signals_available:
    raise RuntimeError("pip install blinker")


_USERS = {"1": "Vasya", "2": "Petya"}
_IDS = {val: id for id, val in _USERS.items()}


class XFMMiddleware:

    def __init__(self, app, real_ip="10.1.1.1"):
        self.app = app
        self.real_ip = real_ip

    def __call__(self, environ, start_response):
        if "HTTP_X_FORWARDED_FOR" not in environ:
            values = "%s, 10.3.4.5, 127.0.0.1" % self.real_ip
            environ["HTTP_X_FORWARDED_FOR"] = values
        return self.app(environ, start_response)


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


conf = Config("settings.ini")
app = Flask(__name__)
app.config.update(conf.get_map("flask"))
app.url_map.converters["registered"] = RegisteredUser
app.wsgi_app = XFMMiddleware(app.wsgi_app)
app.register_blueprint(teams)


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


@app.errorhandler(500)
def error_handling(error):
    return jsonify({"Error": str(error), "code": 500}, 500)


@app.route("/")
def auth():
    print("The raw Authorization header")
    print(request.environ["HTTP_AUTHORIZATION"])
    print("Flask's authorization header")
    print(request.authorization)
    return ""


@app.route("/api", methods=["POST", "GET"])
def my_microservice():
    if "X-Forwarded-For" in request.headers:
        ips = [
            ip.strip() for ip in
            request.headers["X-Forwarded-For"].split(",")
        ]
        ip = ips[0]
    else:
        ip = request.remote_addr
    print(request)
    print(request.environ)
    # response = yamlify(["Hello", "YAML", "World!"])
    response = jsonify({"Hello": g.user, "IP": ip})
    return response


@app.route("/api/person/<registered:name>")
def person(name):
    response = jsonify({"Hello": name})
    return response


if __name__ == "__main__":
    app.run(debug=(app.config["DEBUG"] == 1))
