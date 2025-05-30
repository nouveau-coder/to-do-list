import mysql.connector as ms

class Database:
    def __init__(self):
        self.con = ms.connect(host='localhost', username='root', password='1234')
        self.cur = self.con.cursor()
    
    def create_tables(self):
        self.cur.execute('CREATE DATABASE IF NOT EXISTS todolist')
        self.cur.execute('USE todolist')
        self.cur.execute('CREATE TABLE IF NOT EXISTS users(userid INT, name VARCHAR(100), password VARCHAR(100))')
        self.cur.execute('CREATE TABLE IF NOT EXISTS tasks(userid INT, task VARCHAR(100))')   
        self.con.commit()

    def close_connection(self):
        self.cur.close()
        self.con.close()

    def add_user(self, userid, name, password):
        self.cur.execute('INSERT INTO users (userid, name, password) VALUES (%s, %s, %s)', (userid, name, password))
        self.con.commit()
    
    def add_task(self, userid, task):
        self.cur.execute('INSERT INTO tasks (userid, task) VALUES (%s, %s)', (userid, task))
        self.con.commit()
    
    def get_tasks(self, userid):
        self.cur.execute('SELECT task FROM tasks WHERE userid = %s', (userid,))
        return self.cur.fetchall()
    
    def get_user(self, userid):
        self.cur.execute('SELECT userid FROM users WHERE userid = %s', (userid,))
        return self.cur.fetchone()
    
    def remove_task(self, userid, task):
        self.cur.execute('DELETE FROM tasks WHERE userid = %s AND task = %s', (userid, task))
        self.con.commit()
    


