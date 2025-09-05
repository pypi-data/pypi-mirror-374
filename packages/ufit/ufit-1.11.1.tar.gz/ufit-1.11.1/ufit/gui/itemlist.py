#  -*- coding: utf-8 -*-
# *****************************************************************************
# ufit, a universal scattering fitting suite
#
# Copyright (c) 2013-2025, Georg Brandl and contributors.  All rights reserved.
# Licensed under a 2-clause BSD license, see LICENSE.
# *****************************************************************************

"""A list view and model for different session items in the GUI."""

# parts borrowed from M. Janoschek' nfit2 GUI

from ufit.qt import QAbstractItemModel, QAbstractItemView, QListWidget, \
    QListWidgetItem, QModelIndex, QSize, QStyle, QStyledItemDelegate, Qt, \
    QTextDocument, QTreeView, pyqtSignal

from ufit.gui.scanitem import ScanDataItem
from ufit.gui.session import ItemGroup, session
from ufit.utils import from_encoding


class ItemListWidget(QListWidget):
    """Static view of all items, without model."""

    def populate(self, itemcls=None):
        data2obj = {}
        i = 0
        for group in session.groups:
            i += 1
            data2obj[i] = group
            wi = QListWidgetItem('Group: ' + group.name, self, i)
            if itemcls:
                wi.setFlags(Qt.ItemFlag.NoItemFlags)  # make it unselectable
            for item in group.items:
                i += 1
                data2obj[i] = item
                itemstr = '   %d - %s' % (item.index, item.title)
                if isinstance(item, ScanDataItem):
                    itemstr += ' (%s)' % item.data.meta.filedesc
                wi = QListWidgetItem(itemstr, self, i)
                if itemcls and not isinstance(item, itemcls):
                    wi.setFlags(Qt.ItemFlag.NoItemFlags)
        return data2obj


class ItemTreeView(QTreeView):
    newSelection = pyqtSignal()

    def __init__(self, parent):
        QTreeView.__init__(self, parent)
        self.header().hide()
        # self.setRootIsDecorated(False)
        # self.setStyleSheet("QTreeView::branch { display: none; }")
        self.setItemDelegate(ItemListDelegate(self))
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def selectionChanged(self, selected, deselected):
        self.newSelection.emit()
        QTreeView.selectionChanged(self, selected, deselected)


class ItemListModel(QAbstractItemModel):

    def __init__(self):
        QAbstractItemModel.__init__(self)
        session.itemsUpdated.connect(self.reset)
        session.itemUpdated.connect(self.on_session_itemUpdated)
        session.itemAdded.connect(self.on_session_itemAdded)
        session.groupAdded.connect(self.on_session_groupAdded)
        session.groupUpdated.connect(self.on_session_groupUpdated)
        self.groups = session.groups

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

    def index_for_item(self, item):
        groupidx = self.groups.index(item.group)
        groupidx = self.index(groupidx, 0)
        return self.index(item.group.items.index(item), 0, groupidx)

    def index_for_group(self, group):
        return self.index(self.groups.index(group), 0)

    def on_session_itemUpdated(self, item):
        index = self.index_for_item(item)
        self.dataChanged.emit(index, index)

    def on_session_groupUpdated(self, group):
        index = self.index(self.groups.index(group), 0)
        self.dataChanged.emit(index, index)

    def on_session_itemAdded(self, item):
        groupindex = self.index(self.groups.index(item.group), 0)
        self.dataChanged.emit(groupindex, groupindex)
        itemrow = item.group.items.index(item)
        self.rowsInserted.emit(groupindex, itemrow, itemrow)

    def on_session_groupAdded(self, group):
        itemrow = self.groups.index(group)
        self.rowsInserted.emit(QModelIndex(), itemrow, itemrow)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def rowCount(self, index=QModelIndex()):
        if index.isValid():   # data items
            obj = index.internalPointer()
            if isinstance(obj, ItemGroup):
                return len(self.groups[index.row()].items)
            return 0
        return len(self.groups)

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid():  # data items
            group = parent.internalPointer()
            return self.createIndex(row, column, group.items[row])
        return self.createIndex(row, column, self.groups[row])

    def parent(self, index):
        obj = index.internalPointer()
        if isinstance(obj, ItemGroup):
            return QModelIndex()
        group = obj.group
        return self.createIndex(self.groups.index(group), 0, group)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        obj = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return obj.htmldesc
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft |
                       Qt.AlignmentFlag.AlignVCenter)
        return None

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if orientation == Qt.Orientation.Horizontal:
                return int(Qt.AlignmentFlag.AlignLeft |
                           Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignRight |
                       Qt.AlignmentFlag.AlignVCenter)
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        return None


class ItemListDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        text = index.model().data(index)
        palette = self.parent().palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.StateFlag.State_Selected:
            document.setHtml("<font color=%s>%s</font>" %
                             (palette.highlightedText().color().name(),
                              from_encoding(text, 'utf-8', 'ignore')))
            color = palette.highlight().color()
        else:
            document.setHtml(text)
            color = palette.base().color()
        painter.save()
        painter.fillRect(option.rect, color)
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        text = index.model().data(index)
        document = QTextDocument()
        document.setDefaultFont(option.font)
        document.setHtml(text)
        return QSize(round(document.idealWidth()),
                     round(document.size().height()))
