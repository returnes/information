# Author Caozy
from flask import Blueprint
profile_bul=Blueprint('profile',__name__,url_prefix='/profile')

from . import views