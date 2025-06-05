from database import Database
from datetime import datetime
import logging
import bcrypt
import mysql.connector as mysql
logger = logging.getLogger(__name__)

class ToDoListApp:
    def __init__(self, db_instance: Database):
        self.db = db_instance

    def setup_database(self):
        try:
            with self.db as conn:
                conn.create_tables()
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
    
    def authenticate_user(self, username: str, password: str) -> tuple[int | None, str]:
        if not username or not password:
            logger.warning("Authentication attempt with empty username or password.")
            return None, "Error: Username and password cannot be empty."

        try:
            with self.db as conn:
                conn.cursor.execute("SELECT id, password FROM users WHERE name = %s", (username,))
                result = conn.cursor.fetchone()

                if result:
                    user_id = result[0]
                    stored_hashed_password = result[1]

                    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                        logger.info(f"User '{username}' (ID: {user_id}) authenticated successfully.")
                        return user_id, "Success: Authentication successful."
                    else:
                        logger.warning(f"Authentication failed for user '{username}': Invalid password.")
                        return None, "Error: Invalid username or password."
                else:
                    logger.warning(f"Authentication failed: User '{username}' not found.")
                    return None, "Error: Invalid username or password."

        except mysql.Error as e: 
            logger.error(f"Database error during authentication for user '{username}': {e}", exc_info=True)
            return None, "Error: A database problem occurred during authentication."
        except Exception as e: 
            logger.critical(f"An unexpected application error occurred during authentication for user '{username}': {e}", exc_info=True)
            return None, "Error: An unexpected application error occurred during authentication."

    def add_task(self, user_id: int, task_name: str, due_date: str = None, priority: int = None) -> str:
        if not task_name or not task_name.strip():
            logger.warning(f"Attempted to add an empty task for user_id: {user_id}")
            return "Error: Task description cannot be empty."

        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Invalid due_date format '{due_date}' for task '{task_name}' (user_id: {user_id}).")
                return "Error: Due date must be in YYYY-MM-DD format."

        if priority is not None:
            if not isinstance(priority, int) or not (0 <= priority <= 10): # Example range
                logger.warning(f"Invalid priority value {priority} for task '{task_name}' (user_id: {user_id}).")
                return "Error: Priority must be an integer between 0 and 10."

        try:
            with self.db as conn:
                conn.cursor.execute(
                    "INSERT INTO tasks (user_id, task, due_date, priority) VALUES (%s, %s, %s, %s)",
                    (user_id, task_name, parsed_due_date, priority) # Pass parsed date object
                )
                task_id = conn.cursor.lastrowid
                logger.info(f"Task '{task_name}' (ID: {task_id}) added for user_id: {user_id}.")
                return f"Success: Task '{task_name}' added with ID: {task_id}."

        except mysql.IntegrityError as e: 
            logger.error(f"Error adding task for user_id {user_id}: Foreign key constraint failed. {e}", exc_info=True)
            return "Error: The specified user does not exist or there was a data integrity issue."
        except mysql.Error as e:
            logger.error(f"Database error adding task for user_id {user_id} and task '{task_name}': {e}", exc_info=True)
            return "Error: A database problem occurred while adding the task."
        except Exception as e:
            logger.critical(f"An unexpected application error occurred while adding task for user_id {user_id}: {e}", exc_info=True)
            return "Error: An unexpected application error occurred while adding the task."

    def delete_task(self, user_id: int, task_id: int) -> str:
        if not isinstance(user_id, int) or user_id <= 0:
            logger.warning(f"Invalid user_id {user_id} provided for task deletion.")
            return "Error: Invalid user ID provided."
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"Invalid task_id {task_id} provided for deletion (user_id: {user_id}).")
            return "Error: Invalid task ID provided."

        try:
            with self.db as conn:
                deleted = conn.delete_task(user_id, task_id)

                if deleted:
                    logger.info(f"App: Task ID {task_id} deleted successfully for user_id {user_id}.")
                    return f"Success: Task ID {task_id} deleted."
                else:
                    logger.info(f"App: Task ID {task_id} not found or not owned by user_id {user_id}.")
                    return f"Info: Task ID {task_id} not found or you do not have permission to delete it."

        except mysql.Error as e:
            logger.error(f"App: Database error deleting task ID {task_id} for user_id {user_id}: {e}", exc_info=True)
            return "Error: A database problem occurred while deleting the task."
        except Exception as e:
            logger.critical(f"App: An unexpected application error occurred while deleting task ID {task_id} for user_id {user_id}: {e}", exc_info=True)
            return "Error: An unexpected application error occurred while deleting the task."

    def update_task(self, user_id: int, task_id: int, task_name: str = None, due_date: str = None, priority: int = None) -> str:
        if not isinstance(user_id, int) or user_id <= 0:
            logger.warning(f"Invalid user_id {user_id} provided for task update.")
            return "Error: Invalid user ID provided."
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"Invalid task_id {task_id} provided for update (user_id: {user_id}).")
            return "Error: Invalid task ID provided."

        validated_task_name = task_name if task_name is not None and task_name.strip() else None

        parsed_due_date = None
        if due_date is not None:
            try:
                parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Invalid due_date format '{due_date}' for task ID {task_id} (user_id: {user_id}).")
                return "Error: Due date must be in YYYY-MM-DD format."

        validated_priority = priority
        if priority is not None:
            if not isinstance(priority, int) or not (0 <= priority <= 10): # Example range
                logger.warning(f"Invalid priority value {priority} for task ID {task_id} (user_id: {user_id}).")
                return "Error: Priority must be an integer between 0 and 10."

        try:
            with self.db as conn:
                updated = conn.update_task(
                    user_id=user_id,
                    task_id=task_id,
                    task_name=validated_task_name,
                    due_date=parsed_due_date,
                    priority=validated_priority
                )

                if updated:
                    logger.info(f"App: Task ID {task_id} status updated for user ID: {user_id}.")
                    return f"Success: Task ID {task_id} updated."
                else:
                    logger.info(f"App: Task ID {task_id} not found or no changes applied for user ID: {user_id}.")
                    return f"Info: Task ID {task_id} not found or no changes were needed."

        except mysql.Error as e:
            logger.error(f"App: Database error updating task ID {task_id} for user ID {user_id}: {e}", exc_info=True)
            return "Error: A database problem occurred while updating the task."
        except Exception as e:
            logger.critical(f"App: An unexpected application error occurred while updating task ID {task_id} for user ID {user_id}: {e}", exc_info=True)
            return "Error: An unexpected application error occurred while updating the task."

    def get_user_tasks(self, user_id: int) -> str:
        if not isinstance(user_id, int) or user_id <= 0:
            logger.warning(f"Invalid user_id {user_id} provided for task retrieval.")
            return "Error: Invalid user ID provided."

        try:
            with self.db as conn: 
                raw_tasks = conn.get_tasks(user_id)

                if not raw_tasks:
                    logger.info(f"App: No tasks found for user_id {user_id}.")
                    return "Info: No tasks found for your account."

                formatted_tasks = [f"ID: {task[0]}, Task: {task[1]}, Status: {task[2]}, Due Date: {task[3]}, Priority: {task[4]}" for task in raw_tasks]
                
                logger.info(f"App: Successfully retrieved and formatted {len(formatted_tasks)} tasks for user_id {user_id}.")
                
                return "Your Tasks:\n" + "\n".join(formatted_tasks)

        except mysql.Error as e:
            logger.error(f"App: Database error retrieving tasks for user_id {user_id}: {e}", exc_info=True)
            return "Error: A database problem occurred while retrieving tasks."
        except Exception as e:
            logger.critical(f"App: An unexpected application error occurred while retrieving tasks for user_id {user_id}: {e}", exc_info=True)
            return "Error: An unexpected application error occurred while retrieving tasks."
