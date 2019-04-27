from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
)
from PyQt5 import uic
from os.path import expanduser
from pathlib import Path
import os
import resources
import sqlite3
import shutil


class NoteListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def parseText(self, text):
        cols = text.split(',')
        if len(cols) != 2:
            return None
        return { 'id': cols[0], 'created': cols[1] }

    def parseRow(self, dict_row):
        return '{id}, {created}'.format(id=dict_row['id'], created=dict_row['created'])


class NoteBookModel:
    def __init__(self, remove_settings=False):
        self.remove_settings = remove_settings
        self.initEnv()
        self.initDB()

    def initEnv(self):
        self.homePath = expanduser('~')
        self.settingDirPath = os.path.join(self.homePath, '.note')
        
        if self.remove_settings:
            shutil.rmtree(self.settingDirPath)

        if not os.path.exists(self.settingDirPath):
            os.mkdir(self.settingDirPath)

        self.dbPath = os.path.join(self.settingDirPath, 'db.sqlite3')
        if not os.path.exists(self.dbPath):
            Path(self.dbPath).touch()

    def initDB(self):
        self.dbConn = sqlite3.connect(self.dbPath)
        self.dbConn.row_factory = sqlite3.Row

        cursor = self.dbConn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                content TEXT NOT NULL DEFAULT "内容なし"
            );
        ''')
        self.dbConn.commit()


class NoteModel:
    def __init__(self, dbConn):
        self.dbConn = dbConn

    def create(self):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            INSERT INTO note DEFAULT VALUES;
        ''')
        self.dbConn.commit()

        cursor.execute('''
            SELECT * FROM note WHERE id = ?
        ''', (cursor.lastrowid, ))
        row = cursor.fetchone()
        return row

    def deleteById(self, rid):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT * FROM note WHERE id = ?
        ''', (rid, ))
        row = cursor.fetchone()

        cursor.execute('''
            DELETE FROM note WHERE id = ?
        ''', (rid, ))
        self.dbConn.commit()

        return row
    
    def selectById(self, rid):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT * FROM note WHERE id = ?
        ''', (rid, ))
        row = cursor.fetchone()
        return row

    def update(self, id, content):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            UPDATE note SET content = ? WHERE id = ?;
        ''', (content, id, ))
        self.dbConn.commit()

    def selectAll(self):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT * FROM note;
        ''')
        return cursor.fetchall()


class NoteBookView(QMainWindow):
    def __init__(self, noteBookModel, debug=False):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.debug = debug
        self.noteModel = NoteModel(noteBookModel.dbConn)
        self.noteListModel = NoteListModel()
        self.load()
        self.smsg("I'm ready")

    def smsg(self, msg):
        self.statusBar().showMessage(msg)

    def showDebug(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def load(self):
        rows = self.noteModel.selectAll()
        rows = sorted(rows, key=lambda row: -int(row['id']))
        for row in rows:
            text = self.noteListModel.parseRow(row)
            item = QStandardItem(text)
            self.noteListModel.appendRow(item)
        self.smsg('load complete')

    def new(self):
        row = self.noteModel.create()
        text = self.noteListModel.parseRow(row)
        item = QStandardItem(text)
        self.noteListModel.insertRow(0, item)
        self.textEdit.setText(row['content'])
        self.titleEdit.setText(text)
        self.showDebug('inserted', dict(row))
        self.smsg('created new note')

    def delete(self):
        selectionModel = self.noteList.selectionModel()
        indexes = selectionModel.selectedIndexes()
        if not len(indexes):
            QMessageBox.about(self, '日記が選択されていません', '削除する日記を選択して下さい。')
            return

        reply = QMessageBox.question(self, '削除確認', '本当にこの日記を削除しますか？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        for index in indexes:
            text = self.noteListModel.itemFromIndex(index).text()
            row = self.noteListModel.parseText(text)
            if row is None:
                continue
            row = self.noteModel.deleteById(row['id'])
            self.showDebug('deleted', dict(row))
            self.smsg('deleted note by id "%d"' % (row['id'], ))

        for index in indexes:
            self.noteListModel.removeRow(index.row())


    def save(self):
        selectedTitle = self.titleEdit.text()
        row = self.noteListModel.parseText(selectedTitle)
        if row is None:
            return

        row['content'] = self.textEdit.toPlainText()
        self.noteModel.update(id=row['id'], content=row['content'])
        self.showDebug('updated', row)
        self.smsg('updated note by id "%s"' % (row['id'], ))
        QMessageBox.about(self, '保存結果', '日記の保存に成功しました。')

    def changed(self, selected, deselected):
        for index in selected.indexes():
            text = self.noteListModel.itemFromIndex(index).text()
            row = self.noteListModel.parseText(text)
            if row is None:
                continue
            row = self.noteModel.selectById(row['id'])
            self.textEdit.setText(row['content'])
            self.titleEdit.setText(text)
            self.smsg('selected note by id "%d"' % (row['id'], ))


class NoteBookController:
    def __init__(self):
        self.noteBookModel = NoteBookModel()
        self.noteBook = NoteBookView(self.noteBookModel)
        self.noteBook.newButton.clicked.connect(self.noteBook.new)
        self.noteBook.deleteButton.clicked.connect(self.noteBook.delete)
        self.noteBook.saveButton.clicked.connect(self.noteBook.save)
        self.noteBook.noteList.setModel(self.noteBook.noteListModel)
        self.noteBook.noteList.selectionModel().selectionChanged.connect(self.noteBook.changed)

    def run(self):
        self.noteBook.show()


def main():
    qapp = QApplication([])
    ctrl = NoteBookController()
    ctrl.run()
    qapp.exec()


if __name__ == '__main__':
    main()
