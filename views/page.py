from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    qApp,
)
from PyQt5.QtGui import (
    QStandardItem,
)
from PyQt5 import uic


class PageView(QMainWindow):
    def __init__(self, debug=False):
        super().__init__()
        uic.loadUi('ui/page.ui', self)
        self.debug = debug
        self.note_id = None
        self.pageModel = None
        self.pageListModel = None
        self.noteModel = None

    def smsg(self, msg):
        self.statusBar().showMessage(msg)

    def showDebug(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def load(self):
        if self.note_id is None:
            self.showDebug('can not load. note id is null')
            return

        # init list
        rows = self.pageModel.selectAllByNoteId(self.note_id)
        rows = sorted(rows, key=lambda row: -int(row['id']))
        nrows = len(rows)
        self.pageListModel.clear()
        for row in rows:
            text = self.pageListModel.parseRow(row)
            item = QStandardItem(text)
            self.pageListModel.appendRow(item)

        self.pageListLabel.setText('ページ数: %d' % nrows)

        # set note title
        note_row = self.noteModel.selectById(self.note_id)
        self.noteTitleLabel.setText(note_row['title'])

        # clear input 
        self.textEdit.setText('')
        self.titleEdit.setText('')

        # done
        self.smsg('ロードが完了しました')

    def new(self):
        if self.note_id is None:
            self.showDebug('can not new. note id is null')
            return

        # 挿入
        row = self.pageModel.create(self.note_id)
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


