# Author Caozy

# template_filter:可理解过模板过滤

def do_index_class(index):
    click_dict = {0: 'first', 1: 'second', 2: 'third'}
    if index < 3:
        return click_dict[index]
    else:
        return ''

