from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp
from app.models import User


class SuggestionForm(FlaskForm):
    name = StringField(
        label="姓名",
        validators=[DataRequired("姓名不能为空！")],
        render_kw={
            "placeholder": "请输入姓名！",
            "class": "form-control",
        }
    )
    email = StringField(
        label="邮箱",
        validators=[DataRequired("邮箱不能为空！"),
                    Email("邮箱格式不正确！")],
        render_kw={
            "placeholder": "请输入邮箱！",
            "type": "email",
            "class": "form-control"
        }
    )
    suggestion = TextAreaField(
        label="意见建议",
        validators=[DataRequired("内容不能为空！")],
        render_kw={
            "placeholder": "请输入内容！",
            "class": "form-control",
            "rows": 7
        }
    )
    submit = SubmitField(
        "发送消息",
        render_kw={
            "class": "form-control",
        }
    )

