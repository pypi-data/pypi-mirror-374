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


def test_nonexistent_filename(cli_runner):
    output = cli_runner("parse", "nonexistent.txt")
    assert (
        "[Errno 2] No such file or directory: 'nonexistent.txt'"
        in output.stderr
    )


def test_empty_file_content(cli_runner, infile):
    txt = infile("empty_file.txt")
    output = cli_runner("parse", str(txt))
    assert f"error: Empty file content in {str(txt)}" in output.stdout
