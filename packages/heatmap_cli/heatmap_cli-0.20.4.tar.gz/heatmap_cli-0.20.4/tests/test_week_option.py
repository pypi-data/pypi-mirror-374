# Copyright (C) 2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
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


@pytest.mark.parametrize("option", ["-w", "--week"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d", option, "42")

    assert "2024_week_42_RdYlGn_r_heatmap_" in ret.stderr
    assert "week=42" in ret.stderr


def test_last_week_of_the_year(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d", "-w", "52")

    assert "2024_RdYlGn_r_heatmap_" in ret.stderr
    assert "week=52" in ret.stderr
