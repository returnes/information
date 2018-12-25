#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-16
import datetime
import random

# from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy

# app=Flask(__name__)
#
# class Config(object):
#     DEBUG=True
#     SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:000000@127.0.0.1:3306/news'
#     SQLALCHEMY_TRACK_MODIFICATIONS=False
#     # SQLALCHEMY_ECHO=True
#
#
# app.config.from_object(Config)
# db=SQLAlchemy(app=app)
#
#
# @app.route('/')
# def index():
#     return 'ok'
from info import db
from info.models import User
from manage import app


def add_test_users():
    users = []
    now = datetime.datetime.now()
    for num in range(0, 10000):
        try:
            user = User()
            user.nick_name = "%011d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    with app.app_context():
        db.session.add_all(users)
        db.session.commit()
    print('OK')



if __name__ == '__main__':
    add_test_users()
    # # app.run()
    # import random
    # base_code = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # sms_code = ''.join(random.sample(base_code, 6))
    # print(sms_code)