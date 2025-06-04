import mysql.connector as mysql
import os
from dotenv import load_dotenv
import logging 
logger = logging.getLogger(__name__) # __name__ will be 'database' here

class Database:
    def __init__(self):
        load_dotenv()
        db_host = os.getenv('DB_HOST', 'localhost')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '1234')
        db_name = os.getenv('DB_NAME', 'todo_list')

        self.con = None
        self.cursor = None

        try:
            self.con = mysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                dictionary=True
            )
            self.cursor = self.con.cursor()
            logger.info("Database connection established successfully.") # Replaced print
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to database: {err}", exc_info=True) # Replaced print, added exc_info
            self.con = None
            self.cursor = None
            raise 

    def __enter__(self):
        if self.con is None or not self.con.is_connected():
            logger.warning("Connection not active upon entering context. Attempting to reconnect.") # Replaced print
            try:
                db_host = os.getenv('DB_HOST', 'localhost')
                db_user = os.getenv('DB_USER', 'root')
                db_password = os.getenv('DB_PASSWORD', '1234')
                db_name = os.getenv('DB_NAME', 'todo_list')
                self.con = mysql.connect(host=db_host, user=db_user, password=db_password, database=db_name, dictionary=True)
                self.cursor = self.con.cursor()
                logger.info("Database re-connection established.") # Replaced print
            except mysql.connector.Error as err:
                logger.error(f"Error during re-connection in __enter__: {err}", exc_info=True) # Replaced print, added exc_info
                raise

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.con and self.con.is_connected():
            try:
                if exc_type:
                    self.con.rollback()
                    logger.warning(f"Database transaction rolled back due to error: {exc_val}") # Replaced print
                else:
                    self.con.commit()
                    logger.info("Database transaction committed successfully.") # Replaced print
            except mysql.Error as err:
                logger.error(f"Error during commit/rollback: {err}", exc_info=True) # Replaced print, added exc_info
            finally:
                try:
                    if self.cursor:
                        self.cursor.close()
                    if self.con:
                        self.con.close()
                    logger.info("Database connection and cursor closed.") # Replaced print
                except mysql.Error as err:
                    logger.error(f"Error during connection closure: {err}", exc_info=True) # Replaced print, added exc_info
        else:
            logger.info("No active database connection to close upon exiting context.") # Replaced print

        return False

    def create_tables(self):
        try:
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
                task VARCHAR(100) NOT NULL,
                task_status VARCHAR(15) DEFAULT 'pending',
                due_date DATE,       -- Add this line
                priority INT,        -- Add this line
                FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            logger.info("Tables checked/created successfully.") 
        except mysql.Error as err:
            logger.error(f"Error creating tables: {err}", exc_info=True) 
            raise
    
    def add_user(self, name: str, password_hash: str): 
        try:
            self.cursor.execute(
                "INSERT INTO users (name, password) VALUES (%s, %s)",
                (name, password_hash) 
            )
            user_id = self.cursor.lastrowid
            logger.info(f"User '{name}' added successfully with ID: {user_id}.")
            return user_id
        except mysql.IntegrityError as err:
            logger.error(f"Error adding user '{name}': Duplicate name. {err}", exc_info=True)
            raise ValueError(f"Username '{name}' already exists.")
        except mysql.Error as err:
            logger.error(f"Error adding user '{name}': {err}", exc_info=True)
            raise
    
    def get_user(self, name: str):
        try:
            self.cursor.execute("SELECT id, password FROM users WHERE name = %s", (name,))
            result = self.cursor.fetchone() # This will be a dictionary if dictionary=True is set

            if result:
                logger.info(f"User '{name}' found.")
                return result # Directly return the dictionary (e.g., {'id': 1, 'password': 'hashed_value'})
            else:
                logger.info(f"User '{name}' not found.")
                return None
        except mysql.connector.Error as err:
            logger.error(f"Error retrieving user '{name}': {err}", exc_info=True)
            raise
    
    def add_task(self, user_id: int, task: str):
        if not task or not task.strip():
            logger.warning(f"Attempted to add an empty task for user_id: {user_id}")
            raise ValueError("Task description cannot be empty.")

        try:
            self.cursor.execute("INSERT INTO tasks (user_id, task) VALUES (%s, %s)", (user_id, task))

            task_id = self.cursor.lastrowid
            logger.info(f"Task '{task}' added successfully for user_id {user_id} with ID: {task_id}.")
            return task_id
        except mysql.IntegrityError as err:
            logger.error(f"Error adding task for user_id {user_id}: User ID does not exist or invalid data. {err}", exc_info=True)
            raise ValueError(f"User with ID {user_id} does not exist or task data is invalid.")
        except mysql.Error as err:
            logger.error(f"Error adding task for user_id {user_id} and task '{task}': {err}", exc_info=True)
            raise
    
    def get_tasks(self, user_id: int):
        try:
            self.cursor.execute(
                "SELECT id, task, task_status FROM tasks WHERE user_id = %s ORDER BY id ASC",
                (user_id,)
            )
            tasks = self.cursor.fetchall()

            if tasks:
                logger.info(f"Retrieved {len(tasks)} tasks for user_id: {user_id}.")
            else:
                logger.info(f"No tasks found for user_id: {user_id}.")
            return tasks
        except mysql.Error as err:
            logger.error(f"Error retrieving tasks for user_id {user_id}: {err}", exc_info=True)
            raise
    
    def delete_task(self, user_id: int, task_id: int) -> bool:
        try:
            self.cursor.execute(
                "DELETE FROM tasks WHERE user_id = %s AND id = %s", # CRITICAL: Include user_id
                (user_id, task_id)
            )
            if self.cursor.rowcount > 0:
                logger.info(f"Database: Task ID {task_id} deleted successfully for user_id {user_id}.")
                return True
            else:
                logger.info(f"Database: Task ID {task_id} not found or not deleted for user_id {user_id}.")
                return False
        except mysql.Error as err:
            logger.error(f"Database: Error deleting task ID {task_id} for user_id {user_id}: {err}", exc_info=True)
            raise
    
    def update_task(self, user_id: int, task_id: int, task_name: str = None, due_date: date = None, priority: int = None) -> bool:
        updates = []
        params = []

        if task_name is not None:
            updates.append("task = %s") # Use 'task' column name
            params.append(task_name)
        if due_date is not None:
            updates.append("due_date = %s")
            params.append(due_date)
        if priority is not None:
            updates.append("priority = %s")
            params.append(priority)

        if not updates:
            logger.info(f"No update parameters provided for task ID {task_id} (user_id: {user_id}).")
            return False

        query = "UPDATE tasks SET " + ", ".join(updates) + " WHERE user_id = %s AND id = %s"
        params.extend([user_id, task_id]) # Add user_id and task_id to the parameters

        try:
            self.cursor.execute(query, tuple(params))

            if self.cursor.rowcount > 0:
                logger.info(f"Database: Task ID {task_id} updated successfully for user_id {user_id}.")
                return True
            else:
                logger.info(f"Database: Task ID {task_id} not found or no changes applied for user_id {user_id}.")
                return False
        except mysql.Error as err:
            logger.error(f"Database: Error updating task ID {task_id} for user_id {user_id}: {err}", exc_info=True)
            raise
