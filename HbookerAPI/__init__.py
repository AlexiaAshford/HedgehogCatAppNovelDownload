from HbookerAPI import HttpUtil, UrlConstants
from instance import *


def get(api_url: str, params: dict = None, **kwargs):
    if params is None:
        params = Vars.cfg.data['common_params']
    if params is not None:
        params.update(Vars.cfg.data['common_params'])
    api_url = UrlConstants.WEB_SITE + api_url.replace(UrlConstants.WEB_SITE, '')
    return HttpUtil.get(api_url, params=params, **kwargs)


def post(api_url: str, data: dict = None, **kwargs):
    if data is None:
        data = Vars.cfg.data['common_params']
    if data is not None:
        data.update(Vars.cfg.data['common_params'])
    api_url = UrlConstants.WEB_SITE + api_url.replace(UrlConstants.WEB_SITE, '')
    return HttpUtil.post(api_url, data=data, **kwargs)


class SignUp:
    @staticmethod
    def login(account_info: dict):
        return post(UrlConstants.MY_SIGN_LOGIN, data=account_info)

    @staticmethod
    def user_account():
        response = post(UrlConstants.MY_DETAILS_INFO)
        if response.get('code') == '100000':
            return response.get('data').get('reader_info').get('reader_name')
        else:
            print("Error:", response.get('tip'), "请先登入账号！")


class BookShelf:
    @staticmethod
    def get_shelf_list():
        return post(UrlConstants.BOOKSHELF_GET_SHELF_LIST)

    @staticmethod
    def shelf_list(shelf_id: str, last_mod_time: str = '0', direction: str = 'prev'):
        data = {'shelf_id': shelf_id, 'last_mod_time': last_mod_time, 'direction': direction}
        return post(UrlConstants.BOOKSHELF_GET_SHELF_BOOK_LIST, data)


class Book:
    @staticmethod
    def get_division_list(book_id: str):
        data = {'book_id': book_id}
        return get(UrlConstants.GET_DIVISION_LIST, data)

    @staticmethod
    def get_chapter_update(division_id: str, last_update_time: str = '0'):
        data = {'division_id': division_id, 'last_update_time': last_update_time}
        return post(UrlConstants.GET_CHAPTER_UPDATE, data)

    @staticmethod
    def get_info_by_id(book_id: str):
        data = {'book_id': book_id, 'recommend': '', 'carousel_position': '', 'tab_type': '', 'module_id': ''}
        return post(UrlConstants.BOOK_GET_INFO_BY_ID, data)


class Chapter:
    @staticmethod
    def get_chapter_command(chapter_id: str):
        data = {'chapter_id': chapter_id}
        return get('chapter/get_chapter_command', data)

    @staticmethod
    def get_cpt_ifm(chapter_id: str, chapter_command: str):
        data = {'chapter_id': chapter_id, 'chapter_command': chapter_command}
        return get('chapter/get_cpt_ifm', data)
