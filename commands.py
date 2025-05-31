# commands.py
from database import Database
# import bcrypt # Uncomment and install if you implement password hashing

class ToDoListApp: # Renamed for clarity, implies it's the application logic layer
    """
    Handles the core business logic for the ToDoList application,
    interacting with the database and providing high-level operations.
    """
    def __init__(self, db_instance: Database):
        """
        Initializes the ToDoListApp with a database instance.

        Args:
            db_instance (Database): An instance of the Database class.
        """
        self.db = db_instance

    def signup(self, name: str, password: str) -> int | None:
        """
        Registers a new user in the system.
        Hashes the password before storing (placeholder for actual hashing).

        Args:
            name (str): The desired username.
            password (str): The plain-text password.

        Returns:
            int | None: The new user's ID if successful, None otherwise.
        """
        if not name or not password:
            return None # GUI should show error message for empty fields

        # --- IMPORTANT SECURITY CONSIDERATION ---
        # NEVER store plain passwords. Use a strong hashing library like bcrypt.
        # Example with bcrypt (install: pip install bcrypt):
        # try:
        #     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        #     new_user_id = self.db.add_user(name, hashed_password)
        #     return new_user_id
        # except Exception as e:
        #     print(f"Error during password hashing or user registration: {e}") # Log for debugging
        #     return None
        # --- END SECURITY CONSIDERATION ---

        # For now, using plain password as per your original code (but highly discouraged for real apps)
        new_user_id = self.db.add_user(name, password) # Assuming Database.add_user is updated to return ID
        return new_user_id


    def login(self, name: str, password: str) -> int | None:
        """
        Authenticates a user based on username and password.

        Args:
            name (str): The username.
            password (str): The plain-text password entered by the user.

        Returns:
            int | None: The user ID if login is successful, None otherwise.
        """
        if not name or not password:
            return None # GUI should show error for empty fields

        # This assumes Database.get_user_by_name_and_password exists and returns (userid, name, hashed_password)
        user_data = self.db.get_user_by_name_and_password(name, password)

        if user_data:
            user_id, retrieved_name, stored_password_hash = user_data
            # --- IMPORTANT SECURITY CONSIDERATION ---
            # if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            #     return user_id
            # else:
            #     return None # Password mismatch
            # --- END SECURITY CONSIDERATION ---

            # For now, using direct comparison as per your original code (if password is NOT hashed in DB)
            # If you implement hashing, you MUST remove this line and use the bcrypt.checkpw above.
            return user_id # Returns the user ID upon successful login
        return None # User not found or incorrect credentials


    def add_task(self, user_id: int, task_description: str) -> bool:
        """
        Adds a new task for a specified user.

        Args:
            user_id (int): The ID of the user.
            task_description (str): The description of the task to add.

        Returns:
            bool: True if the task was added successfully, False otherwise.
        """
        if not user_id or not task_description:
            return False
        try:
            self.db.add_task(user_id, task_description)
            return True
        except Exception as e:
            print(f"Error adding task for user {user_id}: {e}") # Log error for debugging
            return False

    def get_all_tasks(self, user_id: int) -> list[tuple[str, str]]:
        """
        Retrieves all tasks for a given user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple is (task_description, status).
                                   Returns an empty list if no tasks or on error.
        """
        if not user_id:
            return []
        try:
            tasks = self.db.get_tasks(user_id) # Assuming this now returns (task, status)
            return tasks
        except Exception as e:
            print(f"Error retrieving tasks for user {user_id}: {e}") # Log error for debugging
            return []

    def delete_task(self, user_id: int, task_description: str) -> bool:
        """
        Deletes a specific task for a user.

        Args:
            user_id (int): The ID of the user.
            task_description (str): The description of the task to delete.

        Returns:
            bool: True if the task was deleted successfully, False otherwise.
        """
        if not user_id or not task_description:
            return False
        try:
            self.db.remove_task(user_id, task_description)
            # You might want to check self.db.cur.rowcount in database.py's remove_task
            # and return that count to determine if a row was actually deleted.
            return True # Assuming success unless an exception occurs
        except Exception as e:
            print(f"Error deleting task for user {user_id}: {e}") # Log error for debugging
            return False

    def update_task_status(self, user_id: int, task_description: str, new_status: str) -> bool:
        """
        Updates the status of a specific task for a user.

        Args:
            user_id (int): The ID of the user.
            task_description (str): The description of the task to update.
            new_status (str): The new status for the task (e.g., 'completed', 'pending').

        Returns:
            bool: True if the task status was updated successfully, False otherwise.
        """
        if not user_id or not task_description or not new_status:
            return False
        try:
            self.db.update_task_status(user_id, task_description, new_status)
            return True
        except Exception as e:
            print(f"Error updating task status for user {user_id}: {e}") # Log error for debugging
            return False