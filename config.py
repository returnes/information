#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-16
import logging
from redis import StrictRedis


# 配置文件
class Config(object):
    # debug模式配置
    # DEBUG=True
    LOG_LEVEL = logging.DEBUG
    # mysql 配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:000000@127.0.0.1:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    # redis 配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # session 配置
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,db=1)
    PERMANENT_SESSION_LIFETIME = 3600
    SECRET_KEY = 'KZtgoZECnZyp/hiU49YHotf2Nv4IGYqF5I7M6K3iClzvTWYtALha9E2i7wgIK78X'


# 开发环境
class DevelopmentConfig(Config):
    DEBUG = True


# 生产环境
class ProductionConfig(Config):
    DEBUG = False


# 定义一个字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
