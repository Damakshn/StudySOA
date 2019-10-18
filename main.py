from flask import Flask, jsonify, request
from werkzeug.routing import BaseConverter, ValidationError

_USERS = {"1": "Vasya", "2": "Petya"}
_IDS = {val: id for id, val in _USERS.items()}

class RegisteredUser(BaseConverter):

    def to_python(self, value):
        if value in _USERS:
            return _USERS[value]
        raise ValidationError()
    
    def to_url(self, value):
        return _IDS[value]

app = Flask(__name__)
app.url_map.converters["registered"] = RegisteredUser

@app.route("/api", methods=["POST", "DELETE", "GET"])
def my_microservice():
    print(request)
    print(request.environ)
    response = jsonify({"Hello":"World!"})
    print(response)
    print(response.data)
    return response

@app.route("/api/person/<registered:name>")
def person(name):
    response = jsonify({"Hello": name})
    return response

if __name__ == "__main__":
    app.run()
