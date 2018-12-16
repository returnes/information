#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-16

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import creat_app,db
from flask import current_app

# 用Manager类管理app
app=creat_app()
manager=Manager(app)
# 迁移app和db
Migrate(app=app,db=db)
# 将迁移指令添加到Manager类中
manager.add_command('db',MigrateCommand)

@app.route('/')
def index():

    current_app.logger.debug('debug')
    current_app.logger.error('error')
    return "hello"


if __name__ == '__main__':
    # app.run()
    manager.run()
