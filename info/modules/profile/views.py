# Author Caozy
from flask import render_template, g, request

from . import profile_bul
from info.utils.common import user_login_data

@profile_bul.route('/info')
@user_login_data
def get_user_info():
    '''用户中心'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_base_info.html',data=data)


@profile_bul.route('/pic_info')
@user_login_data
def pic_info():
    '''头像设置'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_pic_info.html',data=data)


@profile_bul.route('/follow_info')
@user_login_data
def follow_info():
    '''我的关注'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_follow.html',data=data)

@profile_bul.route('/pass_info')
@user_login_data
def pass_info():
    '''密码修改'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_pass_info.html',data=data)
@profile_bul.route('/collection_info')
@user_login_data
def collection_info():
    '''我的收藏'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_collection.html',data=data)
@profile_bul.route('/news_release_info')
@user_login_data
def news_release_info():
    '''新闻发布'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_news_release.html',data=data)

@profile_bul.route('/news_list_info')
@user_login_data
def news_list_info():
    '''新闻列表'''
    user=g.user
    if request.method=="GET":
        data={
            'user_info':user.to_dict() if user else None
        }
        return render_template('news/user_news_list.html',data=data)