from PyQt5.QtCore import (
    QAbstractItemModel,
    QAbstractTableModel,
    QModelIndex,
    Qt,
)
from models.note import NoteModel


class NoteTableModel(QAbstractItemModel):
    def __init__(self, dbConn):
        super().__init__()
        self.dbConn = dbConn
        self.noteModel = NoteModel(self.dbConn)
        self.header_labels = ['ID', '作成日', 'タイトル']
        self.items = [
            ['1', '2019', 'dummy title'],
        ]

    def insert(self, index, row):
        self.items.insert(index, [row['id'], row['created'], row['title']])
        self.layoutChanged.emit()

    def getRow(self, index):
        return self.items[index.row()]

    def removeRowById(self, id_):
        for i in range(len(self.items)):
            try:
                rid = int(self.items[i][0])
            except ValueError:
                pass

            if rid == id_:
                self.items.pop(i)
                self.layoutChanged.emit()
                return

    def load(self):
        self.items = []
        rows = self.noteModel.selectAll()
        for row in rows:
            self.items.append([row['id'], row['created'], row['title']])
        self.layoutChanged.emit()

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, None)

    def parent(self, child):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        if self.items:
            return max([len(item) for item in self.items])
        return 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            try:
                return self.items[index.row()][index.column()]
            except:
                return None
        return

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 2:
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        return Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if not len(value):
            return False

        if index.isValid() and role == Qt.EditRole and index.column() == 2:
            id = self.items[index.row()][0]
            self.noteModel.update(id=id, title=value)
            self.items[index.row()][2] = value
            self.layoutChanged.emit()
            return True
        return False