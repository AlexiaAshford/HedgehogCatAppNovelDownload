from instance import *
import book


def save_cache(file_name: str, response: dict) -> None:
    if not os.path.exists(Vars.cfg.data['local_cache_dir']):
        os.mkdir(Vars.cfg.data['local_cache_dir'])
    if Vars.cfg.data.get('backups_local_cache'):
        with open(f"{Vars.cfg.data['local_cache_dir']}/{file_name}", 'w', encoding='utf-8') as book_info_file:
            json.dump(response, book_info_file, ensure_ascii=False, indent=4)
    else:
        print("backups local cache is not open, if you need it, please open it in the configuration file.")


def load_cache(file_name: str) -> dict:
    local_cache_dir = f"{Vars.cfg.data['local_cache_dir']}/{file_name}"
    if os.path.exists(local_cache_dir) and \
            os.path.getsize(local_cache_dir) > 0:
        with open(local_cache_dir, 'r', encoding='utf-8') as book_info_file:
            return json.load(book_info_file)
    else:
        print(f'\n{file_name} not found.')


def test_division_list(book_id: str):
    division_list = load_cache(f"{book_id}_chapter_list.json")
    if isinstance(division_list, dict):
        print("server can't get division list, get division list from local cache success.")
        return division_list
    print("server can't get division list, get division list from local cache failed.")


def test_cache_and_init_object(book_id: str):
    current_book = load_cache(f"{book_id}.json")
    if isinstance(current_book, dict):
        print("[info] server can't get book info, get book info from local cache success.")
        Vars.current_book = book.Book(book_info=current_book)
    else:
        print("[info] server can't get book info, try to get book info from local cache, but not found.")
        Vars.current_book = None
