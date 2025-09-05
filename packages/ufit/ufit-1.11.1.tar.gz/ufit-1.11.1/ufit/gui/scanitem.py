#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Session item for datasets and corresponding GUI."""

import re
from os import path

from numpy import array, linspace, mean, savetxt, sqrt

from ufit.qt import QApplication, QDialog, QMessageBox, QTabWidget, QWidget, \
    pyqtSignal, pyqtSlot

from ufit.data.merge import rebin
from ufit.gui import logger
from ufit.gui.common import loadUi
from ufit.gui.dataops import DataOps
from ufit.gui.dialogs import ParamSetDialog
from ufit.gui.fitter import Fitter
from ufit.gui.mappingitem import MappingItem
from ufit.gui.modelbuilder import ModelBuilder
from ufit.gui.session import SessionItem, session
from ufit.models import eval_model
from ufit.param import prepare_params
from ufit.utils import from_encoding


def default_model(data):
    ymin = data.y.min()
    ymaxidx = data.y.argmax()
    ymax = data.y[ymaxidx]
    xmax = data.x[ymaxidx]
    overhalf = data.x[data.y > (ymax + ymin)/2.]
    if len(overhalf) >= 2:
        xwidth = abs(overhalf[0] - overhalf[-1]) or 0.1
    else:
        xwidth = 0.1
    new_model = eval_model('Background() + Gauss(\'peak\')')
    new_model.params[0].value = ymin
    new_model.params[1].value = xmax
    new_model.params[2].value = ymax-ymin
    new_model.params[3].value = xwidth
    return new_model


class ScanDataItem(SessionItem):
    newModel = pyqtSignal(object, bool)

    itemtype = 'scan'

    def __init__(self, data, model=None):
        self.data = data
        self.model = model or default_model(data)
        SessionItem.__init__(self)

    def change_model(self, model, keep_param_values=True):
        self.model = model
        self.newModel.emit(model, keep_param_values)
        session.set_dirty()

    def after_load(self):
        self.data.after_load()  # upgrade datastructures

    def __reduce__(self):
        return (self.__class__, (self.data, self.model))

    def create_panel(self, mainwindow, canvas):
        return ScanDataPanel(mainwindow, canvas, self)

    def create_multi_panel(self, mainwindow, canvas):
        return MultiDataOps(mainwindow, canvas)

    def update_htmldesc(self):
        title = self.data.title
        self.title = title
        htmldesc = '<big><b>%s</b></big>' % self.index + \
            (title and ' - %s' % title or '') + \
            (self.data.environment and
             '<br>%s' % ', '.join(self.data.environment) or '') + \
            ('<br><small>%s</small>' % '<br>'.join(self.data.sources[:5]))
        if len(self.data.sources) > 5:
            htmldesc += '<br><small>...</small>'
        self.htmldesc = htmldesc
        session.itemsUpdated.emit()

    def export_python(self, filename):
        with open(filename, 'w') as fp:
            fp.write('from ufit.lab import *\n')
            fp.write('\n')
            self.data.export_python(fp, 'data')
            fp.write('\n')
            self.model.export_python(fp, 'model')
            fp.write('''\
## just plot current values
data.plot()
model.plot_components(data)
model.plot(data)

## to fit again use this...
#result = model.fit(data)
#result.printout()
#result.plot()

show()
''')

    def export_ascii(self, filename):
        with open(filename, 'wb') as fp:
            self.data.export_ascii(fp)

    def export_fits(self, filename):
        xx = linspace(self.data.x.min(), self.data.x.max(), 1000)
        paramvalues = prepare_params(self.model.params, self.data.meta)[3]
        yy = self.model.fcn(paramvalues, xx)
        yys = []
        for comp in self.model.get_components():
            if comp is self.model:
                continue
            yys.append(comp.fcn(paramvalues, xx))
        savetxt(filename, array([xx, yy] + yys).T)


class ScanDataPanel(QTabWidget):
    def __init__(self, parent, canvas, item):
        QTabWidget.__init__(self, parent)
        self.item = item
        self.dataops = DataOps(self)
        self.mbuilder = ModelBuilder(self)
        self.fitter = Fitter(self)
        self._limits = None
        self._dont_update_modeldef = False
        self.picker_widget = None

        self.item.newModel.connect(self.on_item_newModel)

        self.canvas = canvas
        self.dataops.initialize(item)
        self.mbuilder.initialize(item.data, item.model)
        self.fitter.initialize(item.model, item.data, fit=False)
        self.dataops.pickRequest.connect(self.set_picker)
        self.dataops.replotRequest.connect(self.plot)
        self.dataops.titleChanged.connect(self.item.update_htmldesc)
        self.mbuilder.newModel.connect(self.on_mbuilder_newModel)
        self.mbuilder.pickRequest.connect(self.set_picker)
        self.fitter.replotRequest.connect(self.plot)
        self.fitter.pickRequest.connect(self.set_picker)
        self.addTab(self.dataops, 'Data operations')
        self.addTab(self.mbuilder, 'Modeling')
        self.addTab(self.fitter, 'Fitting')
        self.setCurrentWidget(self.mbuilder)

    def on_mbuilder_newModel(self, model, update_modeldef=False,
                             switch_fitter=True):
        self._dont_update_modeldef = not update_modeldef
        try:
            self.item.change_model(model)
        finally:
            self._dont_update_modeldef = False
        if switch_fitter:
            self.setCurrentWidget(self.fitter)

    def on_item_newModel(self, model, keep_param_values):
        if not self._dont_update_modeldef:
            self.mbuilder.modeldefEdit.setText(model.get_description())
        self.fitter.initialize(model, self.item.data, fit=False,
                               keep_old=keep_param_values)

    def set_picker(self, widget):
        self.picker_widget = widget

    def on_canvas_pick(self, event):
        if self.picker_widget:
            self.picker_widget.on_canvas_pick(event)

    def save_limits(self):
        self._limits = self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim()

    def get_saved_limits(self):
        return self._limits

    def plot(self, limits=True, canvas=None):
        canvas = canvas or self.canvas
        plotter = canvas.plotter
        plotter.reset(limits)
        try:
            plotter.plot_data(self.item.data)
            plotter.plot_model_full(self.item.model, self.item.data)
        except Exception:
            logger.exception('Error while plotting')
        else:
            canvas.draw()

    def export_ascii(self, filename):
        self.item.export_ascii(filename)

    def export_fits(self, filename):
        self.item.export_fits(filename)

    def export_python(self, filename):
        self.item.export_python(filename)


class MultiDataOps(QWidget):
    replotRequest = pyqtSignal(object)

    def __init__(self, parent, canvas):
        QWidget.__init__(self, parent)
        self.mainwindow = parent
        self.canvas = canvas
        self.replotRequest.connect(self.plot)

        loadUi(self, 'multiops.ui')

    def initialize(self, items):
        self.items = [i for i in items if isinstance(i, ScanDataItem)]
        self.datas = [i.data for i in self.items]
        self.monscaleEdit.setText(
            str(int(mean([d.nscale for d in self.datas]))))
        self.onemodelBox.clear()
        self.onemodelBox.addItems(['%d' % i.index for i in self.items])

    def plot(self, limits=True, canvas=None):
        canvas = canvas or self.canvas
        xlabels = set()
        ylabels = set()
        titles = set()
        canvas.plotter.reset()
        for i in self.items:
            c = canvas.plotter.plot_data(i.data, multi=True)
            canvas.plotter.plot_model(i.model, i.data, labels=False, color=c)
            xlabels.add(i.data.xaxis)
            ylabels.add(i.data.yaxis)
            titles.add(i.data.title)
        canvas.plotter.plot_finish(', '.join(xlabels), ', '.join(ylabels),
                                   from_encoding(', '.join(titles),
                                                 'ascii', 'ignore'))
        canvas.draw()

    @pyqtSlot()
    def on_rebinBtn_clicked(self):
        try:
            binsize = float(self.precisionEdit.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Enter a valid precision.')
            return
        for data in self.datas:
            new_array, new_meta = rebin(array(data._data), binsize, data.meta)
            data.__init__(new_meta, new_array,
                          data.xcol, data.ycol, data.ncol,
                          data.nscale, name=data.name,
                          sources=data.sources)
        self.replotRequest.emit(None)
        session.set_dirty()

    @pyqtSlot()
    def on_mulBtn_clicked(self):
        try:
            const = float(self.scaleConstEdit.text())
        except ValueError:
            return
        for data in self.datas:
            data.y *= const
            data.y_raw *= const
            data.dy *= const
            data.dy_raw *= const
        self.replotRequest.emit(None)
        session.set_dirty()

    @pyqtSlot()
    def on_addBtn_clicked(self):
        try:
            const = float(self.addConstEdit.text())
        except ValueError:
            return
        for data in self.datas:
            data.y += const
            data.y_raw += const * data.norm
        self.replotRequest.emit(None)
        session.set_dirty()

    @pyqtSlot()
    def on_scaleXBtn_clicked(self):
        try:
            const = float(self.scaleXConstEdit.text())
        except ValueError:
            return
        for data in self.datas:
            data.x *= const
        self.replotRequest.emit(None)
        session.set_dirty()

    @pyqtSlot()
    def on_shiftBtn_clicked(self):
        try:
            const = float(self.shiftConstEdit.text())
        except ValueError:
            return
        for data in self.datas:
            data.x += const
        self.replotRequest.emit(None)
        session.set_dirty()

    @pyqtSlot()
    def on_monscaleBtn_clicked(self):
        try:
            const = int(self.monscaleEdit.text())
        except ValueError:
            return
        for data in self.datas:
            data.nscale = const
            data.norm = data.norm_raw / const
            data.y = data.y_raw/data.norm
            data.dy = sqrt(data.y_raw)/data.norm
            data.yaxis = data.ycol + ' / %s %s' % (const, data.ncol)
        self.replotRequest.emit(None)
        session.set_dirty()

    @pyqtSlot()
    def on_mergeBtn_clicked(self):
        try:
            precision = float(self.mergeEdit.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Enter a valid precision.')
            return
        new_data = self.datas[0].merge(precision, *self.datas[1:])
        session.add_item(ScanDataItem(new_data), self.items[-1].group)

    @pyqtSlot()
    def on_floatMergeBtn_clicked(self):
        try:
            precision = float(self.mergeEdit.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Enter a valid precision.')
            return
        new_data = self.datas[0].merge(precision, floatmerge=True,
                                       *self.datas[1:])
        session.add_item(ScanDataItem(new_data), self.items[-1].group)

    @pyqtSlot()
    def on_onemodelBtn_clicked(self):
        which = self.onemodelBox.currentIndex()
        if which < 0:
            return
        src_item = self.items[which]
        with_params = self.onemodelWithParamsBox.isChecked()
        # ensure params are updated from the last entered values in controls
        if with_params:
            src_panel = self.mainwindow.itempanels.get(src_item)
            if src_panel:
                src_panel.fitter.update_from_controls()
        for i, item in enumerate(self.items):
            if i == which:
                continue
            item.change_model(src_item.model.copy(),
                              keep_param_values=not with_params)
        self.replotRequest.emit(None)

    @pyqtSlot()
    def on_fitallBtn_clicked(self):
        results = []
        n = len(self.items)
        for (i, item) in enumerate(self.items):
            self.fitallLbl.setText(f'Working on dataset {i+1}/{n}...')
            QApplication.processEvents()
            res = item.model.fit(item.data)
            results.append(
                f'{item.data.title} {item.data.name}: ' +
                (res.success and 'Converged. ' or 'Failed. ') + res.message +
                ' Reduced chi^2 = %.3g.' % res.chisqr)
            session.modelFitted.emit(item, res)
        self.fitallLbl.setText('')
        resdlg = QDialog(self)
        loadUi(resdlg, 'results.ui')
        resdlg.textBox.setText('\n'.join(results))
        resdlg.show()
        self.replotRequest.emit(None)

    @pyqtSlot()
    def on_paramsetBtn_clicked(self):
        dlg = ParamSetDialog(self, self.items)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        session.add_item(ScanDataItem(dlg.new_data), self.items[-1].group)

    @pyqtSlot()
    def on_mappingBtn_clicked(self):
        item = MappingItem([item.data for item in self.items], None)
        session.add_item(item, self.items[-1].group)

    @pyqtSlot()
    def on_globalfitBtn_clicked(self):
        QMessageBox.warning(self, 'Sorry', 'Not implemented yet.')

    def export_ascii(self, filename):
        base, ext = path.splitext(filename)
        for i, item in enumerate(self.items):
            item.export_ascii(base + '.%d' % i + ext)

    def export_fits(self, filename):
        base, ext = path.splitext(filename)
        for i, item in enumerate(self.items):
            item.export_fits(base + '.%d' % i + ext)

    def export_python(self, filename):
        base, ext = path.splitext(filename)
        for i, item in enumerate(self.items):
            item.export_python(base + '.%d' % i + ext)

    @pyqtSlot()
    def on_massrenameBtn_clicked(self):
        dlg = QDialog(self)
        loadUi(dlg, 'massrename.ui')
        dlg.availEdit.setText('name, ' + ', '.join(self.items[0].data.meta))
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        title_tpl = dlg.titleEdit.text()
        name_tpl = dlg.nameEdit.text()
        for item in self.items:
            def repl(m):
                key = m.group(1)
                if key == 'name':
                    return item.data.name
                return str(item.data.meta.get(key, '?'))

            item.data.meta.title = re.sub(r'\{(.*?)\}', repl, title_tpl)
            item.data.name = re.sub(r'\{(.*?)\}', repl, name_tpl)
            item.update_htmldesc()

            panel = self.mainwindow.itempanels.get(item)
            if panel:
                panel.dataops.initialize(item)
        session.set_dirty()
        self.replotRequest.emit(None)
