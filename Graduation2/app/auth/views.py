from app.auth.forms import RegisterForm, LoginForm
from app.mail import send_mail
from app.models import User, UserLog
from app import db
from flask import redirect, url_for, flash, render_template, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
import datetime


@auth.before_app_request
def before_request():
    if (current_user.is_authenticated
        and not current_user.confirmed
        and request.blueprint != "auth"
        and request.endpoint != "static"):
        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("foreground.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    # print(confirm)
    if current_user.confirmed:
        return redirect(url_for("foreground.index"))
    if current_user.confirm(token):
        db.session.commit()
        flash("您已经完成邮箱确认!")
    else:
        flash("链接无效或已超时！")
    return redirect(url_for("foreground.index"))


@auth.route("/resend")
@login_required
def resend_mail():
    token = current_user.generate_confirmed_token()
    send_mail(current_app.config["GRADUATION_MAIL_SUBJECT_PREFIX"] + "Confirm account",
              current_app.config["GRADUATION_MAIL_SENDER"],
              [current_user.email],
              "auth/confirm_auth/confirm",
              token=token,
              user=current_user)
    return redirect(url_for("foreground.index"))


@auth.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).count()
        if not user:
            user_add = User(name=form.name.data,
                            email=form.email.data,
                            password=form.password.data)
            db.session.add(user_add)
            db.session.commit()
            send_mail("用户注册提示",
                      current_app.config["GRADUATION_MAIL_SENDER"],
                      [current_app.config["GRADUATION_MAIL_ADMIN"]],
                      "auth/remind_admin/remind_admin",
                      user=user_add)
            token = user_add.generate_confirmed_token()
            send_mail("账户确认",
                      current_app.config["GRADUATION_MAIL_SENDER"],
                      [user_add.email],
                      "auth/confirm_auth/confirm",
                      token=token,
                      user=user_add)
            flash("注册成功！有一封邮件已发送至您的邮箱请前往确认！")
            return redirect(url_for("auth.login"))
        else:
            flash("邮箱已被注册！")
            return redirect(url_for("auth.register"))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            duration = datetime.timedelta(seconds=60)
            login_user(user, form.remember_me.data, duration=duration)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("foreground.index")
            userlog = UserLog(user_id=user.id,
                              ip=request.remote_addr)
            db.session.add(userlog)
            db.session.commit()
            return redirect(next)
        flash("邮箱或密码错误！")
        return redirect(url_for("auth.login"))
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("你已退出登录")
    return redirect(url_for("auth.login"))



