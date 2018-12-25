# Author Caozy
from datetime import datetime, timedelta
import time

from info.models import User
from . import admin_blu
from info.utils.common import user_login_data
from flask import render_template, url_for, request, redirect, current_app, session, g


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
    user=g.user
    if not user:
        return redirect(url_for('admin.admin_login'))

    context={
        'user':user.to_dict() if user else None
    }

    return render_template('admin/index.html',context=context)


@admin_blu.route('/user_count')
@user_login_data
def user_count():
    '''用户数量统计页'''
    # 用户总数,不包括超级管理员
    users_count=None
    try:
        users_count=User.query.filter(User.is_admin!=True).count()
    except Exception as e:
        current_app.logger.error(e)
    # 用户月新增数
    mon_count=0
    now=time.localtime()
    try:
        mon_begin='%d-%02d-01'%(now.tm_year,now.tm_mon)
        mon_begin_date=datetime.strptime(mon_begin,'%Y-%m-%d')
        mon_count=User.query.filter(User.is_admin!=True,User.create_time>mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)


    # 用户日新增数
    day_count=0
    try:
        day_begin='%d-%02d-%02d'%(now.tm_year,now.tm_mon,now.tm_mday)
        day_begin_date=datetime.strptime(day_begin,'%Y-%m-%d')
        day_count=User.query.filter(User.is_admin!=True,User.create_time>day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)


    # 查询图表信息，获取到当天00:00:00时间
    now_date=datetime.strptime(datetime.now().strftime('%Y-%m-%d'),'%Y-%m-%d')
    # 定义空数组，保存数据
    active_date=[]
    active_count=[]

    # 依次添加数据，再反转
    for i in range(0,31):
        begin_date=now_date-timedelta(days=i)
        end_date=now_date-timedelta(days=(i-1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count=0
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login <end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)
    active_date.reverse()
    active_count.reverse()
    data={
        'users_count':users_count,
        'mon_count':mon_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count

    }
    return render_template('admin/user_count.html',data=data)


@admin_blu.route('/user_list')
@user_login_data
def user_list():
    '''用户列表'''
    return render_template('admin/user_list.html')



@admin_blu.route('/news_review')
@user_login_data
def news_review():
    '''新闻审核'''
    return render_template('admin/news_review.html')

@admin_blu.route('/news_review_detail')
@user_login_data
def news_review_detail():
    '''新闻审核详情'''
    return render_template('admin/news_review_detail.html')

@admin_blu.route('/news_edit')
@user_login_data
def news_edit():
    '''新闻编辑'''
    return render_template('admin/news_edit.html')

@admin_blu.route('/news_edit_detail')
@user_login_data
def news_edit_detail():
    '''新闻编辑详情'''
    return render_template('admin/news_edit_detail.html')

@admin_blu.route('/news_type')
@user_login_data
def news_type():
    '''新闻分类管理'''
    return render_template('admin/news_type.html')