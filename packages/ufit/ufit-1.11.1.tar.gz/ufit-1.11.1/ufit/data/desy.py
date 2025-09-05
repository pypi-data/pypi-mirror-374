#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Load routine for DESY scattering data."""

import io
import time

from numpy import array, genfromtxt


def check_data(fp):
    line1 = fp.readline()
    line2 = fp.readline()
    fp.seek(0, 0)
    return line1.strip() == b'!' and line2.strip() == b'! Comments'


def guess_cols(colnames, coldata, meta):
    xg, yg, mg = None, 'mag_c06', 'sumvfcs_counts'
    if 'h_position' in colnames:
        qhindex = colnames.index('h_position')
        deviations = array([(cs.max()-cs.min())
                            for cs in coldata.T[qhindex:qhindex+3]])
        xg = colnames[qhindex + deviations.argmax()]
    return xg, yg, None, mg


def read_data(filename, fp):
    fp = io.TextIOWrapper(fp, 'ascii', 'ignore')
    meta = {}
    mode = None
    cline = 0
    names = []

    for line in fp:
        if line.startswith('!'):
            pass
        elif line.startswith('%'):
            mode = line[1:2]
        elif mode == 'c':  # Comments
            if cline == 0:
                meta['subtitle'] = line.strip()
            elif cline == 1:
                meta['users'] = line.split()[1]
                ix = line.find('Acquisition started')
                if ix > 0:
                    meta['date'] = line[ix+23:].strip()
                    meta['created'] = time.mktime(time.strptime(
                        line[ix:].strip(),
                        'Acquisition started at %a %b %d %H:%M:%S %Y'))
            cline += 1
        elif mode == 'p':  # Parameters
            try:
                name, val = line.split(' = ', 1)
                meta[name] = float(val)
            except ValueError:
                pass
        elif mode == 'd':  # Data
            if line.startswith(' Col'):
                parts = line.split()
                names.append(parts[2])
            else:
                lines = [line]
                lines.extend(fp)
                arr = genfromtxt(lines, comments='!')
                break

    for i, n in enumerate(names):
        meta[n] = arr[:, i].mean()

    meta['environment'] = []
    for name in names:
        if name.endswith('persistentfieldt'):
            meta['environment'].append('B = %.5f T' % meta[name])
        elif name.endswith('tempprobe'):
            meta['environment'].append('T = %.3f K' % meta[name])

    if 'h_position' in names:
        qhindex = names.index('h_position')
        meta['hkle'] = arr[:, qhindex:qhindex+3]
        meta['hkle'] = array([(h, k, l, 0) for (h, k, l) in meta['hkle']])
        deviations = array([(cs.max()-cs.min())
                            for cs in arr.T[qhindex:qhindex+3]])
        meta['hkle_vary'] = ['h', 'k', 'l', 'E'][deviations.argmax()]

    return names, arr, meta
