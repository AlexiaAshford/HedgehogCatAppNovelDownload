from config import *


class Vars:
    cfg = Config(os.getcwd() + '/config.json', os.getcwd())
    current_bookshelf = None
    current_book = None
    out_text_file = None
    help_info = [
        '下载的书籍文件、缓存和配置文件在./Hbooker/下',
        'quit \t\t\t\t 退出脚本',
        'login \t\t\t\t <用户名> <密码> \t 登录欢乐书客帐号',
        'help \t\t\t\t 用法与帮助',
        'bookshelf \t\t\t 刷新并显示第一个书架列表',
        'bookshelf \t\t\t <书架编号> \t 切换书架',
        'download \t\t\t <书籍编号/书籍ID> \t 下载到最后章节为止',
        'update \t\t\t\t 更新已下载的所有书籍并复制到updates文件夹'
    ]


def write(file_path, mode='', data=''):
    if mode == 'r' or 'r' in mode:
        return open(file_path, 'r', encoding='utf-8').read()
    with open(file_path, mode, encoding='utf-8') as _file:
        _file.write(data)


def get(prompt, default=None):
    while True:
        ret = input(prompt)
        if ret != '':
            return ret
        elif default is not None:
            return default
