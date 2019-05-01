from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
)
from PyQt5 import uic


class NoteView(QMainWindow):
    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        uic.loadUi('ui/note.ui', self)
        self.noteModel = None
        self.noteTableModel = None
        self.onOpen = None

    def showDebug(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def new(self):
        row = self.noteModel.create()
        self.noteTableModel.insert(0, row)

    def getSelectedRows(self):
        rows = []
        for index in self.noteTable.selectionModel().selectedRows():
            rows.append(self.noteTableModel.getRow(index))
        return rows

    def delete(self):
        for row in self.getSelectedRows():
            try:
                id = int(row[0])
                reply = QMessageBox.question(self, '削除確認', '本当にノート(%d)を削除しますか？' % id, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    continue
                self.noteModel.deleteById(id)
                self.noteTableModel.removeRowById(id)
            except ValueError:
                print('invalid id value')

    def open(self):
        rows = self.getSelectedRows()
        if not len(rows):
            return
        self.onOpenNote(rows[-1][0])

    def changed(self, index):
        row = self.noteTableModel.getRow(index)
        row = self.noteModel.selectById(row[0])
        self.showDebug('changed', dict(row))
