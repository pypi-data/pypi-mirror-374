#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Qt compatibility layer."""

# pylint: disable=wildcard-import, unused-import, unused-wildcard-import

import sys

try:
    import PyQt5

except ImportError:
    from PyQt6 import uic
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtPrintSupport import *
    from PyQt6.QtSvg import *
    from PyQt6.QtWidgets import *

    import ufit.guires_qt6

else:
    from PyQt5 import uic
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtPrintSupport import *
    from PyQt5.QtSvg import *
    from PyQt5.QtWidgets import *

    import ufit.guires_qt5

# Do not abort on exceptions in signal handlers.
# pylint: disable=unnecessary-lambda
sys.excepthook = lambda *args: sys.__excepthook__(*args)
