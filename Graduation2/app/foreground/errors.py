from flask import render_template
from . import foreground


@foreground.app_errorhandler(404)
def page_not_found(e):
    return render_template("foreground/404.html"), 404


@foreground.app_errorhandler(500)
def server_error(e):
    return render_template("foreground/500.html"), 500
