#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Data browsing window for the standalone GUI."""

import os
from os import path

from ufit.qt import QApplication, QByteArray, QFileDialog, QFont, \
    QListWidgetItem, QMainWindow, QTextCursor, QVBoxLayout, pyqtSlot

from ufit.data import Loader
from ufit.gui import logger
from ufit.gui.common import MPLCanvas, MPLToolbar, SettingGroup, loadUi, \
    path_to_str
from ufit.gui.scanitem import ScanDataItem
from ufit.gui.session import session
from ufit.utils import extract_template


class Unavailable:
    def __format__(self, fmt):
        # Accepts all format strings (important for e.g. ".2f")
        return '???'


class FormatWrapper:
    """Wraps a dataset for the purposes of format() not raising exceptions."""

    def __init__(self, n, dataset):
        self.__n = n
        self.__dataset = dataset

    def __getattr__(self, attr, default=Unavailable()):
        if attr == 'n':
            return self.__n
        val = getattr(self.__dataset, attr, default)
        if isinstance(val, list):
            return ', '.join(map(str, val))
        return val

    def __getitem__(self, attr):
        return getattr(self, attr)


class BrowseWindow(QMainWindow):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        loadUi(self, 'browse.ui')
        self.logger = logger.getChild('browse')

        self.dataloader = parent
        self.rootdir = ''
        self.loader = Loader()
        self._data = {}
        self.yaxis = None
        self.canvas = MPLCanvas(self)
        self.canvas.plotter.lines = True
        self.toolbar = MPLToolbar(self.canvas, self)
        self.toolbar.setObjectName('browsetoolbar')
        self.addToolBar(self.toolbar)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.plotframe.setLayout(layout)
        self.sgroup = SettingGroup('browse')

        font = self.fileText.font()
        font.setFamily('Monospace')
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.fileText.setFont(font)

        with self.sgroup as settings:
            geometry = settings.value('geometry', QByteArray())
            self.restoreGeometry(geometry)
            windowstate = settings.value('windowstate', QByteArray())
            self.restoreState(windowstate)
            splitstate = settings.value('splitstate', QByteArray())
            self.splitter.restoreState(splitstate)
            def_fmtstr = self.fmtStringEdit.text()
            self.fmtStringEdit.setText(settings.value('fmtstring', def_fmtstr))
            self.monScaleEdit.setText(settings.value('fixedmonval'))
            self.noNormalize.setChecked(bool(settings.value('nonorm')))

    @pyqtSlot()
    def on_loadBtn_clicked(self):
        datas = [self._data[item.type()]
                 for item in self.dataList.selectedItems()]
        if not datas:
            return
        items = [ScanDataItem(data) for data in datas]
        session.add_items(items)

    @pyqtSlot()
    def on_addNumBtn_clicked(self):
        numors = [self._data[item.type()].meta['filenumber']
                  for item in self.dataList.selectedItems()]
        if not numors:
            return
        self.dataloader.add_numors(sorted(numors))

    @pyqtSlot()
    def on_dirBtn_clicked(self):
        newdir = QFileDialog.getExistingDirectory(self, 'New directory',
                                                  self.rootdir)
        self.set_directory(path_to_str(newdir))

    @pyqtSlot()
    def on_refreshBtn_clicked(self):
        self.set_directory(self.rootdir)

    def set_directory(self, root):
        self.setWindowTitle('ufit browser - %s' % root)
        self.canvas.axes.text(0.5, 0.5, 'Please wait, loading all data...',
                              horizontalalignment='center')
        self.canvas.draw()
        QApplication.processEvents()
        self.rootdir = root
        files = os.listdir(root)
        self.dataList.clear()

        normcol = None if self.noNormalize.isChecked() else 'auto'
        for fn in sorted(files):
            fn = path.join(root, fn)
            if not path.isfile(fn):
                continue
            try:
                t, n = extract_template(fn)
                self.loader.template = t
                fixed_yaxis = self.yAxisEdit.text()
                yaxis = fixed_yaxis if (fixed_yaxis and
                                        self.useYAxis.isChecked()) else 'auto'
                res = self.loader.load(n, 'auto', yaxis, 'auto', normcol, -1)
            except Exception as e:
                self.logger.warning('While loading %r: %s' % (fn, e))
            else:
                if self.useMonScale.isChecked() and normcol:
                    const = int(self.monScaleEdit.text())  # XXX check
                    res.rescale(const)
                if self.useFmtString.isChecked():
                    try:
                        scan_label = self.fmtStringEdit.text().format_map(
                            FormatWrapper(n, res))
                    except Exception:
                        scan_label = '%s (%s) - %s | %s' % (
                            n, res.xcol, res.title, ', '.join(res.environment))
                else:
                    scan_label = '%s (%s) - %s | %s' % (
                        n, res.xcol, res.title, ', '.join(res.environment))
                self._data[n] = res
                QListWidgetItem(scan_label, self.dataList, n)
        self.canvas.axes.clear()
        self.canvas.draw()

    def on_dataList_itemSelectionChanged(self):
        numors = [item.type() for item in self.dataList.selectedItems()]
        if not numors:
            return
        plotter = self.canvas.plotter
        plotter.reset(False)
        if len(numors) > 1:
            for numor in numors:
                plotter.plot_data(self._data[numor], multi=True)
            plotter.plot_finish()
        else:
            plotter.plot_data(self._data[numors[0]])
        plotter.draw()

        filename = self._data[numors[-1]].meta['datafilename']
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        vscrollpos = self.fileText.verticalScrollBar().value()
        hscrollpos = self.fileText.horizontalScrollBar().value()
        self.fileText.setPlainText(text)
        self.fileText.verticalScrollBar().setValue(vscrollpos)
        self.fileText.horizontalScrollBar().setValue(hscrollpos)

    def closeEvent(self, event):
        event.accept()
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())
            settings.setValue('windowstate', self.saveState())
            settings.setValue('splitstate', self.splitter.saveState())
            settings.setValue('fmtstring', self.fmtStringEdit.text())
            settings.setValue('fixedmonval', self.monScaleEdit.text())
            settings.setValue('nonorm', self.noNormalize.isChecked())
