from models.page import PageModel
from models.page_list import PageListModel
from models.note import NoteModel
from views.page import PageView


class PageController:
    def __init__(self, dbConn):
        self.dbConn = dbConn
        
        # models
        self.pageModel = PageModel(self.dbConn)
        self.pageListModel = PageListModel()
        self.noteModel = NoteModel(self.dbConn)

        # PageView
        self.pageView = PageView()
        self.pageView.pageModel = self.pageModel
        self.pageView.pageListModel = self.pageListModel
        self.pageView.noteModel = self.noteModel

        # buttons
        self.pageView.newButton.clicked.connect(self.pageView.new)
        self.pageView.deleteButton.clicked.connect(self.pageView.delete)
        self.pageView.saveButton.clicked.connect(self.pageView.save)

        # page list
        self.pageView.pageList.setModel(self.pageListModel)
        self.pageView.pageList.selectionModel().selectionChanged.connect(self.pageView.changed)

        # menu bar
        self.pageView.actionNewPage.triggered.connect(self.pageView.new)
        self.pageView.actionSavePage.triggered.connect(self.pageView.save)
        self.pageView.actionDeletePage.triggered.connect(self.pageView.delete)
        self.pageView.actionCloseNote.triggered.connect(self.pageView.quit)

    def show(self):
        self.pageView.show()

    def open(self, note_id):
        self.pageView.note_id = note_id
        self.pageView.load()
        self.pageView.show()