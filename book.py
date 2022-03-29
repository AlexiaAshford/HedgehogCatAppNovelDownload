import threading
import HbookerAPI
from instance import *


class Book:

    def __init__(self, book_info, index=None):
        self.index = index
        self.current_progress = 0
        self.threading_list = []
        self.division_list = []
        self.chapter_list = []
        self.division_chapter_list = {}
        self.book_info = book_info
        self.book_id = book_info['book_id']
        self.book_name = book_info['book_name']
        self.author_name = book_info['author_name']
        self.cover = book_info['cover'].replace(' ', '')
        self.last_chapter_info = book_info['last_chapter_info']
        self.pool_sema = threading.BoundedSemaphore(32)

    def get_division_list(self):
        response = HbookerAPI.Book.get_division_list(self.book_id)
        if response.get('code') == '100000':
            self.division_list = response['data']['division_list']

    def show_division_list(self):
        print("开始加载目录信息...")
        for division in self.division_list:
            print('第{}卷'.format(division['division_index']), '分卷名:', division['division_name'])

    def get_chapter_catalog(self):
        self.chapter_list.clear()
        self.show_division_list()
        for division in self.division_list:
            response = HbookerAPI.Book.get_chapter_update(division['division_id'])
            if response.get('code') == '100000':
                self.chapter_list.extend(response['data']['chapter_list'])
                self.division_chapter_list[division['division_name']] = response['data']['chapter_list']
        self.chapter_list.sort(key=lambda x: int(x['chapter_index']))
        self.show_chapter_latest()

    def show_chapter_latest(self):
        print('章节编号:', self.chapter_list[-1]['chapter_index'], ', 章节标题:', self.chapter_list[-1]['chapter_title'])

    def download_chapter(self):
        Config("", Vars.config_text), Config(Vars.out_text_file, "./downloads")
        for index, data in enumerate(self.chapter_list):
            if data['chapter_id'] + '.txt' in os.listdir(Vars.config_text) or data['auth_access'] == '0':
                continue
            thread = threading.Thread(target=self.download_thread, args=(data['chapter_id'], len(self.chapter_list),))
            self.threading_list.append(thread)

        for thread in self.threading_list:
            thread.start()

        for thread in self.threading_list:
            thread.join()
        self.export_txt()
        print('[提示][下载]', '《' + self.book_name + '》下载完成,已导出文件')

    def export_txt(self):
        for file_name in os.listdir(Vars.config_text):
            file_info = write(Vars.config_text + "/" + file_name, 'r')
            write(Vars.out_text_file, "a", "\n\n" + file_info)

    def show_progress(self, current, length):
        self.current_progress += 1
        print('[{} 下载进度]: {}/{}'.format(self.book_name, current, length), end="\r")

    def download_thread(self, chapter_id: str, division_chapter_length: int):
        self.pool_sema.acquire()
        response = HbookerAPI.Chapter.get_chapter_command(chapter_id)
        response2 = HbookerAPI.Chapter.get_cpt_ifm(chapter_id, response['data']['command'])
        if response2.get('code') == '100000' and response2['data']['chapter_info']['chapter_title'] is not None:
            chapter_info = response2['data']['chapter_info']
            chapter_title = "第" + chapter_info['chapter_index'] + "章: " + chapter_info['chapter_title']
            chapter_content = HbookerAPI.CryptoUtil.decrypt(chapter_info['txt_content'], response['data']['command'])
            chapter_info = "{}\n{}".format(chapter_title.replace("#G9uf", ""), chapter_content.decode('utf-8'))
            write(Vars.config_text + "/" + chapter_id + ".txt", 'w', chapter_info)
            self.show_progress(self.current_progress, division_chapter_length)
            self.pool_sema.release()
        else:
            self.show_progress(self.current_progress, division_chapter_length)
            print('[提示][下载]chapter_id:', chapter_id, ', 该章节为空章节，标记为已下载')
            self.pool_sema.release()
