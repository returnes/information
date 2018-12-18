#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-18

from flask import Blueprint

index_blu=Blueprint('index',__name__)

from . import views