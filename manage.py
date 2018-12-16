#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-16

from flask import Flask

app=Flask(__name__)


@app.route('/')
def index():
    return "hello"

if __name__ == '__main__':
    app.run(debug=True)