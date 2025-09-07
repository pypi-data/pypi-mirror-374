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


@pytest.mark.parametrize("option", ["-hn", "--header-number"])
def test_header_to_numbers_conversion(cli_runner, infile, option):
    txtfile = infile("sample_long_headers.txt")

    output = cli_runner("-d", option, txtfile)
    expected_output1 = dedent(
        """\
        DEBUG: Convert header to numbers: 第一卷 -> 第1卷
        DEBUG: Convert header to numbers: 第一章 月既不解饮 -> 第1章 月既不解饮
        DEBUG: Convert header to numbers: 第二章 影徒随我身 -> 第2章 影徒随我身
    """
    )
    assert expected_output1 in output.stdout

    output = cli_runner("-d", "--header-number", txtfile)
    expected_output2 = dedent(
        """\
        DEBUG: Convert header to numbers: 第二卷 -> 第2卷
        DEBUG: Convert header to numbers: 第三章 暂伴月将影 -> 第3章 暂伴月将影
        DEBUG: Convert header to numbers: 第二百章 暂伴月将影 -> 第200章 暂伴月将
        DEBUG: Convert header to numbers: 第九百九十九章 暂伴 -> 第999章 暂伴月将
        DEBUG: Convert header to numbers: 第九千百九十九章 暂 -> 第9919章 暂伴月
    """
    )

    assert expected_output2 in output.stdout
