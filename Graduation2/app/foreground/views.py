from flask import redirect, url_for, flash, render_template, request
from . import foreground
from app.models import Scenic, Area, Collect, Travels, Suggestion
from sqlalchemy import and_
from flask_login import current_user, login_required
from app import db
from app.foreground.forms import SuggestionForm


@foreground.route("/index")
def index():
    area = Area.query.all()
    hot_area = Area.query.filter_by(is_recommended=1).limit(2).all()
    scenic = Scenic.query.filter_by(is_hot=1).all()
    # for v in scenic:
    # print(v.introduction)
    return render_template("foreground/index.html", area=area, hot_area=hot_area, scenic=scenic)


@foreground.route("/search")
def search():
    """搜索功能

       Args:

       Returns:

       Raise:

       """
    page = request.args.get("page", 1, type=int)
    area = Area.query.all()
    area_id = request.args.get("area_id", type=int)
    star = request.args.get("star", type=int)

    if area_id or star:
        filters = and_(Scenic.area_id == area_id, Scenic.star == star)
        page_data = Scenic.query.filter(filters).paginate(page=page, per_page=3)
    else:
        page_data = Scenic.query.paginate(page=page, per_page=3)
    return render_template("foreground/search.html", page_data=page_data, area=area, area_id=area_id, star=star)


@foreground.route("/info/<int:id>")
def info(id=None):
    """详情页

        Args:

        Returns:

        Raise:

        """

    scenic = Scenic.query.get_or_404(int(id))
    user_id = current_user.id if current_user.is_authenticated else None
    if user_id:
        count = Collect.query.filter_by(
            user_id=int(user_id),
            scenic_id=int(id)
        ).count()
    else:
        user_id = 0
        count = 0
    return render_template("foreground/info.html", scenic=scenic, user_id=user_id, count=count)


@foreground.route("/travels/<int:id>/")
def travels(id=None):
    """详情页

    Args:

    Returns:

    Raise:

    """
    travels = Travels.query.get_or_404(int(id))
    return render_template('foreground/travels.html', travels=travels)


@foreground.route("/collect_add")
def collect_add():
    """收藏景区

    Args:

    Returns:

    Raise:

    """
    scenic_id = request.args.get("scenic_id", "")
    user_id = current_user.id
    collect = Collect.query.filter_by(
        user_id=int(user_id),
        scenic_id=int(scenic_id)
    ).count()
    if collect == 1:
        data = dict(ok=0)
    if collect == 0:
        collect = Collect(
            user_id=int(user_id),
            scenic_id=int(scenic_id)
        )
        db.session.add(collect)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


@foreground.route("/collect_del")
def collect_del():
    """取消收藏

    Args:

    Returns:

    Raise:

    """
    if request.args.get("collect_id"):
        scenic_id = Collect.query.filter_by(id=request.args.get("collect_id")).first().scenic_id
    else:
        scenic_id = request.args.get("scenic_id")
    user_id = current_user.id
    collect = Collect.query.filter_by(
        user_id=int(user_id),
        scenic_id=int(scenic_id)
    ).first()
    db.session.delete(collect)
    db.session.commit()
    data = dict(ok=1)
    import json
    return json.dumps(data)


@foreground.route("/collect_list")
@login_required
def collect_list():
    # 获取page参数值
    page = request.args.get("page", 1, type=int)
    # 根据user_id筛选Collect表数据
    page_data = Collect.query.filter_by(user_id=current_user.id).order_by(
        Collect.add_time.desc()
    # 使用分页方法
    ).paginate(page=page, per_page=3)
    # 渲染模板
    print(page_data.items)
    return render_template("foreground/collect_list.html", page_data=page_data)


@foreground.route("suggestion", methods=["POST", "GET"])
@login_required
def suggestion():
    form = SuggestionForm()
    if form.validate_on_submit():
        data = form.data
        suggestion = Suggestion(name=data["name"],
                                email=data["email"],
                                suggestion=data["suggestion"])
        db.session.add(suggestion)
        db.session.commit()
        flash("您的建议我们已收到,感谢您的提供!", "ok")
        return redirect(url_for("foreground.suggestion"))
    return render_template("foreground/suggestion_list.html", form=form)
