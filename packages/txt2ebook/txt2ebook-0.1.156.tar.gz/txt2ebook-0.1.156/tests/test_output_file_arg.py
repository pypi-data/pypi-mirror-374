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


def test_output_basename_default_to_input_basename(
    tte, infile, outfile
):
    txt = infile("sample.txt")
    epub = outfile("output/sample.epub")
    output = tte("epub", str(txt))

    assert epub.exists()
    assert f"Generate EPUB file: {str(epub)}" in output.stdout


def test_set_output_filename(tte, infile, outfile):
    txt = infile("sample.txt")
    epub = outfile("foobar.epub")
    output = tte("epub", str(txt), str(epub))

    assert epub.exists()
    assert f"Generate EPUB file: {str(epub)}" in output.stdout
