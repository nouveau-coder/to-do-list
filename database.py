import mysql.connector as mysql
import os
from dotenv import load_dotenv
from datetime import date
import logging 
logger = logging.getLogger(__name__) 

class Database:
    def __init__(self):
        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')

        self.con = None
        self.cursor = None

        try:
            self.con = mysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
            )
            self.cursor = self.con.cursor(dictionary=True)
            logger.info("Database connection established successfully.") # Replaced print
        except mysql.Error as err:
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
                self.con = mysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
                self.cursor = self.con.cursor(dictionary=True)
                logger.info("Database re-connection established.") # Replaced print
            except mysql.Error as err:
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
        tables = {}
        tables['users'] = (
            "CREATE TABLE IF NOT EXISTS users ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "name VARCHAR(255) NOT NULL UNIQUE,"
            "password VARCHAR(255) NOT NULL"
            ") ENGINE=InnoDB"
        )
        tables['tasks'] = (
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "user_id INT NOT NULL,"
            "task VARCHAR(255) NOT NULL,"
            "task_status ENUM('pending', 'completed') DEFAULT 'pending'," # Added status
            "due_date DATE,"
            "priority INT,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
            ") ENGINE=InnoDB"
        )

        for name, ddl in tables.items():
            try:
                logger.info(f"Creating table {name}: {ddl}")
                self.cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                    logger.warning(f"Table {name} already exists, skipping creation.")
                else:
                    logger.error(f"Error creating table {name}: {err}", exc_info=True)
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
    
    def get_tasks(self, user_id: int) -> list[tuple]:
        """
        Retrieves all tasks for a specific user from the database.
        Returns a list of tuples, where each tuple is a task row.
        """
        try:
            self.cursor.execute(
                "SELECT id, task, task_status, due_date, priority FROM tasks WHERE user_id = %s ORDER BY id ASC",
                (user_id,) # <--- CRITICAL: Filter by user_id
            )
            tasks = self.cursor.fetchall()
            if tasks:
                logger.info(f"Database: Retrieved {len(tasks)} tasks for user_id: {user_id}.")
            else:
                logger.info(f"Database: No tasks found for user_id: {user_id}.")
            return tasks
        except mysql.connector.Error as err:
            logger.error(f"Database: Error retrieving tasks for user_id {user_id}: {err}", exc_info=True)
            raise # Re-raise the database error for the calling layer (commands.py) to handle
    
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
    
    def update_task(self, user_id: int, task_id: int, task_name: str = None, due_date: date = None, priority: int = None, task_status: str = None) -> bool:
        updates = []
        values = []

        if task_name is not None:
            updates.append("task = %s")
            values.append(task_name)
        if due_date is not None:
            updates.append("due_date = %s")
            values.append(due_date)
        if priority is not None:
            updates.append("priority = %s")
            values.append(priority)
        if task_status is not None: # New: Handle task_status
            updates.append("task_status = %s")
            values.append(task_status)

        if not updates:
            logger.info(f"DB: No fields to update for task ID {task_id} (user_id: {user_id}).")
            return False # Nothing to update

        sql_query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
        values.extend([task_id, user_id])

        try:
            self.cursor.execute(sql_query, tuple(values))
            return self.cursor.rowcount > 0 # Returns True if a row was updated
        except mysql.connector.Error as e:
            logger.error(f"DB: Error updating task {task_id} for user {user_id}: {e}", exc_info=True)
            return False

    def get_tasks(self, user_id: int) -> list[dict]:
        """Retrieves all tasks for a specific user."""
        try:
            self.cursor.execute(
                "SELECT id, task, task_status, due_date, priority FROM tasks WHERE user_id = %s",
                (user_id,)
            )
            return self.cursor.fetchall() # Returns list of dictionaries
        except mysql.connector.Error as e:
            logger.error(f"DB: Error retrieving tasks for user {user_id}: {e}", exc_info=True)
            return [] # Return empty list on error
