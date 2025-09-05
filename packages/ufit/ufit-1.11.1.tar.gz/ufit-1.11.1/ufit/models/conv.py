#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Convolution models."""

import re

from numpy import log, sqrt
from scipy.ndimage import gaussian_filter

from ufit.models.base import Model
from ufit.param import Param

__all__ = ['GaussianConvolution']


id_re = re.compile('[a-zA-Z][a-zA-Z0-9_]*$')


class GaussianConvolution(Model):
    """Models a 1-D convolution with a Gaussian kernel.  Points at the edge are
    repeated to mitigate edge effects.

    Parameters:

    * `width` - FWHM of Gaussian kernel
    """

    def __init__(self, model, width=1, name=None):
        self._model = model
        if name is not None:
            self.name = name
        elif model.name and id_re.match(model.name):
            self.name = '%s_conv' % model.name
        else:
            self.name = 'conv'
        self.params = model.params[:]
        pname = self.name + '_width'
        self.params.append(Param.from_init(pname, width))

        def convfcn(p, x):
            data = model.fcn(p, x)
            binwidth = (x.max() - x.min()) / (len(x) - 1)
            return gaussian_filter(data, p[pname] / binwidth / sqrt(8*log(2)),
                                   mode='nearest')
        self.fcn = convfcn
