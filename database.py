import mysql.connector as mysql

class Database:
    def __init__(self):
        self.con = mysql.connect(host='localhost',user = 'root', password = '1234', database = 'todo_list')
        self.cursor = self.con.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                task varchar(100) NOT NULL,
                task_status varchar(15) DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.con.commit()
    
    def add_user(self, name: str, password: str):
        self.cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, password))
        self.con.commit()
        return self.cursor.lastrowid
    
    def get_user(self, name: str):
        self.cursor.execute("SELECT id, password FROM users WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        if result:
            return {'id': result[0], 'password': result[1]}
        return None
    
    def add_task(self, user_id: int, task: str):
        self.cursor.execute("INSERT INTO tasks (user_id, task) VALUES (%s, %s)", (user_id, task))
        self.con.commit()
        return self.cursor.lastrowid
    
    def get_tasks(self, user_id: int):
        self.cursor.execute("SELECT task, completed FROM tasks WHERE user_id = %s", (user_id,))
        return self.cursor.fetchall()
    
    def delete_task(self, user_id: int, task: str):
        self.cursor.execute("DELETE FROM tasks WHERE user_id = %s AND task = %s", (user_id, task))
        self.con.commit()
        return self.cursor.rowcount > 0
    
    def close_connection(self):
        if self.con.is_connected():
            self.cursor.close()
            self.con.close()
            print("Database connection closed.")
        else:
            print("No active database connection to close.")
    
    def __del__(self):
        self.close_connection()
