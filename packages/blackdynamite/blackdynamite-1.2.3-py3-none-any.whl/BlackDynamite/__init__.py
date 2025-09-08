#!/usr/bin/env python3
# flake8: noqa
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import lazy_loader as lazy
import warnings

warnings.filterwarnings(
    "ignore", message=".*subpackages can technically be lazily loaded.*"
)

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    [
        "base",
        "base_zeo",
        "bdparser",
        "jobselector",
        "run_zeo",
        "runselector",
        "run_zeo",
        # "BDstat",
        # "coating",
        # "conffile_zeo",
        # "job",
        # "loader",
        # "lowercase_btree",
    ],
    submod_attrs={
        "bdparser": ["BDParser", "RunParser"],
        "base": ["Base"],
        "base_zeo": ["BaseZEO"],
        "runselector": ["RunSelector"],
        "jobselector": ["JobSelector"],
        "run_zeo": ["RunZEO", "getRunFromScript"],
    },
)

################################################################

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("blackdynamite")
except PackageNotFoundError:
    pass
