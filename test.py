#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-16

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

class Config(object):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:000000@127.0.0.1:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # SQLALCHEMY_ECHO=True


app.config.from_object(Config)
db=SQLAlchemy(app=app)


@app.route('/')
def index():
    return 'ok'

if __name__ == '__main__':
    # app.run()
    import random
    base_code = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    sms_code = ''.join(random.sample(base_code, 6))
    print(sms_code)