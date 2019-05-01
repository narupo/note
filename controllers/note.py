from PyQt5.QtWidgets import (
    QMessageBox,
    qApp,
)
from views.note import NoteView
from models.note import NoteModel
from models.note_table import NoteTableModel


class NoteController:
    def __init__(self, dbConn):
        self.dbConn = dbConn
        self.pageCtrl = None

        self.noteView = NoteView()
        self.noteModel = NoteModel(self.dbConn)
        self.noteTableModel = NoteTableModel(self.dbConn)
        self.noteTableModel.load()

        self.noteView.noteModel = self.noteModel
        self.noteView.noteTableModel = self.noteTableModel
        self.noteView.noteTable.setModel(self.noteTableModel)
        self.noteView.noteTable.selectionModel().currentChanged.connect(self.noteView.changed)

        self.noteView.newButton.clicked.connect(self.noteView.new)
        self.noteView.deleteButton.clicked.connect(self.noteView.delete)
        self.noteView.openButton.clicked.connect(self.noteView.open)
        self.noteView.onOpenNote = self.openNote

        self.noteView.actionNewNote.triggered.connect(self.noteView.new)
        self.noteView.actionDeleteNote.triggered.connect(self.noteView.delete)
        self.noteView.actionOpenNote.triggered.connect(self.noteView.open)
        self.noteView.actionCloseWindow.triggered.connect(self.quit)

    def show(self):
        self.noteView.show()

    def openNote(self, note_id):
        self.pageCtrl.open(note_id)

    def quit(self):
        reply = QMessageBox.question(self, '終了確認', 'ノートを終了しますか？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        qApp.quit()
