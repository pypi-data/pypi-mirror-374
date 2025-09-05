#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Load routine for simple whitespace-separated column data files."""

import io
from os import path

from numpy import insert, loadtxt


def guess_cols(colnames, coldata, meta):
    if len(colnames) > 2 and not any(c < 0 for c in coldata[2]):
        dycol = colnames[2]
    else:
        dycol = None
    return colnames[0], colnames[1], dycol, None


def check_data_simple(fp, sep=None):
    line = fp.readline()
    # find the first non-comment line
    while line.startswith((b'#', b'%')):
        line = fp.readline()
    line2 = fp.readline()
    fp.seek(0, 0)
    # special case FRM2 irradiation
    if sep == b',' and line2.startswith(b'Wavelength (nm),Abs,'):
        return True
    # must be values in non-comment line, or the line after
    try:
        [float(x) for x in line.split(sep)]
    except ValueError:
        try:
            [float(x) for x in line2.split(sep)]
        except ValueError:
            return False
    return True


def check_data(fp):
    return check_data_simple(fp, None)


def read_data_simple(filename, fp, sep=None):
    fp = io.TextIOWrapper(fp, 'ascii', 'ignore')
    line1 = ''
    line2 = fp.readline()
    skiprows = 0
    # find the first non-comment line
    while line2.startswith(('#', '%')):
        line1 = line2
        line2 = fp.readline()
        skiprows += 1
    # now line2 is the first non-comment line (but may be column names)

    # check for special case
    line3 = fp.readline()
    if sep == ',' and line3.startswith('Wavelength (nm),Abs,'):
        return read_data_frm2_irradiation(filename, line2, fp)

    # if there are comments, line1 will have the comment char
    comments = '#'
    if line1.startswith(('#', '%')):
        comments = line1[0]
        line1 = line1[1:]
    try:
        [float(x) for x in line2.split(sep)]
    except ValueError:
        # must be column names
        colnames = line2.rstrip().split(sep)
        skiprows += 1
    else:
        # line1 might have column names
        if line1:
            colnames = line1.rstrip().split(sep)
        else:
            colnames = []
    fp.seek(0, 0)
    arr = loadtxt(fp, ndmin=2, skiprows=skiprows, comments=comments,
                  delimiter=sep)
    # if number of colnames is not correct, discard them
    if len(colnames) != arr.shape[1]:
        colnames = ['Column %d' % i for i in range(1, arr.shape[1]+1)]
    meta = {}
    meta['filedesc'] = path.basename(filename)
    return colnames, arr, meta


def read_data(filename, fp):
    return read_data_simple(filename, fp, None)


def read_data_frm2_irradiation(filename, samplenames, fp):
    fp.seek(0, 0)
    cols = samplenames.rstrip().split(',')[:-1]
    colnames = sum((
        [f'{sample} wavelength', f'{sample} abs', f'{sample} abs err']
        for sample in cols[::2]), [])
    usecols = list(range(len(cols)))
    arr = loadtxt(fp, ndmin=2, skiprows=2, delimiter=',', usecols=usecols)
    for i in range(len(cols) // 2):
        arr = insert(arr, 3*i + 2, 0.01, axis=1)
    meta = {'filedesc': path.basename(filename)}
    return colnames, arr, meta
