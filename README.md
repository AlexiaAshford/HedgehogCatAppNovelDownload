# _HedgehogCatAppNovel_

- project is open source
- HbookerAppNovelDownloader project old version refactoring，project author name: [SeaLoong](https://github.com/SeaLoong)
- ciweimao【happy booker】 Novel Downloader，Android API implementation
- login your account to get your `token` to use this script
- download the book as `epub` and `txt` files (if you have the permission)
- support download `vip chapters`  the chapters save as epub files and txt files
- you can use the `epub` and `txt` files to read the books
- check for update books and chapters automatically
- download chapters `multi threads` support default thread is `32`，you can change the `max_thread` to set the number of
  threads
- cache image in EPUB files `image is not saved in localstorage`
- the path to save `epub` and txt `file` to local `./Hbooker` and `./downloads`
- This customization adds a file path in the *config.json* that lets you change the location you want to save it to.


## imitate the Microsoft Windows control panel
```bash
book text file and config file in ./Hbooker/
q  | quit                                  --- exit program
l  | account login_token/account           --- login hbooker with account
d  | book-id                               --- download book
u  | updata                                --- update config.json downloaded_book_id_list
bs | bookshelf                             --- read bookshelf


```

## command line

- **download book** ``` --download bookid```
- **update booklist** ``` --update ```
- **show bookshelf** ``` --bookshelf ```
- **bookinfo** ``` --bookinfo bookid```
- **clear cache** ``` --clear_cache```
-

## 此程序仅供个人备份文本，请勿用于任何盗版和传播

* 防止/章节/小说 哪天遭屏蔽或下架，让读者有預先下载小说到本地保存的选择。
* 请尊重作者的成果，勿用于盗版小说制作和传播
