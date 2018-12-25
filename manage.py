#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-16

from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import creat_app, db
from info import models

# 用Manager类管理app
from info.models import User

app = creat_app()
manager = Manager(app)
# 迁移app和db
Migrate(app=app, db=db)
# 将迁移指令db添加到Manager类中
manager.add_command('db', MigrateCommand)

# 使用flask-script扩展添加命令行相关逻辑
@manager.option('-n','-name',dest='name')
@manager.option('-p','-password',dest='password')
def createsuperuser(name,password):
    '''创建管理员'''
    if not all([name,password]):
        print('参数不足')
        return
    user=User()
    user.mobile=name
    user.nick_name=name
    user.password=password
    user.is_admin=True
    try:
        db.session.add(user)
        db.session.commit()
        print('创建成功')
    except Exception as e:
        print(e)
        db.session.rollback()




if __name__ == '__main__':
    # app.run()
    manager.run()
