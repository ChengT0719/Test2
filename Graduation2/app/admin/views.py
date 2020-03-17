from functools import wraps
from sqlalchemy import or_
from . import admin
from app.admin.forms import LoginForm, ScenicForm, AreaForm, TravelsForm
from flask import render_template, redirect, url_for, session, request, flash, current_app, make_response
from app.models import Admin, AdminLog, Area, Scenic, Oplog, Travels, User, Suggestion, UserLog
from app import db
from werkzeug.utils import secure_filename
from random import random
import os


def admin_login(f):
    """登录装饰器

    Args:

    Returns:

    Raise:

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            flash("请先登录", "error")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)

    return decorated_function


@admin.route("login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        account = data["account"]
        password = data["password"]
        admin = Admin.query.filter_by(account=account).first()
        if admin.check_password_hash(password):
            session["admin"] = admin.account
            session["admin_id"] = admin.id
            adminlog = AdminLog(admin_id=admin.id,
                                ip=request.remote_addr)
            db.session.add(adminlog)
            db.session.commit()
            return redirect(url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/index", methods=["GET"])
@admin_login
def index():
    return render_template("admin/index.html", admin=session["admin"])


@admin.route("scenic/add", methods=["POST", "GET"])
@admin_login
def scenic_add():
    """添加景区页面

    Args:

    Returns:

    Raise:

    """
    form = ScenicForm()
    form.area_id.choices = [(v.id, v.name) for v in Area.query.all()]
    if form.validate_on_submit():
        data = form.data
        scenic_count = Scenic.query.filter_by(title=data["title"]).count()
        if scenic_count == 1:
            flash("景点已存在！", "err")
            return redirect(url_for("admin.scenic_add"))
        # 生成唯一的文件名称
        file_logo = secure_filename(form.logo.data.filename)

        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
            os.chmod(current_app.config["UP_DIR"], "rw")
        # logo = change_filename(file_logo)
        logo = file_logo
        form.logo.data.save(current_app.config["UP_DIR"] + logo)
        scenic = Scenic(
            title=data["title"],
            logo=logo,
            star=int(data["star"]),
            address=data["address"],
            is_hot=int(data["is_hot"]),
            is_recommended=int(data["is_recommended"]),
            introduction=data["introduction"],
            content=data["content"],
            area_id=data["area_id"]
        )
        db.session.add(scenic)
        db.session.commit()
        flash("添加成功！", "ok")
        return redirect(url_for("admin.scenic_add" ))
    return render_template("admin/scenic_add.html", form=form)


@admin.route("/scenic/list", methods=["POST", "GET"])
@admin_login
def scenic_list():
    title = request.args.get("title", "", type=str)
    page = request.args.get("page", 1, type=int)
    if title:
        page_data = Scenic.query.filter_by(title=title).order_by(
            Scenic.add_time.desc()
        ).paginate(page=page, per_page=5)
    else:
        page_data = Scenic.query.order_by(
            Scenic.add_time.desc()
        ).paginate(page=page, per_page=5)
        return render_template("admin/scenic_list.html", page_data=page_data)


@admin.route("/scenic/edit/<int:id>", methods=["POST", "GET"])
@admin_login
def scenic_edit(id=None):
    form = ScenicForm()
    form.area_id.choices = [(v.id, v.name) for v in Area.query.all()]
    form.submit.label.text = "修改"
    form.logo.validators = []
    scenic = Scenic.query.get_or_404(int(id))
    if request.method == "GET":
        form.is_recommended.data =scenic.is_recommended
        form.is_hot.data = scenic.is_hot
        form.area_id.data = scenic.area_id
        form.star.data = scenic.star
        form.content.data = scenic.content
        form.introduction.data = scenic.introduction
        form.title.data = scenic.title
        form.address.data = scenic.address
    if form.validate_on_submit():
        data = form.data
        scenic_count = Scenic.query.filter_by(title=data["title"]).count()

        if scenic_count == 1 and scenic.title != data["title"]:
            flash("景点已存在！", "err")
            return redirect(url_for("admin.scenic_edit", id=id))
        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
            os.chmod(current_app.config["UP_DIR"], "rw")
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            scenic.logo = file_logo
            form.logo.data.save(current_app.config["UP_DIR"] + scenic.logo)

        scenic.title = data["title"]
        scenic.address = data["address"]
        scenic.area_id = data["area_id"]
        scenic.star = int(data["star"])
        scenic.is_hot = int(data["is_hot"])
        scenic.is_recommended = int(data["is_recommended"])
        scenic.introduction = data["introduction"]
        scenic.content = data["content"]

        db.session.add(scenic)
        db.session.commit()
        flash("修改景区成功！", "ok")
        addOplog("修改景区" + scenic.title)
        return redirect(url_for("admin.scenic_edit", id=id))
    return render_template("admin/scenic_edit.html", form=form, scenic=scenic)


@admin.route("/scenic/del/<int:id>", methods=["GET"])
@admin_login
def scenic_del(id=None):
    scenic = Scenic.query.get_or_404(id)
    db.session.delete(scenic)
    db.session.commit()
    flash("景区删除成功", "ok")
    addOplog("删除景区" + scenic.title)
    return redirect(url_for("admin.scenic_list", page=1))


@admin.route("/ckupload", methods=["POST", "OPTIONS"])
# @admin.login
def ckupload():
    error = ""
    url = ""
    callback = request.args.get("CKEditorFuncNum")

    if request.method == "POST" and "upload" in request.files:
        fileobj = request.files["upload"]
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = "{}{}".format(random(1000000), fext)

        filepath = os.path.join(current_app.static_folder, "uploads/ckeditor", rnd_name)
        print(filepath)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs((dirname))
            except:
                error = "ERROR_CREATE_DIR"
        elif not os.access(dirname, os.W_OK):
            error = "ERROR_DIR_NOT_WRITEABLE"

        if not error:
            fileobj.save(filepath)
            url = url_for("static", filename="{}{}".format("uploads/ckeditor", rnd_name))
    else:
        error = "post error"

    res = """<script type="text/javascript">
    window.parent.CKEDITOR.tools.callFunction({},'{}','{}'):
    </script>""".format(callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response


@admin.route("/area/add", methods=["GET", "POST"])
@admin_login
def area_add():
    form = AreaForm()
    if form.validate_on_submit():
        data = form.data
        area = Area.query.filter_by(name=data["name"]).count()
        if area == 1:
            flash("地区已存在", "error")
            return redirect(url_for("admin.area_add"))
        area = Area(
            name=data["name"],
            is_recommended=data["is_recommended"],
            introduction=data["introduction"]
        )
        db.session.add(area)
        db.session.commit()
        addOplog("添加地区" + data["name"])
        flash("地区添加成功", "ok")
        return redirect(url_for("admin.area_add"))
    return render_template("admin/area_add.html", form=form)


@admin.route("/area/del", methods=["GET"])
@admin_login
def area_del(id=None):
    area = Area.query.filter_by(id=id).first_or_404()
    db.session.delete(area)
    db.session.commit()
    addOplog("删除地区" +area.name)
    flash("地区<<{0}>>删除成功".format(area.name), "ok")
    return redirect(url_for("admin.area_list"))


@admin.route("/area/list", methods=["GET"])
@admin_login
def area_list():
    name = request.args.get("name", type=str)
    page = request.args.get("page", 1, type=int)
    if name:
        page_data = Area.query.filter_by(name=name).order_by(
            Area.add_time.desc()
        ).paginate(page=page, per_page=5)
    else:
        page_data = Area.query.order_by(
            Area.add_time.desc()
        ).paginate(page=page, per_page=5)
    return render_template("admin/area_list.html", page_data=page_data)


@admin.route("/area/edit/<int:id>", methods=["POST", "GET"])
@admin_login
def area_edit(id=None):
    form = AreaForm()
    form.submit.label.text = "修改"
    area = Area.query.get_or_404(int(id))
    if request.method == "GET":
        form.name.data = area.name
        form.is_recommended.data = area.is_recommended
        form.introduction.data = area.introduction
    if form.validate_on_submit():
        data = form.data
        area_count = Area.query.filter_by(name=data["name"]).count()
        if area_count == 1 and area.name != data["name"]:
            flash("地区已存在！", "error")
            return redirect(url_for("admin.area_edit", id=id))
        area.name = data["name"]
        area.is_recommended = data["is_recommended"]
        area.introduction = data["introduction"]
        db.session.add(area)
        db.session.commit()
        flash("修改地区成功！", "ok")
        addOplog("修改地区" + str(area.name))
        return redirect(url_for("admin.area_edit", id=id))
    return render_template("admin/area_edit.html", form=form, area=area)


@admin.route("/travels/add", methods=["POST", "GET"])
@admin_login
def travels_add():
    form = TravelsForm()
    form.scenic_id.choices = [(v.id, v.title) for v in Scenic.query.all()]
    if form.validate_on_submit():
        data = form.data
        travels_count = Travels.query.filter_by(title=data["title"]).count()
        if travels_count == 1:
            flash("景点已存在！", "err")
            return redirect(url_for("admin.travels_add"))
        travels = Travels(
            title=data["title"],
            author=data["author"],
            scenic_id=data["scenic_id"],
            content=data["content"],
        )
        db.session.add(travels)
        db.session.commit()
        addOplog("添加游记" + data["title"])
        flash("添加游记成功", "ok")
        return redirect(url_for("admin.travels_add"))
    return render_template("admin/travels_add.html", form=form)


@admin.route("/travels/list", methods=["GET"])
@admin_login
def travels_list():
    keywords = request.args.get("keywords", "", type=str)
    page = request.args.get("page", 1, type=int)
    if keywords:
        page_data = Travels.query.filter(Travels.title.like("%"+keywords+"%")).order_by(
            Travels.add_time.desc()
        ).paginate(page=page, per_page=5)
    else:
        page_data = Travels.query.order_by(
            Travels.add_time.desc()
        ).paginate(page=page, per_page=5)
    return render_template("admin/travels_list.html", page_data=page_data)


@admin.route("/travels/edit/<int:id>", methods=["POST", "GET"])
@admin_login
def travels_edit(id=None):
    form = TravelsForm()
    form.scenic_id.choices = [(v.id, v.title) for v in Scenic.query.all()]
    form.submit.label.text = "修改"
    travels = Travels.query.get_or_404(int(id))
    if request.method == "GET":
        form.content.data = travels.content
        form.author.data = travels.author
        form.title.data = travels.title
    if form.validate_on_submit():
        data = form.data
        travels_count = Travels.query.filter_by(title=data["title"]).count()
        if travels_count == 1 and travels.title != data["title"]:
            flash("游记已存在！", "error")
            return redirect(url_for("admin.travels_edit", id=id))
        travels.title = data["title"]
        travels.content = data["content"]
        travels.author = data["author"]
        db.session.add(travels)
        db.session.commit()
        flash("修改景区成功！", "ok")
        addOplog("修改景区" + travels.title)
        return redirect(url_for("admin.travels_edit", id=id))
    return render_template("admin/travels_edit.html", form=form, travels=travels)


@admin.route("/travels/del", methods=["GET"])
@admin_login
def travels_del(id=None):
    travels = Travels.query.filter_by(id=id).first_or_404()
    db.session.delete(travels)
    db.session.commit()
    addOplog("删除地区" + travels.name)
    flash("地区<<{0}>>删除成功".format(travels.name), "ok")
    return redirect(url_for("admin.travels_list"))


@admin.route("/user/list", methods=["GET"])
@admin_login
def user_list():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword", "", type=str)

    if keyword:
        filters = or_(User.username == keyword, User.email == keyword)
        page_data = User.query.filter(filters).order_by(
            User.add_time.desc()
        ).paginate(page=page, per_page=5)
    else:
        page_data = User.query.order_by(
            User.add_time.desc()
        ).paginate(page=page, per_page=5)

    return render_template("admin/user_list.html", page_data=page_data)


@admin.route("/user/view/<int:id>", methods=["GET"])
@admin_login
def user_view(id=None):
    form_page = request.args.get("fp")
    if not form_page:
        form_page = 1
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user, form_page=form_page)


@admin.route("/user/del", methods=["GET"])
@admin_login
def user_del(id=None):
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    addOplog("删除地区" + user.name)
    flash("地区<<{0}>>删除成功".format(user.email), "ok")
    return redirect(url_for("admin.user_list"))


@admin.route("/suggestion_list/list", methods=["GET"])
@admin_login
def suggestion_list():
    page = request.args.get("page", 1, type=int)
    page_data = Suggestion.query.order_by(
        Suggestion.add_time.desc()
    ).paginate(page=page, per_page=5)
    return render_template("admin/suggestion.html", page_data=page_data)


@admin.route("/suggestion/del/<int:id>", methods=["GET"])
@admin_login
def suggestion_del(id=None):
    page = request.args.get("page", 1, type=int)
    suggestion = Suggestion.query.get_or_404(int(id))
    db.session.delete(suggestion)
    db.session.commit()
    addOplog("删除意见建议")
    flash("删除成功！", "ok")
    return redirect(url_for("admin.suggestion_list", page=page))


@admin.route("/oplog/list", methods=["GET"])
@admin_login
def oplog_list():
    page = request.args.get("page", 1, type=int)
    page_data = Oplog.query.join(
        Admin
    ).filter(
        Admin.id == Oplog.admin_id,
    ).order_by(
        Oplog.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/oplog_list.html", page_data=page_data)


@admin.route("/adminloginlog/list", methods=["GET"])
@admin_login
def adminloginlog_list(page=None):
    page = request.args.get("page", 1, type=int)
    page_data = AdminLog.query.join(
        Admin
    ).filter(
        Admin.id == AdminLog.admin_id,
    ).order_by(
        AdminLog.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


@admin.route("userloginlog/list", methods=["GET"])
@admin_login
def userloginlog_list(page=None):
    page = request.args.get("page", 1, type=int)
    page_data = UserLog.query.join(
        User
    ).filter(
        User.id == UserLog.id
    ).order_by(
        UserLog.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("auth/userloginlog_list.html", page_data=page_data)


def addOplog(reason):
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason=reason
    )
    db.session.add(oplog)
    db.session.commit()
#
# def gen_rnd_filename():
#     return datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex)


