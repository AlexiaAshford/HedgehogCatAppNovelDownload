# _HedgehogCatAppNovel_

- 本项目由 HbookerAppNovelDownloader 老版本改写的， 原作者: [SeaLoong](https://github.com/SeaLoong)
- 刺猬猫【原名欢乐书客】 小说下载器，基于刺猬猫API实现
- 支持 `账号登入[关于账号登入，刺猬猫在新版本添加了极客校验，无法直接登入，请自行使用login_token/account来绕过验证]`
- 支持 `付费章节下载`
- 支持 `命令行操作`
- 支持 `书籍的章节更新` / `更新检查`
- 支持 `多线程下载`，默认线程为**32**，可在 *config.json* 文件里修改 **max_thread** 参数更改线程数
- 支持 `自定义存储目录`，你可以在 *config.json* 文件里修改**save_path**和**out_path**的文件名
- 文件存储位置 `./Hbooker` 以及 `./downloads` 目录下

        'book text file and config file in ./Hbooker/',
        'quit \t\t\t\t exit program',
        'login \t\t\t\t <login_token> <account> \t login hbooker with account',
        'bookshelf \t\t\t\t read bookshelf',
        'bookshelf \t\t\t\t <bookshelf index> \t switch bookshelf',
        'download \t\t\t\t <bookshelf index/book index> \t Download the last chapter',
        'update \t\t\t\t update config.json downloaded_book_id_list',

## imitate the Microsoft Windows control panel

```bash
book text file and config file in ./Hbooker/
q  | quit                                  --- exit program
l  | account login_token/account           --- login hbooker with account
d  | book-id                               --- download book
u  | updata                                --- update config.json downloaded_book_id_list
bs | bookshelf                             --- read bookshelf


```

## 命令行交互

- **下载书籍** ```python run.py --download bookid```
- **更新书籍** ```python run.py --update ```
- **显示书架** ```python run.py --bookshelf ```
- **显示书籍** ```python run.py --bookinfo bookid```
- **清除缓存** ```python run.py --clear_cache```
-

## 需求环境

* Python3.6以上
* requests
* ebooklib
* pycrypto或pycryptodome

## 此程序仅供个人备份文本，请勿用于任何盗版和传播

* 防止/章节/小说 哪天遭屏蔽或下架，让读者有預先下载小说到本地保存的选择。
* 请尊重作者的成果，勿用于盗版小说制作和传播
