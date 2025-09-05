#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Load routine for TAIPAN (ANSTO) and PTAX/HB-1 (HFIR) data files."""

import io
import time

from numpy import array, loadtxt


def guess_cols(colnames, coldata, meta):
    return meta['def_x'], meta['def_y'], None, meta.get('preset_channel')


def check_data(fp):
    line = fp.readline()
    fp.seek(0, 0)
    # on the first line is always name of the raw file (TAIPAN) or scan number
    # (PTAX)
    return line.startswith((b'# raw_file =', b'# scan ='))


def read_data(filename, fp):
    fp = io.TextIOWrapper(fp, 'ascii', 'ignore')
    line1 = ''
    line2 = fp.readline()
    skiprows = 0
    date = ''
    meta = {}
    # find the first non-comment line
    while line2.startswith('#'):
        # parse meta:
        line1 = line2
        line2 = fp.readline()
        skiprows += 1
        # do not parse headers
        if not line2.startswith('#'):
            continue
        key, oval = [x.strip() for x in line1[1:].strip().split('=', 1)]
        # name cannot start with col_ - this is reserved for columns values
        if key.startswith('col_'):
            key = key[4:]
        if key == 'experiment':
            title = oval
        elif key == 'experiment_number':
            meta['experiment'] = oval
        elif key == 'samplename':
            remark = oval
        if key == 'scan':
            meta['filenumber'] = int(oval)
        elif key == 'scan_title':
            meta['subtitle'] = oval
        elif key == 'date':
            date = oval
        elif key == 'time':
            if date:
                oval = f'{date} {oval}'
            meta['date'] = oval
        else:
            meta[key] = oval
    meta['instrument'] = 'TAIPAN' if 'raw_file' in meta else 'PTAX'
    if remark and title:
        meta['title'] = title + ', ' + remark
    # print(meta)
    # now line2 is the first data line
    # line1 is header line
    line1 = line1[1:]
    # if there are comments, line1 will have the comment char
    colnames = line1.split()

    fp.seek(0, 0)
    arr = loadtxt(fp, ndmin=2, skiprows=skiprows, comments="#")
    # if number of colnames is not correct, discard them
    if len(colnames) != arr.shape[1]:
        colnames = ['Column %d' % i for i in range(1, arr.shape[1]+1)]

    cols = dict((name, arr[:, i]) for (i, name) in enumerate(colnames))
    meta['environment'] = []
    if 'en' in colnames:
        meta['hkle'] = arr[:, (3, 4, 5, 1)]
        deviations = array([(cs.max()-cs.min()) for cs in meta['hkle'].T])
        meta['hkle_vary'] = ['h', 'k', 'l', 'E'][deviations.argmax()]
    for col in cols:
        meta[col] = cols[col].mean()
    for tcol in ['temp', 'TC1_sensorB', 'TC1_sensorA', 'TC1_sensorC', 'TC1_sensorD']:
        if tcol in cols:
            meta['environment'].append('T = %.3f K' % meta[tcol])
            break
    if 'MAG' in cols:
        if meta['MAG'] > 0:
            meta['environment'].append('B = %.3f T' % meta['B'])

    return colnames, arr, meta
