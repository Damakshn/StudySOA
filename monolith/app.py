from flask import Flask
from monolith.database import db, User
from monolith.views import blueprints
from monolith.auth import login_manager
from konfig import Config


def create_app():
    app = Flask(__name__)
    conf = Config("settings.ini")
    app.config.update(conf.get_map("main"))

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=(app.config["DEBUG"] == 1))
