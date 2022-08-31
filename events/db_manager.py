import sqlite3

db_path = 'events.sqlite'


class dbSelect():

    def __init__(self):
        db = db_path
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def Select(self, command):
        select = self.c.execute(command).fetchall()
        return select

    def Close(self):
        self.conn.commit()
        self.conn.close()


class dbManager(dbSelect):
    def __init__(self):
        super().__init__()

    def Execute(self, command):
        self.c.execute(command)
        return self.c

    def InsertOne(self, table, record):
        '''record in format: n fields (val1, val2); 1 field "('val')" OR '(val int)'''
        self.c.execute(f"INSERT INTO {table} VALUES {record}")
        return self.c

    def InsertMany(self, table, no_of_records, records):
        self.c.executemany(f"INSERT INTO {table} VALUES ({'?, ' * no_of_records}?)", records)
        return self.c

    def DeleteLast(self, table):
        self.c.execute(f"DELETE FROM {table} WHERE rowid = (SELECT max(rowid) FROM {table})")
        return self.c

    def DeleteRecord(self, table, field, value):
        self.c.execute(f"DELETE FROM {table} WHERE {field} = {value}")
        return self.c

    def __del__(self):
        self.conn.commit()
        self.conn.close()


''' creating table '''
# dbManager().Execute("CREATE TABLE settings (setting TEXT, value TEXT)")
''' deleting table '''
# dbManager().Execute("DROP TABLE test3")
''' inserting one record '''
# record = "('4')"  # n fields (val1, val2); 1 field "('val')" OR '(val int)'
# dbManager().InsertOne('settings', record)
''' inserting many records '''
# records = [('before meal',), ('doing sth',), ('next in row',)]
# n fields [(val1, VAL1), (val2, VAL2)]; 1 field [{val1, }, {val2, )]
# dbManager().InsertMany('reasons', len(records[0]) - 1, records)
''' deleting last record '''
# dbManager().DeleteLast('settings')
''' select fetchall '''
# select = dbSelect().Select(f"SELECT reason FROM reasons")
# print(select)
''' any command '''
var = 'after meal'
# dbManager().Execute(f"DELETE from events")
''' any command without dbManager '''
# conn = sqlite3.connect(db_path)
# c = conn.cursor()
#
# c.execute("DELETE FROM test WHERE rowid = (SELECT max(rowid) FROM test)")
# print(c.fetchall())
#
# conn.commit()
# conn.close()
