from app import mail
from flask_mail import Message
from flask import render_template, current_app
from threading import Thread


def send_async_mail(appp, msg):
    with appp.app_context():
        mail.send(msg)


def send_mail(title, sender, recipients: list, template, **args):
    app = current_app._get_current_object()
    msg = Message(title,
                  sender=sender,
                  recipients=recipients)
    msg.body = render_template(template + ".txt", **args)
    msg.html = render_template(template + ".html", **args)
    trd = Thread(target=send_async_mail, args=[app, msg])
    trd.start()
    return trd