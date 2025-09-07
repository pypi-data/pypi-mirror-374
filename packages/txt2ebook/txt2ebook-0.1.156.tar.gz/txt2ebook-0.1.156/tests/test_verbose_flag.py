# # Copyright (c) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.,line-too-long

from textwrap import dedent


def test_default_verbosity(cli_runner, infile):
    txtfile = infile("sample_all_headers.txt")

    output = cli_runner("-d", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Volume(title='第一卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='2')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    """
        )
        not in output.stdout
    )

    output = cli_runner("-d", "-v", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Volume(title='第一卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='2')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    """
        )
        not in output.stdout
    )


def test_second_level_verbosity(cli_runner, infile):
    txtfile = infile("sample_all_headers.txt")

    output = cli_runner("-d", "-vv", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Volume(title='第一卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='2')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    """
        )
        in output.stdout
    )


def test_third_level_verbosity(cli_runner, infile):
    txtfile = infile("sample_all_headers.txt")

    output = cli_runner("-d", "-vvv", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Token stats: Counter({'PARAGRAPH': 5, 'CHAPTER': 3, 'VOLUME': 2, 'TITLE': 1, 'AUTHOR': 1})
    DEBUG: Token(type='TITLE', line_no='0', value='月下独酌·其一')
    DEBUG: Token(type='AUTHOR', line_no='6', value='李白')
    DEBUG: Token(type='PARAGRAPH', line_no='6', value='李白')
    DEBUG: Token(type='VOLUME', line_no='8', value='第一卷')
    DEBUG: Token(type='CHAPTER', line_no='10', value='第1章 月既不解饮')
    DEBUG: Token(type='PARAGRAPH', line_no='12', value='花间一壶酒，独酌无相')
    DEBUG: Token(type='PARAGRAPH', line_no='29', value='我歌月徘徊，我舞影零')
    DEBUG: Token(type='CHAPTER', line_no='19', value='第2章 影徒随我身')
    DEBUG: Token(type='PARAGRAPH', line_no='29', value='我歌月徘徊，我舞影零')
    DEBUG: Token(type='VOLUME', line_no='25', value='第二卷')
    DEBUG: Token(type='CHAPTER', line_no='27', value='第3章 暂伴月将影')
    DEBUG: Token(type='PARAGRAPH', line_no='29', value='我歌月徘徊，我舞影零')
    """
        )
        in output.stdout
    )
