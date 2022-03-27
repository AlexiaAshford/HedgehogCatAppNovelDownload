import threading
import HbookerAPI
from instance import *
import shutil


class Book:

    def __init__(self, book_info, index=None, ):
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
        print('正在获取书籍分卷...')
        response = HbookerAPI.Book.get_division_list(self.book_id)
        if response.get('code') == '100000':
            self.division_list = response['data']['division_list']

    def show_division_list(self):
        for division in self.division_list:
            print('分卷编号:', division['division_index'], ', 分卷名:', division['division_name'])

    def get_chapter_catalog(self):
        print('正在获取书籍目录...')
        self.chapter_list.clear()
        for division in self.division_list:
            response = HbookerAPI.Book.get_chapter_update(division['division_id'])
            if response.get('code') == '100000':
                self.chapter_list.extend(response['data']['chapter_list'])
                self.division_chapter_list[division['division_name']] = response['data']['chapter_list']
        self.chapter_list.sort(key=lambda x: int(x['chapter_index']))

    def show_chapter_latest(self):
        print('\t最新章节: \t章节编号:', self.chapter_list[-1]['chapter_index'], ', 章节标题:',
              self.chapter_list[-1]['chapter_title'])

    def download_chapter(self, copy_dir=None):
        if len(self.chapter_list) == 0:
            print('暂无书籍目录')
            return

        Vars.out_text_file = os.path.join(os.getcwd(), 'downloads', self.book_name + '.txt')
        Vars.config_text = os.path.join(os.getcwd(), 'Hbooker', self.book_name)
        Config("", Vars.config_text)
        for index, data in enumerate(self.chapter_list):
            if data['chapter_id'] + '.txt' in os.listdir(Vars.config_text) or data['auth_access'] == '0':
                continue
            thread = threading.Thread(target=self.download_single, args=(data['chapter_id'], len(self.chapter_list),))
            self.threading_list.append(thread)

        for thread in self.threading_list:
            thread.start()

        for thread in self.threading_list:
            thread.join()
        self.export_txt()
        if Vars.cfg.data.get('copy_start'):
            self.copy_file(copy_dir)
        print('[提示][下载]', '《' + self.book_name + '》下载已完成')

    def export_txt(self):
        Config(Vars.out_text_file, "./downloads")
        for file_name in os.listdir(Vars.config_text):
            file_info = write(os.getcwd() + '/Hbooker/' + Vars.current_book.book_name + "/" + file_name, 'r')
            write(Vars.out_text_file, "a", file_info)

    def copy_file(self, copy_dir: str):
        try:
            if copy_dir is not None:
                copy_dir = copy_dir.replace("?", "？")
                file_dir, file_name = os.path.split(Vars.out_text_file)
                if not os.path.isdir(copy_dir):
                    os.makedirs(copy_dir)
                shutil.copyfile(Vars.out_text_file, copy_dir + '/' + file_name)
                shutil.copyfile(Vars.out_text_file, copy_dir + '/' + Vars.out_text_file)
        except Exception as e:
            print('[错误]', e)
            print('复制文件时出错')

    def download_single(self, chapter_id: str, division_chapter_length: int):
        self.pool_sema.acquire()
        response = HbookerAPI.Chapter.get_chapter_command(chapter_id)
        response2 = HbookerAPI.Chapter.get_cpt_ifm(chapter_id, response['data']['command'])
        if response2.get('code') == '100000' and response2['data']['chapter_info'].get('chapter_title') is not None:
            self.current_progress += 1
            print('[下载进度]: {}/{}'.format(self.current_progress, division_chapter_length), end="\r")
            title = response2['data']['chapter_info']['chapter_title'].replace("#G9uf", "")
            content = HbookerAPI.CryptoUtil.decrypt(
                response2['data']['chapter_info']['txt_content'], response['data']['command']).decode('utf-8')

            write(Vars.config_text + "/" + chapter_id + ".txt", 'w',
                  "{}\n{}\n{}".format(title, content, response2['data']['chapter_info']['author_say'])
                  )

            self.pool_sema.release()
            return True
        else:
            print('[提示][下载]chapter_id:', chapter_id, ', 该章节为空章节，标记为已下载')
            self.pool_sema.release()
            return True
