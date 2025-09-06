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

from . import (BDstat, base, base_zeo, bdparser, coating, conffile_zeo, job,
               jobselector, loader, lowercase_btree, run_zeo, runselector)
from .base import *
from .base_zeo import *
from .bdparser import *
from .BDstat import *
from .conffile_zeo import *
from .job import *
from .jobselector import *
from .lowercase_btree import *
from .run_zeo import *
from .runselector import *

__all__ = ["job", "base"]
__all__.extend(bdparser.__all__)
__all__.extend(base.__all__)
__all__.extend(base_zeo.__all__)
__all__.extend(runselector.__all__)
__all__.extend(jobselector.__all__)
__all__.extend(conffile_zeo.__all__)
__all__.extend(BDstat.__all__)


################################################################

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("blackdynamite")
except PackageNotFoundError:
    pass
