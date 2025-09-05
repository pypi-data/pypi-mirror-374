#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Load routine for simple comma-separated column data files."""

# pylint: disable=unused-import
from ufit.data.simple import check_data_simple, guess_cols, read_data_simple


def read_data(filename, fp):
    return read_data_simple(filename, fp, ',')


def check_data(fp):
    return check_data_simple(fp, b',')
