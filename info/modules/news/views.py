# Author Caozy

from info.models import News, Comment, CommentLike, User
from info.response_code import RET
from info.utils.common import user_login_data
from . import news_blu
from flask import render_template, redirect, g, current_app, abort, jsonify, request
from info import constants, db


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    '''详情页面'''
    try:
        news = News.query.get_or_404(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return abort(404)
    comment_like_ids = []
    if g.user:
        try:
            comment_ids=[comment.id for comment in comments]
            if len(comment_ids)>0:
                #获取当前用户所在当前新闻所有评论点赞的记录
                comment_likes=CommentLike.query(CommentLike.comment_id.in_(comment_ids),CommentLike.user_id==g.user.id).all()
                #取出记录中所有评论id
                comment_like_ids=[comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comment_list=[]
    for item in comments if comments else []:
        comment_dict = item.to_dict()
        comment_dict['is_like']=False
        if g.user and item.id in comment_like_ids:
            comment_dict['is_like']=True
        comment_list.append(comment_dict)

    ##########################以下是 判断用户是否收藏##########################################
    is_collected = False
    is_followed = False  # 都没有关注
    if g.user:
        # user.collection_news
        # [News,News,News,...]
        if news in g.user.collection_news:
            is_collected = True

        try:
            news_user = User.query.get(news.user_id)
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='查询失败')
        # news_user 是发布新闻的作者
        # user 是登陆的用户
        #
        if news_user in g.user.followers:
            is_followed = True

    data = {
        'new_info': news.to_dict(),
        'clicks_news': clicks_news,
        "user_info": g.user.to_dict() if g.user else None,
        'comment_list': comment_list,
        'is_collected': is_collected,
        'is_followed':is_followed

    }
    return render_template('news/detail.html', data=data)


@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    '''收藏'''
    user = g.user
    news_id = request.json.get('new_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if action not in ('collect', 'cancel_collect'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        new = News.query.get(news_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')
    if not new:
        return jsonify(errno=RET.NODATA, errmsg='无数据')
    if action == "collect":
        user.collection_news.append(new)
    else:
        user.collection_news.remove(new)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据错误')
    return jsonify(errno=RET.OK, errmsg='操作成功')


@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    user = g.user
    new_id = request.json.get('new_id')
    comments = request.json.get('comments')
    parent_id = request.json.get('parent_id')

    if not ([new_id, comments, parent_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    try:
        new = News.query.get(new_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')
    if not new:
        return jsonify(errno=RET.NODATA, errmsg='没有数据')
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = new_id
    comment.content = comments
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据保存失败')
    return jsonify(errno=RET.OK, errmsg='保存成功', data=comment.to_dict())


@news_blu.route('/comment_like',methods=['POST'])
@user_login_data
def comment_like():
    user = g.user
    # new_id=request.json.get('new_id')
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg='未登录')
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    if action not in ('add', 'remove'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="无数据")
    try:
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                CommentLike.user_id == user.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')
    if action == 'add':
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment.like_count += 1
    if action == 'remove':
        if comment_like:
            db.session.delete(comment_like)
            comment.like_count -= 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')
    return jsonify(errno=RET.OK, errmsg='成功')

@news_blu.route('/followed_user', methods=["POST"])
@user_login_data
def followed_user():
    if not g.user:
        return jsonify(errno=RET.SESSIONERR,errmsg='请登录')
    user_id=request.json.get('user_id')
    action=request.json.get('action')
    if not all([user_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
    if action not in (['follow','unfollow']):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    try:
        taget_user=User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库错误')
    if not taget_user:
        return jsonify(errno=RET.NODATA,errmsg='无数据')
    if action=='follow':
        if taget_user.followers.filter(User.id==g.user.id).count()>0:
            return jsonify(errno=RET.DATAEXIST,errmsg='已经关注')
        taget_user.followers.append(g.user)
    else:
        if taget_user.followers.filter(User.id==g.user.id).count()>0:
            taget_user.followers.remove(g.user)

    try:
        db.session.commit()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存错误")

    return jsonify(errno=RET.OK, errmsg="操作成功")





