from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp
from app.models import User


class RegisterForm(FlaskForm):
    name = StringField("用户名",
                       validators=[
                           DataRequired("姓名不能为空!"),
                           Regexp("^[A-Za-z][A-Za-z0-9_]*$", 0, "用户名必须以字母开头，且只能包含字母数字下划线！")
                       ],
                       render_kw={
                           "placeholder": "请输入用户名"
                       })

    email = StringField("邮箱",
                        validators=[
                            DataRequired("邮箱不能为空!"),
                            Email("邮箱格式不正确!")
                        ],
                        render_kw={
                            "placeholder": "请输入邮箱"
                        })

    password = PasswordField("密码",
                             validators=[
                                 DataRequired("密码不能为空")
                             ],
                             render_kw={
                                 "placeholder": "请输入密码"
                             })

    repassword = PasswordField("确认密码",
                               validators=[
                                   DataRequired("请确认输入密码"),
                                   EqualTo("password", "两次密码不一致"),
                               ],
                               render_kw={
                                   "placeholder": "请再次输入密码"
                               })
    submit = SubmitField("注册")

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            self.email.data = ""
            raise ValidationError("邮箱已存在！")

    def validate_name(self, field):
        name = field.data
        user = User.query.filter_by(name=name).first()
        if user:
            self.name.data = ""
            raise ValidationError("用户名已存在！")


class LoginForm(FlaskForm):
    email = StringField("邮箱",
                        validators=[
                            DataRequired("邮箱不能为空!"),
                            Email("邮箱格式不正确！")
                        ],
                        render_kw={
                            "placeholder": "请输入邮箱"
                        })
    password = PasswordField("密码",
                             validators=[
                                 DataRequired("密码不能为空!")
                             ],
                             render_kw={
                                 "placeholder": "请输入密码"
                             })
    remember_me = BooleanField("自动登录")
    submit = SubmitField("登录",
                         render_kw={
                             "class": "btn btn-primary",
                         })


