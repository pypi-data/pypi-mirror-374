#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""Common GUI elements."""

import sys
from io import BytesIO
from os import path

import matplotlib.backends.qt_editor.figureoptions
from matplotlib import pyplot
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qtagg import \
    FigureCanvasQTAgg as FigureCanvas, FigureManagerQT, NavigationToolbar2QT
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure

from ufit.qt import QByteArray, QDialog, QFileDialog, QIcon, QLabel, \
    QLineEdit, QMessageBox, QPageLayout, QPainter, QPrintDialog, QPrinter, \
    QPrintPreviewWidget, QRectF, QSettings, QSize, QSizePolicy, QSvgRenderer, \
    Qt, pyqtSignal, uic

pyplot.rc('font', family='sans-serif')
pyplot.rc('font', **{'sans-serif': 'Sans Serif, Arial, Helvetica, '
                     'Lucida Grande, DejaVu Sans'})

# pylint: disable=wrong-import-position
from ufit.gui import logger
from ufit.gui.ploteditor import figure_edit
from ufit.gui.session import session
from ufit.plotting import DataPlotter

# override figure editor with our extended version
matplotlib.backends.qt_editor.figureoptions.figure_edit = figure_edit

uipath = path.dirname(__file__)


def loadUi(widget, uiname, subdir='ui'):
    uic.loadUi(path.join(uipath, subdir, uiname), widget)


def path_to_str(qstring):
    return qstring


def str_to_path(string):
    if not isinstance(string, str):
        return string.decode(sys.getfilesystemencoding())
    return string


class MPLCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    logzChanged = pyqtSignal()
    replotRequest = pyqtSignal()

    def __init__(self, parent, width=10, height=6, dpi=72, maincanvas=False):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor('white')
        self.print_width = 0
        self.main = parent
        self.logz = False
        self.axes = fig.add_subplot(111)
        self.plotter = DataPlotter(self, self.axes)
        # make tight_layout do the right thing
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        self.axes.set_title('(data title)\n(info)')
        FigureCanvas.__init__(self, fig)

        # create a figure manager so that we can use pylab commands on the
        # main viewport
        def make_active(event):
            Gcf.set_active(self.manager)
        self.manager = FigureManagerQT(self, 1)
        self.manager._cidgcf = self.mpl_connect('button_press_event', make_active)
        Gcf.set_active(self.manager)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        # actually get key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.mpl_connect('key_press_event', self.key_press)
        # These will not do anything in standalone mode, but do not hurt.
        if maincanvas:
            session.propsRequested.connect(self.on_session_propsRequested)
            session.propsUpdated.connect(self.on_session_propsUpdated)

    def on_session_propsRequested(self):
        session.props.canvas_logz = self.logz

    def on_session_propsUpdated(self):
        if 'canvas_logz' in session.props:
            self.logz = session.props.canvas_logz
            self.logzChanged.emit()

    def key_press(self, event):
        key_press_handler(event, self)

    def resizeEvent(self, event):
        FigureCanvas.resizeEvent(self, event)
        self.figure.tight_layout(pad=2)

    def print_(self):
        sio = BytesIO()
        self.print_figure(sio, format='svg')
        svg = QSvgRenderer(QByteArray(sio.getvalue()))
        sz = svg.defaultSize()
        aspect = sz.width()/float(sz.height())

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)

        dlg = QDialog(self)
        loadUi(dlg, 'printpreview.ui')
        dlg.width.setValue(self.print_width or 500)
        ppw = QPrintPreviewWidget(printer, dlg)
        dlg.layout().insertWidget(1, ppw)

        def render(printer):
            height = printer.height() * (dlg.width.value()/1000.)
            width = aspect * height
            painter = QPainter(printer)
            svg.render(painter, QRectF(0, 0, width, height))

        def sliderchanged(newval):
            ppw.updatePreview()

        ppw.paintRequested.connect(render)
        dlg.width.valueChanged.connect(sliderchanged)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.print_width = dlg.width.value()
        pdlg = QPrintDialog(printer, self)
        if pdlg.exec() != QDialog.DialogCode.Accepted:
            return
        render(printer)

    def ufit_replot(self):
        self.replotRequest.emit()


class MPLToolbar(NavigationToolbar2QT):

    popoutRequested = pyqtSignal()

    icon_name_map = {
        'home.png':         'magnifier-zoom-fit.png',
        'back.png':         'arrow-180.png',
        'forward.png':      'arrow.png',
        'move.png':         'arrow-move.png',
        'zoom_to_rect.png': 'selection-resize.png',
        'filesave.png':     'document-pdf.png',
        'printer.png':      'printer.png',
        'pyconsole.png':    'terminal--arrow.png',
        'log-x.png':        'log-x.png',
        'log-y.png':        'log-y.png',
        'log-z.png':        'log-z.png',
        'exwindow.png':    'chart--arrow.png',
    }

    toolitems = list(NavigationToolbar2QT.toolitems)
    del toolitems[7]  # subplot adjust
    toolitems.insert(0, ('Log x', 'Logarithmic X scale', 'log-x',
                         'logx_callback'))
    toolitems.insert(1, ('Log y', 'Logarithmic Y scale', 'log-y',
                         'logy_callback'))
    toolitems.insert(2, ('Log z', 'Logarithmic Z scale for images', 'log-z',
                         'logz_callback'))
    toolitems.insert(3, (None, None, None, None))
    toolitems.append(('Print', 'Print the figure', 'printer',
                      'print_callback'))
    toolitems.append(('Pop out', 'Show the figure in a separate window',
                      'exwindow', 'popout_callback'))
    toolitems.append(('Execute', 'Show Python console', 'pyconsole',
                      'exec_callback'))

    def __init__(self, *args, **kwds):
        NavigationToolbar2QT.__init__(self, *args, **kwds)
        self.locLabel.setAlignment(Qt.AlignmentFlag.AlignRight |
                                   Qt.AlignmentFlag.AlignVCenter)
        self._actions['logx_callback'].setCheckable(True)
        self._actions['logy_callback'].setCheckable(True)
        self._actions['logz_callback'].setCheckable(True)
        self.canvas.logzChanged.connect(self.on_canvas_logzChanged)

    def _icon(self, name, color=None):
        if name in self.icon_name_map:
            return QIcon(':/' + self.icon_name_map[name])
        return QIcon()

    def home(self, *args):
        # always unzoom completely
        if hasattr(self, '_views'):
            self._views.clear()
        if hasattr(self, '_positions'):
            self._positions.clear()
        self.canvas.figure.gca().autoscale()
        self.canvas.draw()
        return NavigationToolbar2QT.home(self)

    def logx_callback(self):
        ax = self.canvas.figure.gca()
        if ax.get_xscale() == 'linear':
            ax.set_xscale('symlog')
            self._actions['logx_callback'].setChecked(True)
        else:
            ax.set_xscale('linear')
            self._actions['logx_callback'].setChecked(False)
        self.canvas.draw()

    def logy_callback(self):
        ax = self.canvas.figure.gca()
        if ax.get_yscale() == 'linear':
            ax.set_yscale('symlog')
            self._actions['logy_callback'].setChecked(True)
        else:
            ax.set_yscale('linear')
            self._actions['logy_callback'].setChecked(False)
        self.canvas.draw()

    def logz_callback(self):
        ax = self.canvas.figure.gca()
        self.canvas.logz = not self.canvas.logz
        session.set_dirty()
        self._actions['logz_callback'].setChecked(self.canvas.logz)
        for im in ax.get_images():
            if self.canvas.logz:
                im.set_norm(LogNorm())
            else:
                im.set_norm(None)
        self.canvas.draw()

    def on_canvas_logzChanged(self):
        self._actions['logz_callback'].setChecked(self.canvas.logz)

    def print_callback(self):
        self.canvas.print_()

    def popout_callback(self):
        self.popoutRequested.emit()

    def exec_callback(self):
        try:
            from ufit.gui.console import ConsoleWindow
        except ImportError:
            logger.exception('Qt console window cannot be opened without '
                             'IPython; import error was:')
            QMessageBox.information(self, 'ufit',
                                    'Please install IPython with qtconsole to '
                                    'activate this function.')
            return
        try:
            w = ConsoleWindow(self)
        except Exception as err:
            logger.exception('Qt console window cannot be opened without '
                             'IPython; import error was:')
            QMessageBox.information(self, 'ufit', 'IPython qtconsole '
                                    f'seems to be broken: {err}')
            return
        w.ipython.executeCommand('from ufit.lab import *')
        w.ipython.pushVariables({
            'fig': self.canvas.figure,
            'ax': self.canvas.figure.gca(),
            'D': [item for group in session.groups for item in group.items],
        })
        w.show()

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = sorted(filetypes.items())

        start = self.canvas.get_default_filename()
        filters = []
        for name, exts in sorted_filetypes:
            if 'eps' in exts or 'emf' in exts or 'jpg' in exts or \
               'pgf' in exts or 'raw' in exts:
                continue
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filt = '%s (%s)' % (name, exts_list)
            filters.append(filt)
        filters = ';;'.join(filters)
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Choose a filename to save to', start, filters)
        if fname:
            try:
                self.canvas.print_figure(str(fname))
            except Exception as e:
                logger.exception('Error saving file')
                QMessageBox.critical(self, 'Error saving file', str(e))


class SmallLineEdit(QLineEdit):
    def sizeHint(self):
        sz = QLineEdit.sizeHint(self)
        return QSize(round(sz.width() / 1.5), sz.height())


class SettingGroup:
    def __init__(self, name):
        self.name = name
        self.settings = QSettings('ufit', 'gui')

    def __enter__(self):
        self.settings.beginGroup(self.name)
        return self.settings

    def __exit__(self, *args):
        self.settings.endGroup()
        self.settings.sync()


class SqueezedLabel(QLabel):
    """A label that elides text to fit its width."""

    def __init__(self, parent, designMode=False, **kwds):
        self._fulltext = ''
        QLabel.__init__(self, parent, **kwds)
        self._squeeze()

    def resizeEvent(self, event):
        self._squeeze()
        QLabel.resizeEvent(self, event)

    def setText(self, text):
        self._fulltext = text
        self._squeeze(text)

    def minimumSizeHint(self):
        sh = QLabel.minimumSizeHint(self)
        sh.setWidth(-1)
        return sh

    def _squeeze(self, text=None):
        if text is None:
            text = self._fulltext or self.text()
        fm = self.fontMetrics()
        labelwidth = self.size().width()
        squeezed = False
        new_lines = []
        for line in text.split('\n'):
            if fm.horizontalAdvance(line) > labelwidth:
                squeezed = True
                new_lines.append(fm.elidedText(
                    line, Qt.TextElideMode.ElideRight, labelwidth))
            else:
                new_lines.append(line)
        if squeezed:
            QLabel.setText(self, '\n'.join(new_lines))
            self.setToolTip(self._fulltext)
        else:
            QLabel.setText(self, self._fulltext)
            self.setToolTip('')
