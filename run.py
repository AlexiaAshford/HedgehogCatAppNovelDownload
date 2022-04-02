import sys
import book
from instance import *
import HbookerAPI
import Epub
import re


def shell_bookshelf():
    response = HbookerAPI.BookShelf.get_shelf_list()
    if response.get('code') != '100000':
        print("code:", response.get('code'), "Msg:", response.get("tip"))
        return False
    for shelf in response['data']['shelf_list']:
        print('书架编号:', shelf['shelf_index'], ', 书架名:', shelf['shelf_name'])

    if len(response['data']['shelf_list']) > 1:
        shelf_list = response['data']['shelf_list'][int(get("输入书架编号:").strip()) - 1]
    else:
        shelf_list = response['data']['shelf_list'][0]
        print('检测到账号只有一个书架，已自动选择，书架名:', shelf_list['shelf_name'])

    book_list = HbookerAPI.BookShelf.shelf_list(shelf_list['shelf_id'])
    if book_list.get('code') == '100000':
        for index, data in enumerate(book_list['data']['book_list']):
            Vars.current_bookshelf.append(book.Book(book_info=data['book_info'], index=str(index + 1)))

        for book_info in Vars.current_bookshelf:
            print("\nindex:", book_info.index)
            print('name:', book_info.book_name, " author:", book_info.author_name, " id:", book_info.book_id)
            print("time:", book_info.last_chapter['uptime'], "chapter:", book_info.last_chapter['chapter_title'])

        input_shelf_book_index = get("输入书籍编号:").strip()
        for book_info in Vars.current_bookshelf:
            if book_info.index == input_shelf_book_index:
                shell_download_book(["", book_info.book_id])
        Vars.current_bookshelf.clear()
    else:
        print("code:", book_list.get('code'), "Msg:", book_list.get("tip"))


def shell_login(inputs):
    if len(inputs) >= 3:
        Vars.cfg.data['account_info'] = {'login_name': inputs[1], 'passwd': inputs[2]}
        response = HbookerAPI.SignUp.login(Vars.cfg.data.get('account_info'))
        if response.get('code') == '100000':
            Vars.cfg.data['common_params'] = {
                'login_token': response['data']['login_token'], 'account': response['data']['reader_info']['account']
            }
            HbookerAPI.set_common_params(Vars.cfg.data['common_params'])
            Vars.cfg.save()
            print('登录成功, 当前用户昵称为:', HbookerAPI.SignUp.user_account())
        else:
            print(response.get('tip'))
    else:
        print("当前用户昵称为:", HbookerAPI.SignUp.user_account())


def shell_download_book(inputs):
    if len(inputs) >= 2:
        Vars.current_book = HbookerAPI.Book.get_info_by_id(inputs[1]).get('data')
        if Vars.current_book is not None:
            Vars.current_book = book.Book(book_info=Vars.current_book.get('book_info'))
            print('开始下载书籍《' + Vars.current_book.book_name + '》')
            Vars.current_epub = Epub.EpubFile()
            Vars.current_epub.add_intro()
            Vars.current_book.get_division_list(), Vars.current_book.get_chapter_catalog()
            if len(Vars.current_book.chapter_list) != 0:
                Vars.out_text_file = Vars.cfg.data['out_path'] + Vars.current_book.book_name + '.txt'
                Vars.config_text = Vars.cfg.data['save_path'] + Vars.current_book.book_name
                Vars.current_book.download_chapter()
            else:
                print(Vars.current_book.book_name, "没有需要下载的章节！")
            if Vars.cfg.data['downloaded_book_id_list'].count(Vars.current_book.book_id) == 0:
                Vars.cfg.data['downloaded_book_id_list'].append(Vars.current_book.book_id)
                Vars.cfg.save()
        else:
            print('获取书籍信息失败, book_id:', inputs[1])
    else:
        print('未输入book_id')


def shell_update():
    if len(Vars.cfg.data.get('downloaded_book_id_list')) == 0:
        print('书单暂无可更新书籍，请检查config.json downloaded_book_id_list')
    else:
        for index, book_id in enumerate(Vars.cfg.data['downloaded_book_id_list']):
            shell_download_book([index, book_id])
    print('[提示]书籍更新已完成')


def update_config():
    Vars.cfg.load()
    if Vars.cfg.data.get('common_params') is None:
        Vars.cfg.data['common_params'] = {'login_token': "", 'account': ""}
    if Vars.cfg.data.get('downloaded_book_id_list') is None:
        Vars.cfg.data['downloaded_book_id_list'] = []
    if not isinstance(Vars.cfg.data.get('max_thread'), int):
        Vars.cfg.data['max_thread'] = 32
    if not isinstance(Vars.cfg.data.get('save_path'), str):
        Vars.cfg.data['save_path'] = "./Hbooker/"
    if not isinstance(Vars.cfg.data.get('out_path'), str):
        Vars.cfg.data['out_path'] = "./downloads/"
    Vars.cfg.save()
    HbookerAPI.set_common_params(Vars.cfg.data.get('common_params'))


def tests_account_login():
    if HbookerAPI.SignUp.user_account() is not None:
        print("当前登入账号:", HbookerAPI.SignUp.user_account())
    else:
        if Vars.cfg.data.get('account_info') is not None:
            print("检测到本地配置文件，尝试自动登入...")
            response = HbookerAPI.SignUp.login(Vars.cfg.data['account_info'])
            if response.get('code') == '100000':
                Vars.cfg.data['common_params'] = {
                    'login_token': response['data']['login_token'],
                    'account': response['data']['reader_info']['account']
                }
                HbookerAPI.set_common_params(Vars.cfg.data['common_params'])
                Vars.cfg.save()
                print("账号:", HbookerAPI.SignUp.user_account(), "自动登入成功！")
            else:
                print("登入失败:", response.get('tip'))
        else:
            print("检测到本地配置文件账号信息为空，请手动登入！")


def shell(inputs):
    if inputs[0] == 'q' or inputs[0] == 'quit':
        exit()
    elif inputs[0] == 'l' or inputs[0] == 'login':
        shell_login(inputs)
    elif inputs[0] == 'd' or inputs[0] == 'download':
        shell_download_book(inputs)
    elif inputs[0] == 'bs' or inputs[0] == 'bookshelf':
        shell_bookshelf()
    elif inputs[0] == 'up' or inputs[0] == 'updata':
        shell_update()


if __name__ == '__main__':
    update_config()
    # tests_account_login()
    if len(sys.argv) >= 2:
        shell(sys.argv[1:])
    else:
        for info in Vars.help_info:
            print('[帮助]', info)
        inputs_list = re.split('\\s+', get('>').strip())
        while True:
            shell(inputs_list)
            inputs_list = re.split('\\s+', get('>').strip())
