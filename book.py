import Epub
import threading
import HbookerAPI
import catalog
from instance import *


class Book:

    def __init__(self, book_info, index=None):
        self.index = index
        self.chapter_list_length = 0
        self.current_progress = 0
        self.download_chapter_list = []
        self.book_info = book_info
        self.book_id = book_info['book_id']
        self.book_name = book_info['book_name']
        self.author_name = book_info['author_name']
        self.cover = book_info['cover'].replace(' ', '')
        self.last_chapter = book_info['last_chapter_info']
        self.pool_sema = threading.BoundedSemaphore(Vars.cfg.data['max_thread'])

    def book_information(self):
        Vars.current_epub = Epub.EpubFile()
        Vars.current_epub.add_intro()  # add intro to epub
        print('\n[info] book-name:' + self.book_name)
        print('[info] author-name: ', self.author_name)
        print('[info] book-id:', self.book_id)
        print('[info] new chapter:', self.last_chapter['chapter_title'])
        print('[info] last update:', self.last_chapter['mtime'])
        print('[info] book-cover-url:', self.cover)

    def get_division_list(self):
        self.book_information()
        response = HbookerAPI.Book.get_division_list(self.book_id)  # get division list
        if response.get('code') == '100000':
            division = catalog.Catalog(response['data']['division_list'])
            division.get_division_information()
            division.threading_get_chapter_list()
            division.show_chapter_latest()
            self.download_chapter_list, self.chapter_list_length = division.return_chapter_list()
            return True
        else:
            return print("[warning] get division list error code:", response.get('code'))

    def start_download_chapter(self):  # start download chapter and save to txt
        # create threading to download chapter and save to txt and epub file
        threading_list = list()
        for chapter_id, command_key in self.download_chapter_list:  # download chapter
            thread = threading.Thread(target=self.download_threading, args=(chapter_id, command_key,))
            threading_list.append(thread)  # add thread to threading_list

        for thread in threading_list:  # start threading
            thread.start()

        for thread in threading_list:  # wait for all threads to finish
            thread.join()

        threading_list.clear()  # clear threading list after all threads finished

    def save_export_txt_epub(self):  # save export txt and epub
        for chapter_index, file_name in enumerate(os.listdir(Vars.config_text)):
            file_info = write(Vars.config_text + "/" + file_name, 'r')
            with open(Vars.out_text_file, "a", encoding='utf-8') as _file:
                _file.write("\n\n" + file_info)
            content_splitlines = file_info.splitlines()
            if content_splitlines:
                Vars.current_epub.add_chapter_in_epub_file(
                    content_splitlines[0], content_splitlines[1:], str(chapter_index)
                )
        Vars.current_epub.download_cover_and_add_epub()
        Vars.current_epub.save_epub_file()
        print('[提示] 《' + self.book_name + '》下载完成,已导出文件')  # show msg

    def show_progress(self):  # show progress
        self.current_progress += 1  # add progress count by 1
        print('[{} 下载进度]: {}/{}'.format(
            self.book_name,
            self.current_progress,
            self.chapter_list_length
        ), end="\r")  # show progress of download chapter

    def download_threading(self, chapter_id: str, command_key: str):
        self.pool_sema.acquire()  # acquire semaphore to avoid threading conflict
        response2 = HbookerAPI.Chapter.get_cpt_ifm(chapter_id, command_key)
        if response2.get('code') == '100000' and response2['data']['chapter_info']['chapter_title'] != '该章节未审核通过':
            if response2['data']['chapter_info']['chapter_title'] is None:
                self.pool_sema.release()  # release semaphore when chapter_title is None
                return False
            txt_content = response2['data']['chapter_info']['txt_content']
            with open(Vars.config_text + "/" + chapter_id + ".txt", 'w', encoding='utf-8') as _file:
                _file.write("第" + response2['data']['chapter_info']['chapter_index'] + "章: ")
                _file.write(response2['data']['chapter_info']['chapter_title'] + "\n")
                _file.write(HbookerAPI.HttpUtil.decrypt(txt_content, command_key).decode('utf-8'))
            self.show_progress()
            self.pool_sema.release()
        else:
            self.show_progress()
            if response2['data']['chapter_info']['chapter_title'] == '该章节未审核通过':
                print('chapter_id:', chapter_id, ', 该章节为屏蔽章节，不进行下载')
            else:
                print(response2['data']['chapter_info']['chapter_title'], ', 该章节为空章节，标记为已下载')
            self.pool_sema.release()  # release semaphore to avoid threading conflict
