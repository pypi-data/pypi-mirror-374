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


@pytest.mark.parametrize("option", ["-p", "--purge"])
def test_debug_log(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(txt, "-d", option)
    assert "purge=True" in output.stdout


def test_purge_output_folder_if_exists(cli_runner, infile, tmpdir):
    csv = infile("sample.txt")
    opf = f"{tmpdir}/output"
    _ = cli_runner(csv, "-d", "-of", opf)
    output = cli_runner(csv, "-d", "-of", opf, "-p", "-y")
    assert f"Purge output folder: {opf}" in output.stdout


def test_prompt_when_purging_output_folder(cli_runner, infile, tmpdir):
    csv = infile("sample.txt")
    opf = f"{tmpdir}/output"
    _ = cli_runner(csv, "-d", "-of", opf)

    output = cli_runner(csv, "-d", "-of", opf, "-p", stdin=b"y")
    assert (
        f"Are you sure to purge output folder: {opf}? [y/N] " in output.stdout
    )


def test_no_purge_output_folder_if_not_exists(cli_runner, infile):
    csv = infile("sample.txt")
    output_folder = csv.resolve().parent.joinpath("output")
    output = cli_runner(csv, "-d", "-p")
    assert f"Purge output folder: {output_folder}" not in output.stdout
