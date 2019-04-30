from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    qApp,
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


class PageListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def parseText(self, text):
        cols = text.split(',')
        if len(cols) != 2:
            return None
        return { 'id': int(cols[0]), 'created': cols[1] }

    def parseRow(self, dict_row):
        return '{id}, {created}'.format(id=dict_row['id'], created=dict_row['created'])


class PageModel:
    def __init__(self, dbConn):
        self.dbConn = dbConn

    def create(self):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            INSERT INTO page DEFAULT VALUES;
        ''')
        self.dbConn.commit()

        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content
            FROM page WHERE id = ?
        ''', (cursor.lastrowid, ))
        row = cursor.fetchone()
        return row

    def deleteById(self, rid):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content
            FROM page WHERE id = ?
        ''', (rid, ))
        row = cursor.fetchone()

        cursor.execute('''
            DELETE FROM page WHERE id = ?
        ''', (rid, ))
        self.dbConn.commit()

        return row
    
    def selectById(self, rid):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content
            FROM page WHERE id = ?
        ''', (rid, ))
        row = cursor.fetchone()
        return row

    def update(self, id, content):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            UPDATE page SET content = ? WHERE id = ?;
        ''', (content, id, ))
        self.dbConn.commit()

    def selectAll(self):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content
            FROM page;
        ''')
        return cursor.fetchall()


class NoteView(QMainWindow):
    def __init__(self, dbConn, debug=False):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.debug = debug
        self.pageModel = PageModel(dbConn)
        self.pageListModel = PageListModel()
        self.load()

    def smsg(self, msg):
        self.statusBar().showMessage(msg)

    def showDebug(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def load(self):
        rows = self.pageModel.selectAll()
        rows = sorted(rows, key=lambda row: -int(row['id']))
        nrows = len(rows)
        for row in rows:
            text = self.pageListModel.parseRow(row)
            item = QStandardItem(text)
            self.pageListModel.appendRow(item)

        self.pageListLabel.setText('ページ数: %d' % nrows)
        self.smsg('ロードが完了しました')

    def new(self):
        # 挿入
        row = self.pageModel.create()
        text = self.pageListModel.parseRow(row)
        item = QStandardItem(text)
        self.pageListModel.insertRow(0, item)

        # リストの最初のアイテムをフォーカス
        modelIndex = self.pageListModel.index(0, 0)
        self.pageList.setCurrentIndex(modelIndex)

        # エディタを更新
        self.textEdit.setText(row['content'])
        self.titleEdit.setText(text)
        self.showDebug('inserted', dict(row))
        self.smsg('新規ページを作成しました')

    def delete(self):
        selectionModel = self.pageList.selectionModel()
        indexes = selectionModel.selectedIndexes()
        if not len(indexes):
            QMessageBox.about(self, 'ページが選択されていません', '削除するページを選択して下さい。')
            return

        reply = QMessageBox.question(self, '削除確認', '本当にこのページを削除しますか？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        for index in indexes:
            text = self.pageListModel.itemFromIndex(index).text()
            row = self.pageListModel.parseText(text)
            if row is None:
                continue
            row = self.pageModel.deleteById(row['id'])
            self.showDebug('deleted', dict(row))
            self.smsg('ページを削除しました（id %d）' % (row['id'], ))

        for index in indexes:
            self.pageListModel.removeRow(index.row())

    def save(self):
        selectedTitle = self.titleEdit.text()
        row = self.pageListModel.parseText(selectedTitle)
        if row is None:
            return

        row['content'] = self.textEdit.toPlainText()
        self.pageModel.update(id=row['id'], content=row['content'])
        self.showDebug('updated', row)
        self.smsg('ページを更新しました（id %d）' % (row['id'], ))
        QMessageBox.about(self, '保存結果', 'ページの保存に成功しました。')

    def changed(self, selected, deselected):
        for index in selected.indexes():
            text = self.pageListModel.itemFromIndex(index).text()
            row = self.pageListModel.parseText(text)
            if row is None:
                continue
            row = self.pageModel.selectById(row['id'])
            if row is None:
                continue
            self.textEdit.setText(row['content'])
            self.titleEdit.setText(text)
            self.smsg('ページを選択しました（id %d）' % (row['id'], ))

    def quit(self):
        reply = QMessageBox.question(self, '終了確認', 'ノートを閉じますか？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        qApp.quit()


class NoteController:
    def __init__(self, remove_settings=False):
        self.remove_settings = remove_settings
        self.initEnv()
        self.initDB()
        self.bindModelAndView()

    def bindModelAndView(self):
        self.note = NoteView(self.dbConn)

        # buttons
        self.note.newButton.clicked.connect(self.note.new)
        self.note.deleteButton.clicked.connect(self.note.delete)
        self.note.saveButton.clicked.connect(self.note.save)

        # page list
        self.note.pageList.setModel(self.note.pageListModel)
        self.note.pageList.selectionModel().selectionChanged.connect(self.note.changed)

        # menu bar
        self.note.actionNewPage.triggered.connect(self.note.new)
        self.note.actionSavePage.triggered.connect(self.note.save)
        self.note.actionDeletePage.triggered.connect(self.note.delete)
        self.note.actionCloseNote.triggered.connect(self.note.quit)

    def run(self):
        self.note.show()

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
            CREATE TABLE IF NOT EXISTS page (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                content TEXT NOT NULL DEFAULT "内容なし"
            );
        ''')
        self.dbConn.commit()


def main():
    qapp = QApplication([])
    ctrl = NoteController()
    ctrl.run()
    qapp.exec()


if __name__ == '__main__':
    main()
