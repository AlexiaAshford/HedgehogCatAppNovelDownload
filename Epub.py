from ebooklib import epub
from instance import *


class EpubFile:
    def __init__(self):
        self.epub = epub.EpubBook()
        self.EpubList = list()
        self.path = os.path.join
        self.epub.set_language('zh-CN')
        self.epub.set_identifier(Vars.current_book.book_id)
        self.epub.set_title(Vars.current_book.book_name)
        self.epub.add_author(Vars.current_book.author_name)

    def add_intro(self):
        intro_ = epub.EpubHtml(title='简介信息', file_name='0000-000000-intro.xhtml', lang='zh-CN')
        intro_.content = '<html><head></head><body><h1>简介</h1>'
        intro_.content += '<p>书籍书名:{} 书籍序号:{}</p>'.format(Vars.current_book.book_name, Vars.current_book.book_id)
        # intro_.content += '<p>书籍作者:{} 更新时间:{}</p>'.format(Vars.current_book.author_name, up_time)
        # intro_.content += '<p>最新章节:{}</p><p>系统标签:{}</p>'.format(up_chapter, novel_tag)
        # intro_.content += '<p>简介信息:</p>{}</body></html>'.format(intro)
        self.epub.add_item(intro_)
        self.EpubList.append(intro_)

    def cover(self):
        print("")
        # self.epub.set_cover(self.book_name + '.png', API.Cover.download_cover())

    def add_chapter(self, chapter_title: str, content: str, serial_number: str):
        chapter_serial = epub.EpubHtml(
            title=chapter_title, file_name=str(serial_number).rjust(4, "0") + '-' + chapter_title + '.xhtml',
            lang='zh-CN', uid='chapter_{}'.format(serial_number)
        )
        chapter_serial.content = content.replace('\n', '</p>\r\n<p>')
        self.epub.add_item(chapter_serial)
        self.EpubList.append(chapter_serial)

    def save(self):
        self.cover()
        self.epub.toc = tuple(self.EpubList)
        self.epub.spine = ['nav']
        self.epub.spine.extend(self.EpubList)
        self.epub.add_item(epub.EpubNcx())
        self.epub.add_item(epub.EpubNav())
        epub.write_epub(self.path(
            Vars.cfg.data['out_path'] + Vars.current_book.book_name + '.txt',
            Vars.cfg.data['out_path'] + Vars.current_book.book_name + '.epub'), self.epub, {}
        )
