from flask import Blueprint


foreground = Blueprint("foreground", __name__, url_prefix="/foreground")

from . import views, errors
