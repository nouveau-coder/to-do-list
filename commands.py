from database import Database
import logging
import bcrypt
import mysql.connector as mysql
logger = logging.getLogger(__name__)

class ToDoListApp:
    def __init__(self):
        pass

    def setup_database(self):
        try:
            with Database() as db: 
                db.create_tables()
            logger.info("Database tables checked/created successfully.")
        except mysql.Error as e:
            logger.critical(f"FATAL: Database table creation failed: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"FATAL: Unexpected error during database setup: {e}", exc_info=True)
            raise    
    
    def add_user(self, username: str, password: str) -> str:
        if not username or not password:
            logger.warning("Attempted registration with empty username or password.")
            return "Error: Username and password cannot be empty."

        if len(password) < 8:
            logger.warning(f"Registration failed for '{username}': Password too short.")
            return "Error: Password must be at least 8 characters long."

        try:
            hashed_password_str = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            with self.db as conn:
                conn.cursor.execute(
                    "INSERT INTO users (name, password) VALUES (%s, %s)",
                    (username, hashed_password_str)
                )
                user_id = conn.cursor.lastrowid 
                logger.info(f"User '{username}' added successfully with ID: {user_id}.")
                return f"Success: User '{username}' registered. ID: {user_id}"

        except mysql.IntegrityError as e:
            logger.error(f"Registration failed for '{username}': User already exists. {e}", exc_info=True)
            return f"Error: Username '{username}' already exists."
        except mysql.Error as e:
            logger.error(f"Database error during registration for '{username}': {e}", exc_info=True)
            return "Error: A database problem occurred during registration."
        except Exception as e:
            logger.critical(f"An unexpected error occurred during registration for '{username}': {e}", exc_info=True)
            return "Error: An unexpected application error occurred during registration."
    
    def authenticate_user(self, username: str, password: str):
        try:
            with self.db as conn:
                conn.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                result = conn.cursor.fetchone()
                if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                    logger.info(f"User '{username}' authenticated successfully.")
                    return True
                else:
                    logger.warning(f"Authentication failed for user '{username}'.")
                    return False
        except Exception as e:
            logger.error(f"Error authenticating user '{username}': {e}", exc_info=True)
            return False

    def add_task(self, task_name: str, due_date: str, priority: int):
        try:
            with self.db as conn:
                conn.cursor.execute(
                    "INSERT INTO tasks (task_name, due_date, priority) VALUES (%s, %s, %s)",
                    (task_name, due_date, priority)
                )
                logger.info(f"Task '{task_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error adding task '{task_name}': {e}", exc_info=True)

    def delete_task(self, task_id: int):
        try:
            with self.db as conn:
                conn.cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                logger.info(f"Task with ID {task_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting task with ID {task_id}: {e}", exc_info=True)

    def update_task(self, task_id: int, task_name: str = None, due_date: str = None, priority: int = None):
        try:
            with self.db as conn:
                query = "UPDATE tasks SET "
                params = []
                if task_name is not None:
                    query += "task_name = %s,"
                    params.append(task_name)
                if due_date is not None:
                    query += "due_date = %s,"
                    params.append(due_date)
                if priority is not None:
                    query += "priority = %s,"
                    params.append(priority)
                
                query = query.rstrip(',') + " WHERE id = %s"
                params.append(task_id)

                conn.cursor.execute(query, tuple(params))
                logger.info(f"Task with ID {task_id} updated successfully.")
        except Exception as e:
            logger.error(f"Error updating task with ID {task_id}: {e}", exc_info=True)

    def get_tasks(self):
        try:
            with self.db as conn:
                conn.cursor.execute("SELECT * FROM tasks")
                tasks = conn.cursor.fetchall()
                logger.info("Tasks retrieved successfully.")
                return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks: {e}", exc_info=True)
            return []
