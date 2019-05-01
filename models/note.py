class NoteModel:
    def __init__(self, dbConn):
        self.dbConn = dbConn

    def selectAll(self):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                title
            FROM note;
        ''')
        return cursor.fetchall()

    def selectById(self, id):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                title
            FROM note
            WHERE id = ?
        ''', (id, ))
        return cursor.fetchone()

    def create(self):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            INSERT INTO note DEFAULT VALUES;
        ''')
        self.dbConn.commit()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                title
            FROM note WHERE id = ?;
        ''', (cursor.lastrowid, ))
        return cursor.fetchone()

    def deleteById(self, id):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            DELETE FROM note WHERE id = ?;
        ''', (id, ))
        self.dbConn.commit()

    def update(self, id, title):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            UPDATE note SET title = ? WHERE id = ?;
        ''', (title, id))
        self.dbConn.commit()

