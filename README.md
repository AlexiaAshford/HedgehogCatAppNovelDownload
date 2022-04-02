# _HedgehogCatAppNovel_
- 本项目由 HbookerAppNovelDownloader 老版本改写的， 原作者: [hang333](https://github.com/hang333)
- 刺猬猫【原名欢乐书客】 小说下载器，基于刺猬猫API实现
- 支持`账号登入`
- 支持`付费章节下载`
- 支持`命令行操作`
- 支持`书籍的章节更新`/`更新检查`
- 支持`多线程下载`，默认线程为**32**，可在 *config.json* 文件里修改 **max_thread** 参数更改线程数
- 支持`自定义存储目录`，你可以在 *config.json* 文件里修改**save_path**和**out_path**的文件名
- 文件存储位置 `./Hbooker` 以及 `./downloads` 目录下

##  类似控制台的操作
```bash
输入首字母
h  | help                       --- 显示说明
q  | quit                       --- 退出正在运作的程序
l  | account/password           --- 登入刺猬猫账号
d  | bookid                     --- 输入book id下载小说
u  | updata                     --- 更新下载过的小说
bs | bookshelfid                --- 显示书架信息, 可选书架
```
- **登入账号** ```python run.py l account password```
- **下载书籍** ```python run.py d bookid```
## 需求环境
 * Python3.6以上
 * requests
 * pycrypto或pycryptodome