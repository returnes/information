#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-18
from datetime import datetime

from flask import request, current_app, jsonify, make_response, session, redirect, url_for

from info.models import User
from info.utils.captcha.captcha import captcha
from info.modules.passport import passport_blu
from info import redis_store, db
from info import constants
from info.response_code import RET
from info.lib.yuntongxun.sms import CCP
import re
import random


# 获取验证码
@passport_blu.route('/get_captcha')
def get_image_code():
    code_id = request.args.get('code_id')
    name, text, image = captcha.generate_captcha()
    try:
        redis_store.setex('img_' + code_id, constants.SMS_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis保存失败')
    current_app.logger.info(text)
    response = make_response(image)
    response.headers['content-type'] = 'image/jpeg'
    return response


# 短信验证
@passport_blu.route('/sms_code',methods=['POST'])
def send_sms_code():
    # 2. 后端要接收数据(json)
    # 接收 json数据
    data = request.json
    mobile=data.get('mobile')
    image_code=data.get('image_code')
    image_code_id=data.get('image_code_id')
    # 判断是否全部有值
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.NODATA, errmsg='参数不全')
    # 判断手机号格式
    if not re.match(r'1[3-9]\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')
    # 判断手机号是否已经注册
    user_count = User.query.filter_by(mobile=mobile).count()
    if user_count > 0:
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经注册过')
    try:
        redis_code = redis_store.get('img_' + image_code_id)
        if redis_code:
            redis_code = redis_code.decode()
            # redis 中认证后删除该记录
            redis_store.delete('img_'+ image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='redis数据错误')
    if not redis_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')

    if image_code.lower() != redis_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='验证码不一致')

    # 生成6位验证码
    # base_code = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # sms_code = ''.join(random.sample(base_code, 6))
    sms_code = '%06d' % random.randint(0, 999999)
    result=CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    current_app.logger.info(sms_code)
    try:
        redis_store.setex('sms_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='发送失败')
    return jsonify(errno=RET.OK, errmsg='发送成功')


# 注册
@passport_blu.route('/register',methods=['POST'])
def register():
    mobile=request.json.get('mobile')
    smscode=request.json.get('sms_code')
    password=request.json.get('password')
    if not all([mobile,smscode,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
    try:
        redis_sms_code=redis_store.get('sms_'+mobile)
        if redis_sms_code.decode()==smscode:
            redis_store.delete('sms'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='redis错误')
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')
    if redis_sms_code.decode()!=smscode:
        return jsonify(errno=RET.DATAERR,errmsg='验证码不一致 ')

    user = User()
    user.mobile=mobile
    user.nick_name=mobile
    user.password=password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据保存失败')
    session['user_id']=user.id
    session['mobile']=mobile
    session['nick_name']=mobile
    return jsonify(errno=RET.OK,errmsg='注册成功')


# 登录
@passport_blu.route('/login',methods=['POST'])
def login():
    mobile=request.json.get('mobile')
    password=request.json.get('password')

    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    try:
        user=User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库错误')
    if not user:
        return jsonify(errno=RET.NODATA,errmsg='请先注册')
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR,errmsg='用户名或密码错误')
    session['user_id']=user.id
    session['mobile']=mobile
    session['nick_name']=mobile
    user.last_login=datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据错误')

    return jsonify(errno=RET.OK,errmsg='登录成功')


@passport_blu.route('/logout/<int:id>')
def logout(id=None):
    user_id=session.get('user_id')
    if id==user_id:
        session['user_id']=''
        session['mobile']=''
        session['nick_name']=''
        session['is_admin']=False
        # session.pop('user_id', None)
        # session.pop('nick_name', None)
        # session.pop('mobile', None)
        # del session['user_id']
    return redirect(url_for('index.index'))