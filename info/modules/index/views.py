#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-18
from flask import current_app, render_template, session, abort, redirect, url_for, request, jsonify

from info.models import User, News, Category
from info.modules.index import index_blu
from info import constants
from info.response_code import RET


@index_blu.route('/')
def index():
    # 登录状态
    user = None
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 点击排行
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    # 新闻分类
    try:
        categorys = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    category_list = []
    for index, category in enumerate(categorys):
        print(category)
        category_list.append(category.to_dict())

    data = {
        'user_info': user.to_dict() if user else None,
        'clicks_news': clicks_news,
        'categorys': category_list
    }
    return render_template('news/index.html', data=data)


@index_blu.route('/newslist')
def new_list():
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', constants.HOME_PAGE_MAX_NEWS)
    cid = request.args.get('cid', '1')
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 3. 查询数据并分页
    filters = []
    # 如果分类id不为1，那么添加分类id的过滤
    if cid != "1":
        filters.append(News.category_id == cid)
    try:
        news = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        # 页数/当前页
        totalPage = news.pages
        current_page = news.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')

    news_list = []
    for new in news.items:
        news_list.append(new.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='返回数据成功', currentPage=current_page, totalPage=totalPage, newsList=news_list)


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


@index_blu.route('/detail')
def detail():
    # 详情试图
    return 'tetail'
