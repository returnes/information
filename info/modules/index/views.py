#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-18
from flask import current_app, render_template, session

from info.models import User, News
from info.modules.index import index_blu
from info import constants


@index_blu.route('/')
def index():
    user = None
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    clicks_news=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    data = {
        'user_info': user.to_dict() if user else None,
        'clicks_news':clicks_news
        }
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


@index_blu.route('/detail')
def detail():
    # 详情试图
    return 'tetail'
