class PageModel:
    def __init__(self, dbConn):
        self.dbConn = dbConn

    def create(self, note_id):
        cursor = self.dbConn.cursor()

        # sqlite3's CURRENT_TIMESTAMP create UTC value
        cursor.execute('''
            INSERT INTO page (note_id) VALUES (?);
        ''', (note_id, ))
        self.dbConn.commit()

        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content,
                note_id
            FROM page WHERE id = ?
        ''', (cursor.lastrowid, ))

        return cursor.fetchone()

    def deleteById(self, rid):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content,
                note_id
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
                content,
                note_id
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

    def selectAllByNoteId(self, note_id):
        cursor = self.dbConn.cursor()
        cursor.execute('''
            SELECT
                id,
                DATETIME(created, '+9 hours') AS created,
                content,
                note_id
            FROM page
            WHERE note_id = ?;
        ''', (note_id, ))
        return cursor.fetchall()
