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


def test_debug_logs(cli_runner):
    ret = cli_runner("-d", "--demo", 1)
    assert "demo=1" in ret.stderr
    assert "input_filename='output/sample.csv'" in ret.stderr


def test_total_default_heatmap_count(cli_runner):
    ret = cli_runner("-h")

    assert (
        "generate number of heatmaps by colormaps (default: '182')"
    ) in ret.stdout
