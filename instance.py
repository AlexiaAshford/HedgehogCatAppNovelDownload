import json
import os
import re


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


class TextFile:
    @staticmethod
    def write(text_path: str = "", text_content: str = "", mode: str = "a") -> [str, None]:
        try:
            with open(text_path, mode, encoding="utf-8") as file:
                file.write(text_content)
        except Exception as error:
            print("[error] text_file.write:", error)

    @staticmethod
    def read(text_path: str = "", split_list: bool = False,
             allow_file_not_found: bool = False) -> [str, None]:
        if allow_file_not_found and not os.path.exists(text_path):
            return None
        try:
            with open(text_path, "r", encoding="utf-8") as file:
                if split_list:
                    return file.read().splitlines()
                return file.read()
        except Exception as error:
            print("[error] text_file.read:", error)


class Vars:
    cfg = Config(os.getcwd() + '/config.json', os.getcwd())
    current_bookshelf = []
    current_book = None
    current_epub = None
    out_text_file = None
    config_text = None
    help_info = [
        'book text file and config file in ./Hbooker/',
        'quit \t\t\t\t exit program',
        'login \t\t\t\t <login_token> <account> \t login hbooker with account',
        'bookshelf \t\t\t\t read bookshelf',
        'bookshelf \t\t\t\t <bookshelf index> \t switch bookshelf',
        'download \t\t\t\t <book id> \t download book',
        'update \t\t\t\t update config.json downloaded_book_id_list',
    ]


def get_id(url: str) -> str:
    result = re.compile(r'(\d+)').findall(url)
    if len(result) > 0 and result[0].isdigit() and len(result[0]) == 9:
        return result[0]
    print("[warning] get_id failed", url)


def makedir_config(file_path, dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    if '.txt' in file_path:
        open(file_path, 'w').close()


def get(prompt, default=None):
    while True:
        ret = input(prompt)
        if ret != '':
            return ret
        elif default is not None:
            return default
