#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

# pylint: disable=wrong-import-position, wrong-import-order

from ufit.version import get_version

__version__ = get_version()


class UFitError(Exception):
    pass

import matplotlib

try:
    import ufit.qt
    matplotlib.use('qtagg')
except Exception:
    pass

from ufit.backends import *
from ufit.data import *
from ufit.param import *
from ufit.result import *

from ufit.models import *  # isort: skip
