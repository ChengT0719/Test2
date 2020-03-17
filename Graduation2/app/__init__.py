from flask import Flask
from config import Config, config_create_app
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail

login_manager = LoginManager()
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()

login_manager.login_view = "auth.login"


def create_app(config):
    app = Flask(Config.APP_NAME, template_folder="app/templates", static_folder="app/static")
    app.config.from_object(config_create_app[config])

    config_create_app[config].init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    from app.foreground import foreground
    from app.auth import auth
    from app.admin import admin
    app.register_blueprint(foreground)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    return app
