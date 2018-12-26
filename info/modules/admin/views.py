# Author Caozy
from datetime import datetime, timedelta
import time

from info import constants, db
from info.models import User, News, Category
from info.response_code import RET
from info.utils.image_storage import storage
from . import admin_blu
from info.utils.common import user_login_data
from flask import render_template, url_for, request, redirect, current_app, session, g, jsonify


@admin_blu.route('/login', methods=['GET', 'POST'])
@user_login_data
def admin_login():
    '''后台登录视图'''
    if request.method == 'GET':
        return render_template('admin/login.html')

    else:
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username, password]):
            return render_template('admin/login.html', errmsg='缺少参数')
        try:
            user = User.query.filter(User.nick_name == username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html', errmsg='查询数据库错误')
        if not user:
            return render_template('admin/login.html', errmsg='无此用户')

        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或密码错误')
        if not user.is_admin:
            return render_template('admin/login.html', errmsg='该用户无权限登录')

        session['user_id'] = user.id
        session['nick_name'] = username
        session['mobile'] = user.mobile
        if user.is_admin:
            session['is_admin'] = True
        return redirect(url_for('admin.admin_index'))


@admin_blu.route('/index')
@user_login_data
def admin_index():
    '''后端主界面函数'''
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))

    context = {
        'user': user.to_dict() if user else None
    }

    return render_template('admin/index.html', context=context)


@admin_blu.route('/user_count')
@user_login_data
def user_count():
    '''用户数量统计页'''
    # 用户总数,不包括超级管理员
    users_count = None
    try:
        users_count = User.query.filter(User.is_admin != True).count()
    except Exception as e:
        current_app.logger.error(e)
    # 用户月新增数
    mon_count = 0
    now = time.localtime()
    try:
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin != True, User.create_time > mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 用户日新增数
    day_count = 0
    try:
        day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin != True, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询图表信息，获取到当天00:00:00时间
    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组，保存数据
    active_date = []
    active_count = []

    # 依次添加数据，再反转
    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)
        end_date = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)
    active_date.reverse()
    active_count.reverse()
    data = {
        'users_count': users_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_date': active_date,
        'active_count': active_count

    }
    return render_template('admin/user_count.html', data=data)


@admin_blu.route('/user_list')
@user_login_data
def user_list():
    '''用户列表'''
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        page = 1
    user_page = User.query.order_by(User.last_login.desc()).paginate(page=page,
                                                                     per_page=constants.ADMIN_USER_PAGE_MAX_COUNT)
    users = user_page.items
    current_page = user_page.page
    total_page = user_page.pages
    user_list = []
    for user in users:
        user_list.append(user.to_admin_dict())

    data = {
        'user_list': user_list,
        'current_page': current_page,
        'total_page': total_page
    }
    return render_template('admin/user_list.html', data=data)


@admin_blu.route('/news_review', methods=['GET', 'POST'])
@user_login_data
def news_review():
    '''新闻审核'''

    if request.method == 'GET':
        page = request.args.get('page', 1)
        keywords = request.args.get("keywords", "")
        try:
            page = int(page)
        except Exception as e:
            page = 1

        filters=[]
        if keywords:
            filters.append(News.title.contains(keywords))
        news_page = News.query.filter(*filters).order_by(News.update_time.desc()).paginate(page=page,
                                                                          per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT)
        news = news_page.items
        current_page = news_page.page
        total_page = news_page.pages
        new_list = []
        for new in news:
            new_list.append(new.to_review_dict())
        data = {
            'new_list': new_list,
            'current_page': current_page,
            'total_page': total_page
        }
        return render_template('admin/news_review.html', data=data)


@admin_blu.route('/news_review_detail', methods=['GET', 'POST'])
@user_login_data
def news_review_detail():
    '''新闻审核详情'''
    if request.method == 'GET':
        new_id = request.args.get('new_id')
        if not new_id:
            return render_template('admin/news_review.html', errmsg='错误')
        try:
            new = News.query.get(new_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_review.html', errmsg='数据库错误')
        data = {'new': new.to_dict()}
        return render_template('admin/news_review_detail.html', data=data)
    else:
        new_id = request.json.get('news_id')
        action = request.json.get('action')

        if not all([new_id, action]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
        if action not in ('accept', 'reject'):
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        try:
            new = News.query.get(new_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(RET.DBERR, errmsg='数据库错误')
        if not new:
            return jsonify(RET.NODATA, errmsg='无此数据')
        if action == 'accept':
            new.status = 0
        else:
            reason = request.json.get('reason')
            if not reason:
                return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
            new.status = -1
            new.reason = reason
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='数据库错误')
        return jsonify(errno=RET.OK, errmsg="操作成功")


@admin_blu.route('/news_edit')
@user_login_data
def news_edit():
    '''新闻编辑'''
    try:
        page = request.args.get('page', 1)
        page = int(page)
    except Exception as e:
        page = 1
    keywords=request.args.get('keywords','')
    filters=[]
    if keywords:
        filters.append(News.title.contains(keywords))
    new_page = News.query.filter(*filters).order_by(News.update_time.desc()).paginate(page=page,
                                                                     per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT)
    news = new_page.items
    current_page = new_page.page
    total_page = new_page.pages

    new_list = []
    for new in news:
        new_list.append(new.to_review_dict())

    data = {
        'new_list': new_list,
        'current_page': current_page,
        'total_page': total_page
    }

    return render_template('admin/news_edit.html', data=data)


@admin_blu.route('/news_edit_detail', methods=['GET', 'POST'])
@user_login_data
def news_edit_detail():
    '''新闻编辑详情'''
    if request.method == 'GET':
        new_id = request.args.get('new_id')
        if not new_id:
            return render_template('admin/news_edit_detail.html', errmsg='参数传入错误')
        try:
            new = News.query.get(new_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg='数据库查询错误')
        filters=[Category.id!=1]
        categorys=Category.query.filter(*filters).all()
        category_list=[]
        for category in categorys:
            category_dict=category.to_dict()
            category_dict['is_selected']=False
            if category.id==new.category_id:
                category_dict['is_selected']=True
            category_list.append(category_dict)

        data = {'new_info': new.to_dict(),
                'categorys':category_list
                }

        return render_template('admin/news_edit_detail.html', data=data)


    else:
        new_id=request.form.get('new_id')
        title=request.form.get('title')
        category=request.form.get('category')
        digest=request.form.get('digest')
        new_image=request.files.get('new_image')
        content=request.form.get('content')
        if not all([new_id,title,category,digest,new_image,content]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
        try:
            new=News.query.get(new_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库错误')
        if not new:
            return jsonify(errno=RET.NODATA,errmsg='无此数据')
        try:
            data=new_image.read()
            path=storage(data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR,errmsg='获取数据失败')
        new.title = title
        new.source = '个人'
        new.category_id = category
        new.digest = digest
        new.index_image_url = constants.QINIU_DOMIN_PREFIX + path
        new.content = content
        # new.user_id = g.user.id
        new.status = 1  # 0通过/1审核中/-1未用过

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR,errmsg='数据保存失败')
        return jsonify(errno=RET.OK, errmsg="编辑成功")


@admin_blu.route('/news_type',methods=['GET','POST'])
@user_login_data
def news_type():
    '''新闻分类管理'''
    if request.method=='GET':
        try:
            categorys=Category.query.filter(Category.id!=1).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库错误')
        category_list=[]
        for category in categorys:
            category_list.append(category.to_dict())
        # category_list.pop(0)
        data={
            'categorys':category_list
        }

        return render_template('admin/news_type.html',data=data)
    else:
        # 编辑分类
        category_id=request.json.get('id')
        category_name=request.json.get('name')
        if not category_id:
            # 可用于新增
            category=Category()
            category.name=category_name
            try:
                db.session.add(category)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()
                return jsonify(errno=RET.DBERR,errmsg='数据库错误')
            return jsonify(errno=RET.OK,errmsg='OK')
        if not category_name:
            return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
        try:
            category =Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库错误')
        if not category:
            return jsonify(errno=RET.NODATA,errmsg='无数据')
        # 编辑数据
        category.name=category_name
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR,errmsg='数据库错误')
        return jsonify(errno=RET.OK, errmsg='OK')