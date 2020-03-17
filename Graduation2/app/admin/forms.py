from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, RadioField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from app.models import Admin


class LoginForm(FlaskForm):
    account = StringField("账户",
                          validators=[DataRequired("账户不能为空！")],
                          render_kw={
                              "placeholder": "请输入账户名"
                          })
    password = PasswordField("密码",
                             validators=[DataRequired("密码不能为空！")],
                             render_kw={
                                 "placeholder": "请输入密码"
                             })
    submit = SubmitField("登录")

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(account=account).count()
        if not admin:
            raise ValidationError("用户名不存在！")


class ScenicForm(FlaskForm):
    title = StringField(label="景区名称",
                        validators=[DataRequired("景区名称不能为空！")],
                        render_kw={
                            "placeholder": "请输入景区名称"
                        })
    area_id = SelectField(label="所属地区",
                          validators=[DataRequired("请选择标签！")],
                          coerce=int,
                          render_kw={
                              # "class": "form-control",
                          })
    address = StringField(label="景区地址",
                          validators=[DataRequired("景区地址不能为空！")],
                          render_kw={
                              "placeholder": "请输入景区地址!",
                              # "class": "form-control"
                          })
    star = SelectField(label="星级",
                       validators=[DataRequired("请输入星级！")],
                       coerce=int,
                       choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")], default=5,
                       render_kw={
                           # "class": "form_control",
                       })
    logo = FileField(label="封面",
                     validators=[DataRequired("请上传封面！"),
                                 FileAllowed(["jpg", "png"], "请上传jpg或者png格式图片！")],)
    is_hot = RadioField(label="是否热门",
                        coerce=int,
                        choices=[(0, "否"), (1, "是")], default=0
                        )
    is_recommended = RadioField(label="是否推荐",
                                coerce=int,
                                choices=[(0, "否"), (1, "是")], default=0
                                )
    introduction = TextAreaField(label="景区简介",
                                 validators=[DataRequired("简介不能为空")],
                                 render_kw={
                                     # "class": "form-control",
                                     "rows": 5
                                 })
    content = TextAreaField(label="景区内容",
                            validators=[DataRequired("景区内容不能为空！")],
                            render_kw={
                                # "class": "form-control ckeditor",
                                "rows": 10
                            }
                            )

    submit = SubmitField("添加",
                         render_kw={
                             "class": "btn btn-primary",
                         })


class AreaForm(FlaskForm):
    name = StringField(label="名称",
                       validators=[DataRequired("地区名不能为空")],
                       render_kw={
                           "class": "form-control",
                           "placeholder": "请输入地区名称"
                       })
    is_recommended = RadioField(label="是否推荐",
                                coerce=int,
                                choices=[(0, "否"), (1, "是")], default=0
                                )
    introduction = TextAreaField(label="简介",
                                 validators=[DataRequired("简介不能为空！")],
                                 render_kw={
                                     "class": "form-control",
                                     "rows": 5
                                 })
    submit = SubmitField("添加")


class TravelsForm(FlaskForm):
    title = StringField(label="标题",
                        validators=[DataRequired("标题不能为空！")],
                        render_kw={
                            "class": "form-control",
                            "placeholder": "请输入标题"
                        })
    author = StringField(label="作者",
                         validators=[DataRequired("作者不能为空！")],
                         render_kw={
                             "placeholder": "请输入作者",
                             "class": "form-control"
                         })
    scenic_id = SelectField(label="所属景区",
                            validators=[DataRequired("请选择景区!")],
                            coerce=int,
                            render_kw={
                                "class": "form-control",
                            })
    content = TextAreaField(label="游记内容",
                            validators=[DataRequired("游记内容不能为空！")],
                            render_kw={
                                "class": "form-control ckeditor",
                            })
    submit = SubmitField("添加",
                         render_kw={
                             "class": "btn btn-primary",
                         })
