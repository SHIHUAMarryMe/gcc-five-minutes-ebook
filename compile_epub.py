# -*- coding: utf-8 -*-
import os
import sys
import io
import datetime
import subprocess

from ebooklib import epub
import markdown


ENCODING = 'utf-8'
LANG = 'zh-cn'
DATETIME_FORMAT_STR = "%Y-%m-%d %H:%M:%S"
FILENAME_DATETIME_FORMAT_STR = "%Y%m%d_%H%M%S"
ABOUT_EPUB = '''
# 关于 epub

本 epub 文件编译自 github 开源项目 _gcc五分钟系列_.

项目地址: https://github.com/lexdene/gcc_five_minute

编译版本: {version}, 编译时间: {time}.
使用 Python 版本: {python_version}.
'''


def compile_markdowns_to_epub(base_path):
    version = get_version(base_path)
    now = datetime.datetime.now()

    book = epub.EpubBook()

    # set metadata
    book.set_identifier('gcc five minutes')
    book.set_title('gcc五分钟系列')
    book.set_language(LANG)
    book.add_author('lexdene')

    for index, file_path in enumerate(search_markdown_files(base_path)):
        add_chapter(
            book,
            chapter_id='chapter_%02d' % index,
            title=get_content_title(file_path),
            content=compile_markdown_file(file_path),
        )

    add_chapter(
        book,
        chapter_id='about_epub',
        title='关于 epub',
        content=compile_markdown(
            ABOUT_EPUB.format(
                version=version,
                time=now.strftime(DATETIME_FORMAT_STR),
                python_version='%d.%d.%d' % (
                    sys.version_info.major,
                    sys.version_info.minor,
                    sys.version_info.micro,
                )
            )
        )
    )

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )

    # add CSS file
    book.add_item(nav_css)

    file_name = 'gcc_five_minutes_%s_%s' % (
        version,
        now.strftime(FILENAME_DATETIME_FORMAT_STR),
    )

    # write to the file
    epub.write_epub(
        '%s.epub' % file_name,
        book,
        {}
    )


def get_version(base_path):
    version = subprocess.check_output([
        'git', 'rev-parse', '--short', 'HEAD'
    ])
    version = version.decode(ENCODING)
    version = version[:-1]  # remove suffix '\n'
    return version


def search_markdown_files(base_path):
    for dirpath, dirnames, filenames in os.walk(base_path):
        for file_name in filenames:
            if file_name.endswith('.md'):
                file_path = os.path.join(
                    dirpath, file_name
                )
                print('file name: %s' % file_path)
                yield file_path


def add_chapter(book, chapter_id, title, content):
    chapter_file_name = chapter_id + '.xhtml'

    print('title: %s' % title)

    chapter = epub.EpubHtml(
        title=title,
        file_name=chapter_file_name,
        lang=LANG,
        content=content,
    )

    book.add_item(chapter)
    book.toc.append(
        epub.Link(chapter_file_name, title, chapter_id)
    )
    book.spine.append(chapter)


def get_content_title(file_path):
    with open(file_path, 'r', encoding=ENCODING) as f:
        # remove the prefix '# ' and suffix '\n'
        return f.readline()[2:-1]


def compile_markdown_file(file_path):
    with open(file_path, 'r', encoding=ENCODING) as f:
        return compile_markdown(f.read())


def compile_markdown(source):
    return markdown.markdown(source)


if __name__ == '__main__':
    compile_markdowns_to_epub('.')
