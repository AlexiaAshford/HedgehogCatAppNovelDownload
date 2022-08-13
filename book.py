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
        self.author_name = book_info['author_name']
        self.cover = book_info['cover'].replace(' ', '')
        self.last_chapter = book_info['last_chapter_info']
        self.pool_sema = threading.BoundedSemaphore(Vars.cfg.data['max_thread'])
        self.division = None

    @property
    def book_name(self) -> str:  # 删除windows不规范字符
        return re.sub(r'[\\/:*?"<>|]', '', self.book_info['book_name'])

    def book_information(self):
        print('开始下载书籍《' + self.book_name + '》')
        Vars.out_text_file, Vars.config_text = (
            Vars.cfg.data['out_path'] + Vars.current_book.book_name + '.txt',
            Vars.cfg.data['save_path'] + Vars.current_book.book_name)

        makedir_config(dir_path=[Vars.config_text, Vars.cfg.data['out_path']])
        Vars.current_epub = Epub.EpubFile()
        Vars.current_epub.add_book_intro_in_epub()
        print('\n[info] book-name:' + self.book_name)
        print('[info] author-name: ', self.author_name)
        print('[info] book-id:', self.book_id)
        print('[info] new chapter:', self.last_chapter['chapter_title'])
        print('[info] last update:', self.last_chapter['mtime'])
        print('[info] book-cover-url:', self.cover)

    def get_division_list(self) -> bool:  # get division list from hbooker api
        response = HbookerAPI.Book.get_division_list(self.book_id)  # get division list
        if response.get('code') == '100000':
            self.division = catalog.Catalog(response['data']['division_list'])
            self.division.get_division_information()
            self.division.threading_get_chapter_list()
            self.division.show_chapter_latest()
            self.download_chapter_list, self.chapter_list_length = self.division.return_chapter_list()
            return True
        else:
            print('[error] get division list error:', response['tip'])

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

    def save_export_txt_epub(self):  # save export txt and epub file
        with open(Vars.out_text_file, 'w', encoding="utf-8") as f:
            self.division.get_division_list.sort(key=lambda x: int(x['division_index']))
            for division in self.division.get_division_list:
                division_name = division['division_name']
                volume_info = "第{}卷: {}".format(int(division['division_index']), division_name)
                if int(division['division_index']) != 1:  # the division is not the first
                    volume_info = "\n\n" + volume_info
                f.write(volume_info)
                if division['division_id'] in self.division.map:  # the division has chapter list
                    for chapter_index, chapter in enumerate(self.division.map[division['division_id']], start=1):
                        chapter_id, chapter_title = chapter['chapter_id'], chapter['chapter_title']
                        file_info = TextFile.read(text_path=f"{Vars.config_text}/{chapter_id}.txt", split_list=True,
                                                  allow_file_not_found=True)
                        # If file not found, this mean the chapter need to buy or the chapter is not approved.
                        if file_info is None:
                            file_info = [f"第{chapter_index}章: {chapter_title}",
                                         "未购买章节" if chapter_title != "该章节未审核通过" else f"{chapter_title}(章节ID：{chapter_id})"]
                        if chapter_title == '该章节未审核通过':  # the chapter is not approved
                            chapter_title = file_info[0].split(':', 1)[1].lstrip()
                        file_info[0] = "第{}章: {}".format(chapter_index, chapter_title)
                        f.write("\n\n" + "\n".join(file_info))
                        Vars.current_epub.add_chapter_in_epub_file(chapter_title, file_info[1:], str(chapter_id),
                                                                   division_name)
                else:
                    print("[warning] the division has no chapter list", division['division_id'])
        Vars.current_epub.download_cover_and_add_epub()  # download cover and add to epub file
        Vars.current_epub.save_epub_file()  # save epub file to local
        print('[提示] 《' + self.book_name + '》下载完成,已导出文件')  # show msg

    def show_progress(self):  # show progress of download chapter
        self.current_progress += 1  # add progress count by 1
        print('[{} 下载进度]: {}/{}'.format(
            self.book_name,
            self.current_progress,
            self.chapter_list_length
        ), end="\r")  # show progress of download chapter

    def download_threading(self, chapter_id: str, command_key: str):
        self.pool_sema.acquire()  # acquire semaphore to avoid threading conflict
        self.show_progress()  # show progress of download chapter
        response2 = HbookerAPI.Chapter.get_cpt_ifm(chapter_id, command_key)
        if response2.get('code') == '100000' and response2['data']['chapter_info'][
            'chapter_title'] != '该章节未审核通过':
            if response2['data']['chapter_info']['chapter_title'] is None:
                self.pool_sema.release()  # release semaphore when chapter_title is None
                return False
            write_content = "第" + response2['data']['chapter_info']['chapter_index'] + "章: "
            write_content += response2['data']['chapter_info']['chapter_title'] + "\n"
            write_content += HbookerAPI.HttpUtil.decrypt(
                response2['data']['chapter_info']['txt_content'], command_key).decode('utf-8')
            TextFile.write(text_path=Vars.config_text + "/" + chapter_id + ".txt", text_content=write_content)

            self.pool_sema.release()  # release semaphore to avoid threading conflict when download finished
        else:
            if response2['data']['chapter_info']['chapter_title'] == '该章节未审核通过':  # the chapter is not approved
                print('chapter_id:', chapter_id, ', 该章节为屏蔽章节，不进行下载')
            else:
                print(response2['data']['chapter_info']['chapter_title'], ', 该章节为空章节，标记为已下载')
            self.pool_sema.release()  # release semaphore to avoid threading conflict
