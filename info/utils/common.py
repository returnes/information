# Author Caozy

# template_filter:可理解过模板过滤
from flask import session, g



def do_index_class(index):
    click_dict = {0: 'first', 1: 'second', 2: 'third'}
    if index < 3:
        return click_dict[index]
    else:
        return ''


import functools
def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            from info.models import User
            user = User.query.get(user_id)
        g.user = user
        return f(*args, **kwargs)

    return wrapper
