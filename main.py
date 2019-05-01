from PyQt5.QtWidgets import (
    QApplication,
)
from os.path import expanduser
from pathlib import Path
import os
import sqlite3
import shutil
import ui.resources
from controllers.page import PageController
from controllers.note import NoteController


class Application:
    def __init__(self, remove_settings=False):
        self.remove_settings = remove_settings
        self.initEnv()
        self.initDB()
        self.initCtrls()

    def initCtrls(self):
        self.pageCtrl = PageController(self.dbConn)
        self.noteCtrl = NoteController(self.dbConn)
        self.noteCtrl.pageCtrl = self.pageCtrl

    def run(self):
        self.noteCtrl.show()

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
            PRAGMA foreign_keys = ON;
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(255) NOT NULL DEFAULT ""
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                content TEXT NOT NULL DEFAULT "内容なし",
                note_id INTEGER NOT NULL,
                FOREIGN KEY (note_id) REFERENCES note(id)
            );
        ''')
        self.dbConn.commit()


def main():
    qapp = QApplication([])
    app = Application(remove_settings=False)
    app.run()
    qapp.exec()


if __name__ == '__main__':
    main()
