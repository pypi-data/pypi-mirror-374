#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Load routine for DynaCool PPMS data files."""

import io
from os import path

from numpy import genfromtxt, mean, ptp


def guess_cols(colnames, coldata, meta):
    xcol = 'Time Stamp (sec)'
    for cn in colnames:
        if cn.replace(' ', '').lower().startswith('timestamp'):
            xcol = cn
    ycol = dycol = None
    if 'AC Moment (emu)' in colnames:
        ycol = 'AC Moment (emu)'
        dycol = 'AC Std. Dev. (emu)'
    elif 'Moment (emu)' in colnames:
        ycol = 'Moment (emu)'
        dycol = 'M. Std. Err. (emu)'
    elif 'Samp HC (µJ/K)' in colnames:
        ycol = 'Samp HC (µJ/K)'
        dycol = 'Samp HC Err (µJ/K)'
    elif 'Bridge 1 Resistivity (Ohm-m)' in colnames:
        ycol = 'Bridge 1 Resistivity (Ohm-m)'
        dycol = 'Bridge 1 Std. Dev. (Ohm-m)'
    else:
        # fallback
        ycol = [colnames[i] for i in range(len(colnames))
                if ptp(coldata[:, i]) > 0][-1]
    xcands = ['Magnetic Field (Oe)', 'Temperature (K)', 'Time Stamp (sec)',
              'Time Stamp (Seconds)', 'Sample Temp (Kelvin)']
    spreads = []
    for xcand in xcands:
        if xcand in colnames:
            data = coldata[:, colnames.index(xcand)]
            spreads.append((ptp(data)/mean(data), xcand))
    if spreads:
        xcol = sorted(spreads)[-1][1]
    return xcol, ycol, dycol, None


def check_data(fp):
    fp.readline()
    try:
        line2 = fp.readline()
        line3 = fp.readline()
        line4 = fp.readline()
        fp.seek(0, 0)
        return line2.startswith((b'; VSM Data File',
                                 b'; ACMS II Data File')) or \
               line3.startswith(b'BYAPP,') or \
               line4.startswith(b'BYAPP,')
    except IOError:
        return False


def read_data(filename, fp):
    fp = io.TextIOWrapper(fp, 'latin1', 'ignore')

    meta = {}
    meta['filenumber'] = 0
    try:
        meta['filenumber'] = int(filename.split('_')[-1].split('.')[0])
    except Exception:
        pass
    meta['instrument'] = 'Dynacool'
    meta['filedesc'] = path.basename(filename)
    remark = ''
    title = ''
    is_heatcap = False

    # parse headers
    lines = iter(fp)
    for line in lines:
        line = line.strip()
        if line == '[Data]':
            break
        if not line or line.startswith(';'):
            continue
        parts = line.split(',', 2)
        if parts[0] == 'TITLE':
            title = parts[1]
            continue
        if parts[0] == 'BYAPP' and parts[1] == 'HeatCapacity':
            is_heatcap = True
            continue
        if parts[0] != 'INFO' or len(parts) < 3:
            continue

        if parts[2] == 'VSM_SERIAL_NUMBER':
            meta['instrument'] = parts[1]
        elif parts[2] == 'ACMS_SERIAL_NUMBER':
            meta['instrument'] = parts[1]
        elif parts[2] == 'SAMPLE_MATERIAL':
            remark = parts[1]
        elif parts[2] == 'SAMPLE_COMMENT':
            meta['subtitle'] = parts[1]
        try:
            val = float(parts[1])
        except ValueError:
            val = parts[1]
        meta[parts[2]] = val

    if remark:
        title += ', ' + remark
    meta['title'] = title

    # parse data table
    colnames = next(lines).split(',')
    arr = genfromtxt(lines, delimiter=',', missing_values='0',
                     invalid_raise=False,
                     usecols=list(range(len(colnames))))

    cols = dict((name, arr[:, i]) for (i, name) in enumerate(colnames))
    meta['environment'] = []
    for col in cols:
        meta[col] = cols[col].mean()

    return colnames, arr, meta
