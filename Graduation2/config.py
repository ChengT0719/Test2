import os


class Config:
    APP_NAME = "Graduation"
    SERVER_PORT = 9507
    SECRET_KEY = "what is the key ?"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHENY_COMMIT_ON_TEARDOWN = True

    Debug = True

    MAIL_SERVER = "smtp.sina.com"
    MAIL_PORT = 25
    # MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME") or "chengtt0719@sina.com"
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD") or "b24b2a70a199a3f0"

    GRADUATION_MAIL_SENDER = "chengtt0719@sina.com"
    GRADUATION_MAIL_SUBJECT_PREFIX = "Graduation Project:"
    GRADUATION_MAIL_ADMIN = "chengtt0719@sina.com"

    UP_DIR = "app/static/"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # SQLAlchemy 配置
    HOST = "127.0.0.1"
    PORT = 3306
    USERNAME = "root"
    PASSWORD = "root"
    DATABASE = "graduation"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}".format(USERNAME, PASSWORD, HOST, PORT, DATABASE)


class TestConfig(Config):
    # APP_NAME = "TESTING"
    TESTING = True
    # SQLAlchemy 配置
    HOST = "127.0.0.1"
    PORT = 3306
    USERNAME = "root"
    PASSWORD = "root"
    DATABASE = "graduationtest"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}".format(USERNAME, PASSWORD, HOST, PORT, DATABASE)


config_create_app = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "default": DevelopmentConfig
}