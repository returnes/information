#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:18-12-18
from flask import Blueprint

passport_blu=Blueprint('passport',__name__,url_prefix='/passport')

from . import views