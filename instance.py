import json
import os


class Config:
    file_path = None
    dir_path = None
    data = None

    def __init__(self, file_path, dir_path):
        self.file_path = file_path
        self.dir_path = dir_path
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        if '.txt' in file_path:
            open(self.file_path, 'w').close()
        self.data = {}

    def load(self):
        try:
            with open(self.file_path, 'r', encoding="utf-8") as f:
                self.data = json.load(f) or {}
        except FileNotFoundError:
            try:
                open(self.file_path, 'w', encoding="utf-8").close()
            except Exception as e:
                print('[错误]', e)
                print('创建配置文件时出错')
        except Exception as e:
            print('[错误]', e)
            print('读取配置文件时出错')

    def save(self):
        try:
            with open(self.file_path, 'w', encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print('[错误]', e)
            print('保存配置文件时出错')


class Vars:
    cfg = Config(os.getcwd() + '/config.json', os.getcwd())
    current_bookshelf = []
    current_book = None
    current_epub = None
    out_text_file = None
    config_text = None
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
