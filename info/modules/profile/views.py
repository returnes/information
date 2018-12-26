# Author Caozy
from flask import render_template, g, request, jsonify, current_app

from info import db, constants
from info.models import User, News, Category
from info.response_code import RET
from info.utils.image_storage import storage
from . import profile_bul
from info.utils.common import user_login_data


@profile_bul.route('/info', methods=['GET', 'POST'])
@user_login_data
def get_user_info():
    '''用户中心'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if request.method == "GET":
        data = {
            'user_info': user.to_dict() if user else None
        }
        return render_template('news/user_base_info.html', data=data)
    if request.method == "POST":
        signature = request.json.get('signature')
        nick_name = request.json.get('nick_name')
        gender = request.json.get('gender')
        if gender not in (['MAN', 'WOMAN']):
            return jsonify(errno=RET.DATAERR, errmsg='数据错误')
        if not all([signature, nick_name, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

        try:
            user = User.query.get(user.id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库错误')
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='数据库错误')
        return jsonify(errno=RET.OK, errmsg='提交成功')


@profile_bul.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    '''头像设置'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if request.method == "GET":
        data = {
            'user_info': user.to_dict() if user else None
        }
        return render_template('news/user_pic_info.html', data=data)

    avatar=request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    try:
        data=avatar.read()
        path=storage(data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传失败')
    user.avatar_url=path
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK,errmsg='ok',data={'avatar_url':constants.QINIU_DOMIN_PREFIX+path})


@profile_bul.route('/follow_info')
@user_login_data
def follow_info():
    '''我的关注'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if request.method == "GET":
        page = request.args.get('page',1)
        try:
            page = int(page)
        except Exception as e:
            current_app.logger.error(e)
            page = 1
        try:
            followers_page = user.followed.paginate(page=page, per_page=constants.USER_COLLECTION_MAX_NEWS)
            followers = followers_page.items
            current_page = followers_page.page
            total_page = followers_page.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库错误')
        follows=[]
        for item in followers:
            follows.append(item.to_dict())

        data = {
            'user_info': user.to_dict() if user else None,
            'users':follows,
            'current_page':current_page,
            'total_page':total_page
        }
        return render_template('news/user_follow.html', data=data)


@profile_bul.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    '''密码修改'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if request.method == "GET":
        data = {
            'user_info': user.to_dict() if user else None
        }
        return render_template('news/user_pass_info.html', data=data)

    old_password=request.form.get('old_password')
    new_password1=request.form.get('new_password1')
    new_password2=request.form.get('new_password2')
    if not all([old_password,new_password1,new_password2]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR,errmsg='密码错误')
    if new_password1!=new_password2:
        return jsonify(errno=RET.PWDERR,errmsg='密码不一致')

    user.password=new_password2
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据库错误')
    return jsonify(errno=RET.OK,errmsg='ok')

@profile_bul.route('/collection_info')
@user_login_data
def collection_info():
    '''我的收藏'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    try:
        page=request.args.get('page',1)
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据错误')

    try:
        collection_page=user.collection_news.paginate(page=page,per_page=constants.USER_COLLECTION_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库错误')

    collections=collection_page.items
    current_page=collection_page.page
    total_page=collection_page.pages

    data = {
        'user_info': user.to_dict() if user else None,
        'collections':collections,
        'current_page':current_page,
        'total_page':total_page
    }
    return render_template('news/user_collection.html', data=data)




@profile_bul.route('/news_release_info',methods=['GET','POST'])
@user_login_data
def news_release_info():
    '''新闻发布'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if request.method == "GET":
        try:
            categories=Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="数据库错误")
        category_list=[]
        for category in categories:
            category_list.append(category.to_dict())
        category_list.pop(0)
        data = {
            'user_info': user.to_dict() if user else None,
            'category_list':category_list
        }
        return render_template('news/user_news_release.html', data=data)
    title=request.form.get('title')
    category_id=request.form.get('category_id')
    digest=request.form.get('digest')
    index_image=request.files.get('index_image')
    content=request.form.get('content')

    if not all([title,category_id,digest,index_image,content]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
    try:
        data=index_image.read()
        path=storage(data)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.IOERR,errmsg='数据读取错误')
    news=News()
    news.title=title
    news.source = '个人'
    news.category_id=category_id
    news.digest=digest
    news.index_image_url=constants.QINIU_DOMIN_PREFIX+path
    news.content=content
    news.user_id=user.id
    news.status=1# 0通过/1审核中/-1未用过

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据库错误')
    return jsonify(errno=RET.OK,errmsg='添加成功')


@profile_bul.route('/news_list_info')
@user_login_data
def news_list_info():
    '''新闻列表'''
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if request.method == "GET":
        try:
            page=request.args.get('page',1)
            page=int(page)
        except Exception as e:
            page=1
        try:
            news_page=News.query.filter(News.user_id==user.id).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
            news=news_page.items
            current_page=news_page.page
            total_page=news_page.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库错误')
        new_list=[]
        for new in news:
            new_list.append(new.to_review_dict())

        data = {
            'user_info': user.to_dict() if user else None,
            'new_list':new_list,
            'current_page':current_page,
            'total_page':total_page
        }
        return render_template('news/user_news_list.html', data=data)
