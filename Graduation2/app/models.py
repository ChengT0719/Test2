from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    """用户类

    Args:

    Returns:

    Raise:

    """
    # 表名
    __tablename__ = "user"

    __table_args__ = {"useexisting": True}
    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 姓名
    name = db.Column(db.String(26), nullable=False)
    # 邮箱
    email = db.Column(db.String(26), nullable=False)
    # 密码
    password_hash = db.Column(db.String(255), nullable=False)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())
    # 确认状态
    confirmed = db.Column(db.Boolean, default=False)
    # 景区收藏
    collect = db.relationship("Collect", backref="user")
    # 用户日志
    userlog = db.relationship("UserLog", backref="user")

    def generate_confirmed_token(self, expiration=3600):
        """生成验证码

        Args:
            expiration:有效时间单位秒，s

        Returns:

        Raise:

        """
        s = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id}).decode("utf-8")

    def confirm(self, token):
        """确认验证码

        Args:
            token:被加密的验证码

        Returns:

        Raise:

        """
        s = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def password(self):
        raise AttributeError("密码不可获取！")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """设置输出格式

        Args:

        Returns:

        Raise:

        """
        return "<user {}>".format(self.name)


class Area(db.Model):
    __tablename__ = "area"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    is_recommended = db.Column(db.Boolean(), default=0)
    introduction = db.Column(db.Text)
    scenic = db.relationship("Scenic", backref="area")

    def __repr__(self):
        return "<Area {}>".format(self.name)


class Scenic(db.Model):
    __tablename__ = "scenic"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    star = db.Column(db.Integer)
    logo = db.Column(db.String(255), unique=True)
    introduction = db.Column(db.Text)
    content = db.Column(db.Text)
    address = db.Column(db.Text)
    is_hot = db.Column(db.Boolean(), default=0)
    is_recommended = db.Column(db.Boolean(), default=0)

    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    collect = db.relationship("Collect", backref="scenic")
    travels = db.relationship("Travels", backref="scenic")


class Collect(db.Model):
    __tablename__ = "collect"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    scenic_id = db.Column(db.Integer, db.ForeignKey("scenic.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Travels(db.Model):
    __tablename__ = "travels"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    content = db.Column(db.Text)
    scenic_id = db.Column(db.Integer, db.ForeignKey("scenic.id"))
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)


class UserLog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(30))
    add_time = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Admin(db.Model):
    """管理员

    Args:

    Returns:

    Raise:

    """
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    adminlog = db.relationship("AdminLog", backref="admin")
    oplog = db.relationship("Oplog", backref="admin")

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):
        raise AttributeError("密码不可获取！")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return "<Admin {}>".format(self.account)


class AdminLog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))


class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))


class Suggestion(db.Model):
    __tablename__ = "suggestion"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    suggestion = db.Column(db.Text, nullable=False)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    # print(getattr(User, "email"))


