from flask import Flask

from . import auth


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(auth.bp)
    return app
