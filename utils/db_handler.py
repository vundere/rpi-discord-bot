import sqlite3


class ConnectionInstance:

    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def query(self, query, args=(), one=False):
        self.cur.execute(query, args)
        rv = self.cur.fetchall()
        return (rv[0] if rv else None) if one else rv

    def modify(self, query, args=()):
        self.cur.execute(query, args)
        self.conn.commit()
