#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Routine for creating data mappings."""

import numpy as np
from matplotlib.cbook import flatten
from numpy import array, clip, mgrid


def get_xss_yss_zss(x, y, runs, usemask=True, log=False):
    if usemask:
        xss = array(list(flatten(run['col_'+x][run.mask] for run in runs)))
        yss = array(list(flatten(run['col_'+y][run.mask] for run in runs)))
        if log:
            zss = list(flatten(np.log10(run.y)[run.mask] for run in runs))
        else:
            zss = list(flatten(run.y[run.mask] for run in runs))
    else:
        # XXX duplication
        xss = array(list(flatten(run['col_'+x] for run in runs)))
        yss = array(list(flatten(run['col_'+y] for run in runs)))
        if log:
            zss = list(flatten(np.log10(run.y) for run in runs))
        else:
            zss = list(flatten(run.y for run in runs))
    return xss, yss, zss


def bin_mapping(x, y, runs, usemask=True, log=False, xscale=1, yscale=1,
                interpolate=100, minmax=None):
    from scipy.interpolate import griddata

    xss, yss, zss = get_xss_yss_zss(x, y, runs, usemask, log)
    xss *= xscale
    yss *= yscale
    if minmax is not None:
        if log:
            minmax = list(map(np.log10, minmax))
        zss = clip(zss, minmax[0], minmax[1])
    interpolate = interpolate * 1j
    xi, yi = mgrid[min(xss):max(xss):interpolate,
                   min(yss):max(yss):interpolate]
    zi = griddata(array((xss, yss)).T, zss, (xi, yi))
    return xss/xscale, yss/yscale, xi/xscale, yi/yscale, zi
