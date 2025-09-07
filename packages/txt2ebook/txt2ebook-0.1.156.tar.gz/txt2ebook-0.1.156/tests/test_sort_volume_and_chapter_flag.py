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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from textwrap import dedent

import pytest


@pytest.mark.parametrize("option", ["-ss", "--sort-volume-and-chapter"])
def test_sort_logs(cli_runner, infile, option):
    txtfile = infile("sample_unsorted_headers.txt")

    output = cli_runner("-d", "-l", "zh-cn", "-vv", option, txtfile)
    assert (
        """
"""
        in output.stdout
    )

    assert (
        dedent(
            """\
    DEBUG: Chapter(title='序章', paragraphs='1')
    DEBUG: Volume(title='第一卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='1')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='2')
    """
        )
        in output.stdout
    )
