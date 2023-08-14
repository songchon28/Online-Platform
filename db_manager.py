import sqlite3
from cryptography.fernet import Fernet
class CRUD:
    def __init__(self, db_name : str) -> None:
        self.db_name = db_name
        self.cursor, self.conn = self.get_cursor()
    def get_cursor(self):
        print('Establishing connection to the database...')
        conn = sqlite3.connect(self.db_name, timeout=6666666666666)
        cursor = conn.cursor()
        return cursor, conn
    def insert(self, query):
        print('Inserting data into a table...')
        self.cursor.execute(query)
        self.conn.commit()
    def read(self, query):
        print('Reading a data from table')
        executed_state = self.cursor.execute(query)
        result = executed_state.fetchall()
        return result
    def delete(self, query):
        print('Deleteing data into a table...')
        self.cursor.execute(query)
        self.conn.commit()
    def login_read(self, query, data):
        with open('key.pem', 'r') as key_file:
            key = key_file.readline()
        decrypt_cipher = Fernet(key)
        q_executor = self.cursor.execute(query)
        result = q_executor.fetchall() #[['password']] -> 
        if str(decrypt_cipher.decrypt(result[0])) == data:
            return True
        return False
    def close(self):
        self.conn.close()

if __name__ == '__main__':
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Course (course_name, course_price, course_video, course_descript) VALUES ('wdqqwd', 123, "test", "test")''')
    conn.commit()
    result = cursor.execute('SELECT * FROM User').fetchall()
    print(result)
    conn.close()    
