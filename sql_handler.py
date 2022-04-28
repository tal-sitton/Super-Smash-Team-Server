import sqlite3

db_path = r"SQL\database.db"
table = "players"


class SQLHandler:
    def __init__(self):
        self.db = create_connection(db_path)
        if not self.db:
            print("SOMETHINGS WRONG!!!")
        else:
            self.cursor = self.db.cursor()
            self.table = table

    def get_data(self, col="*", filter_tuple=(None, None)):
        if filter_tuple == (None, None):
            self.cursor.execute(f"SELECT {col} FROM {self.table}")
            result = self.cursor.fetchall()
            return result
        else:
            sql = f"SELECT {col} FROM {self.table} WHERE {filter_tuple[0]} ='{filter_tuple[1]}'"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result

    def update(self, cursor, col, new_value, filter_column, filter_value):
        sql = f"UPDATE {self.table} SET {col} = ? WHERE {filter_column} = ?"
        val = (new_value, filter_value)
        cursor.execute(sql, val)
        self.db.commit()

    def update_inc(self, col, filter_column, filter_value):
        sql = f"UPDATE {self.table} SET {col} = {col}+1 WHERE {filter_column} ={filter_value}"
        self.cursor.execute(sql)
        self.db.commit()

    def insert(self, username, password, win, lose):
        sql = f"INSERT INTO {self.table}(username,password,win,lose) VALUES(?,?,?,?)"
        val = (username, password, win, lose)
        self.cursor.execute(sql, val)
        self.db.commit()

        self.cursor.execute(f"select * from {self.table}")
        rowcount = len(self.cursor.fetchall())
        print(rowcount, "record inserted.")

        return rowcount

    def create_table(self, name):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} (username text, "
                            "password BINARY(32),win INT(255),lose INT(255))")


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("version:", sqlite3.version)
    except Exception as e:
        print(e)
    return conn
