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
        self.book_info = book_info
        self.book_id = book_info['book_id']
        self.book_name = book_info['book_name']
        self.author_name = book_info['author_name']
        self.cover = book_info['cover'].replace(' ', '')
        self.last_chapter_info = book_info['last_chapter_info']
        self.pool_sema = threading.BoundedSemaphore(Vars.cfg.data['max_thread'])

    def get_division_list(self):
        response = HbookerAPI.Book.get_division_list(self.book_id)
        if response.get('code') == '100000':
            self.division_list = response['data']['division_list']
            for division in self.division_list:
                print('第{}卷'.format(division['division_index']), '分卷名:', division['division_name'])

    def get_chapter_catalog(self, max_retry=10):
        self.chapter_list.clear()
        for division in self.division_list:
            for retry in range(max_retry):
                response = HbookerAPI.Book.get_chapter_update(division['division_id'])
                if response.get('code') == '100000':
                    self.chapter_list.extend(response['data']['chapter_list'])
                    break
                else:
                    print("code:", response.get('code'), "error:", response.get("tip"))

        self.chapter_list.sort(key=lambda x: int(x['chapter_index']))
        self.show_chapter_latest()

    def show_chapter_latest(self):
        shield_chapter_length = len([i for i in self.chapter_list if i['chapter_title'] == '该章节未审核通过'])
        if shield_chapter_length != 0:
            print("[提示]本书一共有", shield_chapter_length, "章被屏蔽")
        print('[提示]最新章节:', self.chapter_list[-1]['chapter_title'], "\t更新时间:", self.chapter_list[-1]['mtime'])

    def download_chapter(self):
        Config("", Vars.config_text), Config(Vars.out_text_file, Vars.cfg.data['out_path'])
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

    def export_txt(self):
        for file_name in os.listdir(Vars.config_text):
            file_info = write(Vars.config_text + "/" + file_name, 'r')
            with open(Vars.out_text_file, "a", encoding='utf-8') as _file:
                _file.write("\n\n" + file_info)
        print('[提示] 《' + self.book_name + '》下载完成,已导出文件')

    def show_progress(self, current, length):
        self.current_progress += 1
        print('[{} 下载进度]: {}/{}'.format(self.book_name, current, length), end="\r")

    def download_thread(self, chapter_id: str, division_chapter_length: int):
        self.pool_sema.acquire()
        command = HbookerAPI.Chapter.get_chapter_command(chapter_id)['data']['command']
        response2 = HbookerAPI.Chapter.get_cpt_ifm(chapter_id, command)
        if response2.get('code') == '100000' and response2['data']['chapter_info']['chapter_title'] != '该章节未审核通过':
            if response2['data']['chapter_info']['chapter_title'] is None:
                return False
            txt_content = response2['data']['chapter_info']['txt_content']
            with open(Vars.config_text + "/" + chapter_id + ".txt", 'w', encoding='utf-8') as _file:
                _file.write("第"+response2['data']['chapter_info']['chapter_index']+"章: ")
                _file.write(response2['data']['chapter_info']['chapter_title'].replace("#G9uf", "") + "\n")
                _file.write(HbookerAPI.HttpUtil.decrypt(txt_content, command).decode('utf-8'))

            self.show_progress(self.current_progress, division_chapter_length)
            self.pool_sema.release()
        else:
            self.show_progress(self.current_progress, division_chapter_length)
            if response2['data']['chapter_info']['chapter_title'] == '该章节未审核通过':
                print('chapter_id:', chapter_id, ', 该章节为屏蔽章节，不进行下载')
            else:
                print(response2['data']['chapter_info']['chapter_title'], ', 该章节为空章节，标记为已下载')
            self.pool_sema.release()
