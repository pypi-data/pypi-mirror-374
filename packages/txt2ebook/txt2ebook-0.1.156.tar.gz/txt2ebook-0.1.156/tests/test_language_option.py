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

import pytest


def test_auto_detect_language(cli_runner, infile):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile)
    assert "Detect language: zh-cn" in output.stdout


@pytest.mark.parametrize("option", ["-l", "--language"])
def test_warning_log_for_mismatch_configured_and_detect_language(
    cli_runner, infile, option
):
    txtfile = infile("missing_chapters.txt")
    output = cli_runner(txtfile, option, "en")
    assert "Config language: en" in output.stdout
    assert "Detect language: ko" in output.stdout
    assert "Config (en) and detect (ko) language mismatch" in output.stdout
