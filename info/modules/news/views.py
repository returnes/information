# Author Caozy

from info.models import News, Comment
from info.utils.common import user_login_data
from . import news_blu
from flask import render_template, redirect, g, current_app, abort
from info import constants


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    try:
        news=News.query.get_or_404(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    # comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    comment_list = []
    for item in comments:
        comment_dict = item.to_dict()
        comment_list.append(comment_dict)




    data = {
        'new_info':news.to_dict(),
        'clicks_news':clicks_news,
        "user_info": g.user.to_dict() if g.user else None,
        'comment_list':comment_list,
    }
    return render_template('news/detail.html',data=data)