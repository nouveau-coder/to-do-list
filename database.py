import mysql.connector as ms
from mysql.connector import Error # Import the Error class

class Database:
    def __init__(self):
        self.con = None # Initialize connection to None
        self.cur = None # Initialize cursor to None
        try:
            self.con = ms.connect(host='localhost',
                                  username='root',
                                  password='1234')
            if self.con.is_connected():
                self.cur = self.con.cursor()
                print("Connected to MySQL database successfully!")
            else:
                print("Failed to connect to MySQL database.")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_tables(self):
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot create tables.")
            return

        try:
            self.cur.execute('CREATE DATABASE IF NOT EXISTS todolist')
            self.cur.execute('USE todolist')
            # Add PRIMARY KEY and AUTO_INCREMENT for userid in users table
            # Make password NOT NULL
            self.cur.execute('CREATE TABLE IF NOT EXISTS users('
                             'userid INT AUTO_INCREMENT PRIMARY KEY, '
                             'name VARCHAR(100) NOT NULL, '
                             'password VARCHAR(100) NOT NULL)')
            # Add FOREIGN KEY constraint for tasks to users table
            self.cur.execute('CREATE TABLE IF NOT EXISTS tasks('
                             'taskid INT AUTO_INCREMENT PRIMARY KEY, ' # Add a primary key for tasks
                             'userid INT NOT NULL, '
                             'task VARCHAR(255) NOT NULL, ' # Increase task length
                             'status VARCHAR(20) DEFAULT "pending", ' # Add a status field
                             'FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE)') # ON DELETE CASCADE: if user is deleted, their tasks are also deleted
            self.con.commit()
            print("Tables created/verified successfully.")
        except Error as e:
            print(f"Error creating tables: {e}")
            self.con.rollback() # Rollback in case of error

    def close_connection(self):
        if self.cur:
            self.cur.close()
        if self.con and self.con.is_connected():
            self.con.close()
            print("MySQL connection closed.")

    def add_user(self, name, password): # userid should be auto-incremented
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot add user.")
            return None # Indicate failure

        try:
            # Use parameterized query
            self.cur.execute('INSERT INTO users (name, password) VALUES (%s, %s)', (name, password))
            self.con.commit()
            print(f"User '{name}' added successfully.")
            return self.cur.lastrowid # Return the newly generated userid
        except Error as e:
            print(f"Error adding user: {e}")
            self.con.rollback()
            return None

    def add_task(self, userid, task):
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot add task.")
            return

        try:
            self.cur.execute('INSERT INTO tasks (userid, task) VALUES (%s, %s)', (userid, task))
            self.con.commit()
            print(f"Task '{task}' added for user {userid}.")
        except Error as e:
            print(f"Error adding task: {e}")
            self.con.rollback()

    def get_tasks(self, userid):
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot get tasks.")
            return []

        try:
            # Select both task and status
            self.cur.execute('SELECT task, status FROM tasks WHERE userid = %s', (userid,))
            return self.cur.fetchall()
        except Error as e:
            print(f"Error retrieving tasks: {e}")
            return []

    def get_user_by_id(self, userid): # Renamed for clarity
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot get user.")
            return None
        try:
            self.cur.execute('SELECT userid, name, password FROM users WHERE userid = %s', (userid,))
            return self.cur.fetchone()
        except Error as e:
            print(f"Error retrieving user by ID: {e}")
            return None

    def get_user_by_name_and_password(self, name, password): # New method for login
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot get user.")
            return None
        try:
            self.cur.execute('SELECT userid, name FROM users WHERE name = %s AND password = %s', (name, password))
            return self.cur.fetchone() # Returns (userid, name) or None
        except Error as e:
            print(f"Error retrieving user by name and password: {e}")
            return None

    def remove_task(self, userid, task):
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot remove task.")
            return

        try:
            self.cur.execute('DELETE FROM tasks WHERE userid = %s AND task = %s', (userid, task))
            self.con.commit()
            if self.cur.rowcount > 0:
                print(f"Task '{task}' removed for user {userid}.")
            else:
                print(f"Task '{task}' not found for user {userid}.")
        except Error as e:
            print(f"Error removing task: {e}")
            self.con.rollback()

    def update_task_status(self, userid, task, status):
        if not self.con or not self.con.is_connected():
            print("Database connection not established. Cannot update task status.")
            return

        try:
            self.cur.execute('UPDATE tasks SET status = %s WHERE userid = %s AND task = %s', (status, userid, task))
            self.con.commit()
            if self.cur.rowcount > 0:
                print(f"Status of task '{task}' updated to '{status}' for user {userid}.")
            else:
                print(f"Task '{task}' not found for user {userid}.")
        except Error as e:
            print(f"Error updating task status: {e}")
            self.con.rollback()