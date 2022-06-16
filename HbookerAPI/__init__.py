from HbookerAPI import HttpUtil, UrlConstants
from instance import *

headers = {'User-Agent': 'Android Android com.kuangxiangciweimao.novel'}


def compared_version(ver1, ver2="2.9.281"):
    list1, list2 = (str(ver1).split("."), str(ver2).split("."))  # 循环次数为短的列表的len
    for i in range(len(list1)) if len(list1) < len(list2) else range(len(list2)):
        if int(list1[i]) == int(list2[i]):
            pass
        elif int(list1[i]) < int(list2[i]):
            return True
        else:
            return False
    # 循环结束，哪个列表长哪个版本号高
    if len(list1) == len(list2):
        return False
    elif len(list1) < len(list2):
        return True
    else:
        return False


def get(api_url: str, params: dict = None, **kwargs):
    if params is None:
        params = Vars.cfg.data['common_params']
    if params is not None:
        params.update(Vars.cfg.data['common_params'])
    if compared_version(Vars.cfg.data.get("common_params").get('app_version')):
        api_url = UrlConstants.HBOOKER + api_url.replace(UrlConstants.HBOOKER, '')
    else:
        api_url = UrlConstants.HAPPY + api_url.replace(UrlConstants.HAPPY, '')
    return HttpUtil.get(api_url, params=params, headers=headers, **kwargs)


def post(api_url: str, data: dict = None, **kwargs):
    if data is None:
        data = Vars.cfg.data['common_params']
    if data is not None:
        data.update(Vars.cfg.data['common_params'])
    if compared_version(Vars.cfg.data.get("common_params").get('app_version')):
        api_url = UrlConstants.HBOOKER + api_url.replace(UrlConstants.HBOOKER, '')
    else:
        api_url = UrlConstants.HAPPY + api_url.replace(UrlConstants.HAPPY, '')
    # print(api_url, headers, data)
    return HttpUtil.post(api_url, params=data, headers=headers, **kwargs)


class SignUp:
    @staticmethod
    def login(account_info: dict):
        return post(UrlConstants.MY_SIGN_LOGIN, data=account_info)

    @staticmethod
    def user_account():
        response = get(UrlConstants.MY_DETAILS_INFO)
        if response.get('code') == '100000':
            return response.get('data').get('reader_info').get('reader_name')
        else:
            print("Error:", response.get('tip'), "请先登入账号！")


class BookShelf:
    @staticmethod
    def get_shelf_list():
        """you can change the params to get the book list"""
        return post(UrlConstants.BOOKSHELF_GET_SHELF_LIST)

    @staticmethod
    def shelf_list(shelf_id: str, last_mod_time: str = '0', direction: str = 'prev'):
        data = {'shelf_id': shelf_id, 'last_mod_time': last_mod_time, 'direction': direction}
        return post(UrlConstants.BOOKSHELF_GET_SHELF_BOOK_LIST, data)


class Book:
    @staticmethod
    def get_division_list(book_id: str):
        return get(UrlConstants.GET_DIVISION_LIST, {'book_id': book_id})

    @staticmethod
    def get_chapter_update(division_id: str, update_time: str = '0'):
        return post(UrlConstants.GET_CHAPTER_UPDATE, {'division_id': division_id, 'last_update_time': update_time})

    @staticmethod
    def get_info_by_id(book_id: str):
        data = {'book_id': book_id, 'recommend': '', 'carousel_position': '', 'tab_type': '', 'module_id': ''}
        return post(UrlConstants.BOOK_GET_INFO_BY_ID, data)


class Chapter:
    @staticmethod
    def get_chapter_command(chapter_id: str):
        return get('chapter/get_chapter_command', {'chapter_id': chapter_id})

    @staticmethod
    def get_cpt_ifm(chapter_id: str, chapter_command: str):
        return get('chapter/get_cpt_ifm', {'chapter_id': chapter_id, 'chapter_command': chapter_command})
