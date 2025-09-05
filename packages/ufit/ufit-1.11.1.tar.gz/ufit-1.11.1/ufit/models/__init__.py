#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Models package for ufit."""

from ufit.models.base import *
from ufit.models.conv import *
from ufit.models.corr import *
from ufit.models.other import *
from ufit.models.peaks import *
from ufit.models.sqwtas import *

from ufit.models import base, corr, other, peaks, sqwtas  # isort: skip

__all__ = base.__all__ + peaks.__all__ + corr.__all__ + other.__all__ + \
    sqwtas.__all__

# Concrete models that can be used in the simplified GUI interface.

concrete_models = [
    GaussInt,
    Gauss,
    LorentzInt,
    Lorentz,
    Voigt,
    PseudoVoigt,
    DHO,
    Background,
    SlopingBackground,
    CKI_Corr,
    Bose,
    Const,
    StraightLine,
    Parabola,
    Cosine,
    Cosine2,
    Sinc,
    ExpDecay,
    PowerLaw,
    GaussianConvolution,
]
