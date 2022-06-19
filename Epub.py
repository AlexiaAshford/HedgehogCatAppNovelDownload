from ebooklib import epub
from html.parser import HTMLParser
from instance import *
import os
from posixpath import basename
try:
    import magic
    have_magic = True
except ImportError:
    have_magic = False
    print('Warning: python-magic not found. The mimetype in EPUB file may wrong.')
    import platform
    if platform.system() == "Windows":
        print('python-magic-bin is also needed on Windows.')
from urllib.parse import urlparse
import requests
from typing import List
import xml.etree.ElementTree as ET


def get_cover_image(cover_url: str):
    retry = 0
    while True:
        response = requests.get(cover_url)
        if response.status_code == 200:
            return response.content
        retry += 1
        if retry > 5:
            return None


class HTMLImage:
    def __init__(self, attrs):
        self.src = None
        self.alt = None
        self.path = None
        self.epub_path = None
        for key, value in attrs:
            if key == 'src':
                self.src = value
            elif key == 'alt':
                self.alt = value

    def download_image(self):
        if not self.is_valid():
            return False
        if self.path is None:
            file_name = basename(urlparse(self.src).path)
            if file_name == "" and self.alt is not None:
                file_name = f"{self.alt}.jpg"
            if file_name == "":
                return False
            self.path = os.path.join(Vars.config_text, file_name)
        if os.path.exists(self.path):
            return True
        retry = 0
        while True:
            response = requests.get(self.src)
            if response.status_code == 200:
                break
            retry += 1
            if retry > 5:
                return False
        with open(self.path, 'wb') as f:
            f.write(response.content)
        return True

    def is_valid(self):
        return self.src is not None

    def to_local(self):
        if not self.is_valid():
            return ""
        if not self.download_image():
            raise ValueError("Failed to download image.")
        self.epub_path = os.path.basename(self.path)
        if have_magic:
            with open(self.path, 'rb') as f:
                mime = magic.from_buffer(f.read(4096), True)
            self.epub_path = os.path.splitext(self.epub_path)[0] + get_extension(mime)
        d = { 'src': self.epub_path }
        if self.alt:
            d['alt'] = self.alt
        return ET.tostring(ET.Element('img', d), 'unicode')


# Used to parse content
class ContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_paragraph = False
        self.data = []
        # Local image file lists
        self.images = []
        self._paragraph_data = ''

    def handle_data(self, data: str):
        if self._in_paragraph:
            if isinstance(self._paragraph_data, str):
                self._paragraph_data += data
            elif isinstance(self._paragraph_data, list):
                self._paragraph_data.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            if self._in_paragraph:
                if self._paragraph_data:
                    self._paragraph_data = [self._paragraph_data]
                else:
                    self._paragraph_data = []
                self._paragraph_data.append(HTMLImage(attrs))
            else:
                self.data.append(HTMLImage(attrs))
        elif tag == 'p':
            self._in_paragraph = True
        else:
            raise NotImplementedError()

    def handle_endtag(self, tag: str):
        if tag == 'img':
            pass
        elif tag == 'p':
            self._in_paragraph = False
            if self._paragraph_data:
                self.data.append(self._paragraph_data)
                self._paragraph_data = ''
        else:
            raise NotImplementedError()

    def have_image(self, data_list=None) -> bool:
        if data_list is None:
            data_list = self.data
        for i in data_list:
            if isinstance(i, HTMLImage):
                if i.is_valid():
                    return True
            elif isinstance(i, list):
                if self.have_image(i):
                    return True
        return False

    def to_local(self, data_list=None) -> str:
        default_data_list = False
        if data_list is None:
            data_list = self.data
            default_data_list = True
        data = ''
        for i in data_list:
            if isinstance(i, str):
                if default_data_list:
                    data += f'<p>{i}</p>\n'
                else:
                    data += i
            elif isinstance(i, HTMLImage):
                if i.is_valid():
                    data += i.to_local()
                    self.images.append(i)
            elif isinstance(i, list):
                data += f'<p>{self.to_local(i)}</p>\n'
            else:
                raise NotImplementedError()
        if self._paragraph_data:
            data += f'<p>{self._paragraph_data}</p>\n'
        return data


def get_extension(mime: str) -> str:
    if mime == 'image/gif':
        return '.gif'
    elif mime == 'image/jpeg':
        return '.jpeg'
    elif mime == 'image/png':
        return '.png'
    elif mime == 'image/svg+xml':
        return '.svg'
    elif mime == 'image/webp':  # EPUB 3.3 Draft
        return '.webp'
    else:
        print(mime)
        raise NotImplementedError()


class EpubFile:
    def __init__(self):
        self.epub = epub.EpubBook()
        self.EpubList = list()
        self.epub.set_language('zh-CN')
        self.epub.set_identifier(Vars.current_book.book_id)
        self.epub.set_title(Vars.current_book.book_name)
        self.epub.add_author(Vars.current_book.author_name)
        self.last_division_name = ''

    def add_intro(self):
        intro_ = epub.EpubHtml(title='简介信息', file_name='0000-000000-intro.xhtml', lang='zh-CN')
        intro_.content = '<html><head></head><body><h1>简介</h1>'
        intro_.content += '<p>书籍书名:{} 书籍序号:{}</p>'.format(Vars.current_book.book_name, Vars.current_book.book_id)
        # intro_.content += '<p>书籍作者:{} 更新时间:{}</p>'.format(Vars.current_book.author_name, up_time)
        # intro_.content += '<p>最新章节:{}</p><p>系统标签:{}</p>'.format(up_chapter, novel_tag)
        # intro_.content += '<p>简介信息:</p>{}</body></html>'.format(intro)
        self.epub.add_item(intro_)
        self.EpubList.append(intro_)
        self.epub.spine.append(intro_)

    def download_cover_and_add_epub(self):  # download cover image and add to epub file as cover
        png_file = get_cover_image(Vars.current_book.cover)  # get cover image from url
        if png_file is not None:  # if cover image is not None ,then add to epub file
            if have_magic:
                mime_type = magic.from_buffer(png_file, mime=True)
                file_name = Vars.current_book.book_name + get_extension(mime_type)
            else:
                file_name = Vars.current_book.book_name + '.png'
            self.epub.set_cover(file_name, png_file)  # add cover image to epub file

    def add_chapter_in_epub_file(self, chapter_title: str, content_lines_list: List[str], serial_number: str, division_name: str):
        import uuid
        chapter_serial = epub.EpubHtml(
            title=chapter_title,
            file_name=str(serial_number).rjust(4, "0") + '.xhtml',
            lang='zh-CN',
            uid='u' + uuid.uuid4().hex,  # XML name can not start with diget
        )
        # Set the content as auxiliary content
        # See https://www.w3.org/publishing/epub3/epub-packages.html#attrdef-itemref-linear
        if division_name == '作品相关':
            chapter_serial.is_linear = False
        parser = ContentParser()
        parser.feed('<p>' + '</p>\n<p>'.join(content_lines_list) + '</p>')
        parser.close()
        chapter_serial.content = '<h1 style="text-align: center;">{}</h1>\n'.format(chapter_title) + parser.to_local()
        self.epub.add_item(chapter_serial)  # add chapter to epub file as item
        for oimg in parser.images:
            with open(oimg.path, 'rb') as f:
                img_content = f.read()
            img = epub.EpubImage()
            img.file_name = oimg.epub_path
            img.content = img_content
            img.id = 'i' + uuid.uuid4().hex
            if oimg.epub_path.endswith('.webp'):
                img.media_type = 'image/webp'
            self.epub.add_item(img)
        if self.last_division_name != division_name:
            self.EpubList.append([epub.Link(chapter_serial.file_name, division_name), []])
            self.last_division_name = division_name
        self.EpubList[-1][-1].append(chapter_serial)  # add chapter to epub list
        self.epub.spine.append(chapter_serial)

    def save_epub_file(self):  # save epub file to local
        # the path to save epub file to local
        self.epub.toc = self.EpubList
        self.epub.add_item(epub.EpubNcx()), self.epub.add_item(epub.EpubNav())
        epub.write_epub(
            os.path.join(os.getcwd(), Vars.cfg.data['out_path'], Vars.current_book.book_name + '.epub'), self.epub, {}
        )  # save epub file to out_path directory with book_name.epub
