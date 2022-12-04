from instance import *
import HbookerAPI
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor


class Catalog:
    def __init__(self, get_division_list):
        self.chapter_list = []
        self.download_chapter_id_list = []
        self.map = {}
        self.get_division_list: list = get_division_list

    def get_division_information(self):  # get division information and show it
        # clear chapter_list and download_chapter_id_list before get_division_information
        self.chapter_list.clear(), self.download_chapter_id_list.clear()
        for division in self.get_division_list:  # show division information
            print('第{}卷:'.format(division['division_index']), division['division_name'])

    def show_chapter_latest(self):
        shield_chapter_length = len([i for i in self.chapter_list if i['chapter_title'] == '该章节未审核通过'])
        if shield_chapter_length != 0:  # if chapter is not downloaded and not shield chapter
            print("\n[提示]本书一共有", shield_chapter_length, "章被屏蔽")  # show shield chapter
        print('\n[提示]最新章节:', self.chapter_list[-1]['chapter_title'], "\t更新时间:",
              self.chapter_list[-1]['mtime'])

    # def threading_chapter_catalog(self, division):  # get chapter_list and add to self.chapter_list
    #     response = HbookerAPI.Book.get_chapter_update(division['division_id'])
    #     if response.get('code') == '100000':  # if response is ok and data is not empty
    #         self.chapter_list.extend(response['data']['chapter_list'])  # add chapter_list to self.chapter_list
    #         self.map[division['division_id']] = response['data']['chapter_list']
    #     else:
    #         print("threading_chapter_catalog error:", response.get("tip"))  # show error message if response is not ok

    def threading_get_chapter_list(self):
        for division in self.get_division_list:
            chapter_list = division["chapter_list"]
            self.chapter_list.extend(chapter_list)  # add chapter_list to self.chapter_list
            self.map[division['division_id']] = chapter_list

        # with ThreadPoolExecutor(max_workers=len(self.get_division_list)) as executor:
        #     for division in self.get_division_list:
        #         executor.submit(self.threading_chapter_catalog, division)
        # self.chapter_list.sort(key=lambda x: int(x['chapter_index']))  # sort chapter_list by chapter_index

    def threading_add_key_and_id(self, data) -> None:  # add chapter_id and command_key to threading_chapter_id_list
        if data['chapter_id'] + '.txt' in os.listdir(Vars.config_text) or data['auth_access'] == '0':
            return None  # if chapter is exist or auth_access is 0 then skip it and continue
        response = HbookerAPI.Chapter.get_chapter_command(data['chapter_id'])  # get chapter command
        if response.get('code') == '100000':  # if response is ok and data is not empty
            self.download_chapter_id_list.append([data['chapter_id'], response['data']['command']])
        else:
            print("Msg:", response.get('tip'))  # show error message if response is not ok

    def return_chapter_list(self) -> [None, list]:  # add chapter_id and command_key to self.threading_chapter_id_list
        if not self.chapter_list:  # if chapter_list is empty return False
            return print("the chapter_list is empty")  # if chapter_list is empty return
        division_list_length, track_index = len(self.get_division_list), 1  # track_index is used to show progress

        with ThreadPoolExecutor(max_workers=Vars.cfg.data['max_thread']) as executor:
            for result in track(
                    [executor.submit(self.threading_add_key_and_id, data) for data in self.chapter_list],
                    description=f"length: {division_list_length} Loading..."
            ):  # show progress bar and add chapter_id and command_key to self.threading_chapter_id_list
                result.result()  # if result is not None then add to self.threading_chapter_id_list
            track_index += 1  # add 1 to track_index for next loop
        # print("\n[info]this book download chapter length:",
        #       len(self.download_chapter_id_list))  # show need to download chapter length
        return self.download_chapter_id_list, len(self.download_chapter_id_list)  # return id_list and download length
