import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime, date # Needed for date handling in GUI

from commands import ToDoListApp
from database import Database # Still needed for type hinting or if you move db init here

logger = logging.getLogger(__name__)

class ToDoListGUI:
    def __init__(self, master: tk.Tk, app: ToDoListApp):
        self.master = master
        self.app = app
        self.current_user_id = None # Store the logged-in user's ID

        master.title("ToDo List Application")
        master.geometry("600x500") # Increased size for task management screen

        # --- Login/Registration Frame ---
        self.login_frame = tk.Frame(master, padx=20, pady=20)
        self.login_frame.pack(pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, pady=5, sticky="w")
        self.username_entry = tk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, pady=5, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        self.message_label = tk.Label(self.login_frame, text="", fg="red")
        self.message_label.grid(row=2, column=0, columnspan=2, pady=10)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self._login)
        self.login_button.grid(row=3, column=0, pady=5, padx=5)

        self.register_button = tk.Button(self.login_frame, text="Register", command=self._register)
        self.register_button.grid(row=3, column=1, pady=5, padx=5)

    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.message_label.config(text=f"Attempting login for {username}...")

        user_id, message = self.app.authenticate_user(username, password)
        if user_id:
            self.message_label.config(text=message, fg="green")
            logger.info(f"GUI: Login successful for user '{username}' (ID: {user_id}).")
            self.current_user_id = user_id # Store the user ID
            self._show_main_todo_screen(user_id)
        else:
            self.message_label.config(text=message, fg="red")
            logger.warning(f"GUI: Login failed for user '{username}': {message}")


    def _register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.message_label.config(text=f"Attempting registration for {username}...")

        message = self.app.add_user(username, password)
        if "Success" in message:
            self.message_label.config(text=message, fg="green")
            logger.info(f"GUI: Registration successful for user '{username}'.")
        else:
            self.message_label.config(text=message, fg="red")
            logger.warning(f"GUI: Registration failed for user '{username}': {message}")

    def _show_main_todo_screen(self, user_id):
        self.login_frame.pack_forget() # Hide the login frame

        # --- Main ToDo List Frame ---
        self.main_todo_frame = tk.Frame(self.master, padx=20, pady=20)
        self.main_todo_frame.pack(fill="both", expand=True) # Allow frame to expand

        tk.Label(self.main_todo_frame, text=f"Welcome, User ID: {user_id}!", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.main_todo_frame, text="Your ToDo List:", font=("Arial", 12)).pack(pady=5)

        # --- Task List Display ---
        self.task_list_frame = tk.Frame(self.main_todo_frame)
        self.task_list_frame.pack(fill="both", expand=True, pady=10)

        self.task_listbox = tk.Listbox(self.task_list_frame, height=10, width=50, bd=0)
        self.task_listbox.pack(side="left", fill="both", expand=True)

        self.task_scrollbar = tk.Scrollbar(self.task_list_frame)
        self.task_scrollbar.pack(side="right", fill="y")

        # Link scrollbar to listbox
        self.task_listbox.config(yscrollcommand=self.task_scrollbar.set)
        self.task_scrollbar.config(command=self.task_listbox.yview)

        # Store task data for easy access (e.g., when updating/deleting)
        self.tasks_data = [] # Will store a list of dictionaries (task details)

        # --- Refresh Task Display ---
        self._refresh_tasks_display()

        # --- Add New Task Section ---
        self.add_task_frame = tk.Frame(self.main_todo_frame, pady=10)
        self.add_task_frame.pack(fill="x")

        tk.Label(self.add_task_frame, text="New Task:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        self.new_task_entry = tk.Entry(self.add_task_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=2)

        tk.Label(self.add_task_frame, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=2)
        self.new_due_date_entry = tk.Entry(self.add_task_frame, width=20)
        self.new_due_date_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        tk.Label(self.add_task_frame, text="Priority (0-10):").grid(row=2, column=0, sticky="w", pady=2)
        self.new_priority_entry = tk.Entry(self.add_task_frame, width=10)
        self.new_priority_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        self.add_task_button = tk.Button(self.add_task_frame, text="Add Task", command=self._add_new_task)
        self.add_task_button.grid(row=2, column=2, sticky="e", padx=5, pady=2)

        # Configure columns to expand
        self.add_task_frame.grid_columnconfigure(1, weight=1)

        # --- Logout Button ---
        self.logout_button = tk.Button(self.main_todo_frame, text="Logout", command=self._logout)
        self.logout_button.pack(pady=10)

    def _refresh_tasks_display(self):
        self.task_listbox.delete(0, tk.END) # Clear current listbox contents
        
        # Get tasks from application logic layer
        tasks, message = self.app.get_user_tasks(self.current_user_id)

        if tasks:
            self.tasks_data = tasks # Store the raw task data (list of dictionaries)
            for i, task in enumerate(self.tasks_data):
                # Ensure due_date is handled gracefully if None or not present
                due_date_str = task.get('due_date')
                if due_date_str:
                    # If it's a datetime.date object, format it
                    if isinstance(due_date_str, date):
                        due_date_str = due_date_str.strftime('%Y-%m-%d')
                    # If it's a string from the DB, use it directly
                else:
                    due_date_str = "No Date"

                # Ensure priority is handled gracefully if None or not present
                priority_str = task.get('priority')
                if priority_str is None:
                    priority_str = "N/A"

                display_text = (
                    f"ID: {task.get('id')}, Task: {task.get('task')}, "
                    f"Status: {task.get('task_status').capitalize()}, " # Capitalize for display
                    f"Due: {due_date_str}, Priority: {priority_str}"
                )
                self.task_listbox.insert(tk.END, display_text)
            logger.info("GUI: Task list refreshed successfully.")
        else:
            self.tasks_data = [] # Clear stored data if no tasks
            self.task_listbox.insert(tk.END, message) # Display "No tasks found" message
            logger.info("GUI: No tasks to display or error retrieving tasks.")

    def _add_new_task(self):
        task_name = self.new_task_entry.get()
        due_date = self.new_due_date_entry.get() # Comes as string from entry
        priority_str = self.new_priority_entry.get()

        # Convert priority to int, handle empty string
        priority = None
        if priority_str:
            try:
                priority = int(priority_str)
            except ValueError:
                messagebox.showerror("Input Error", "Priority must be an integer.")
                logger.warning(f"GUI: Invalid priority input '{priority_str}'.")
                return

        # Call application logic to add task
        message = self.app.add_task(self.current_user_id, task_name, due_date, priority)

        if "Success" in message:
            messagebox.showinfo("Success", message)
            self.new_task_entry.delete(0, tk.END) # Clear input fields
            self.new_due_date_entry.delete(0, tk.END)
            self.new_priority_entry.delete(0, tk.END)
            self._refresh_tasks_display() # Refresh the list
            logger.info(f"GUI: New task added successfully for user ID: {self.current_user_id}.")
        else:
            messagebox.showerror("Error", message)
            logger.error(f"GUI: Failed to add new task for user ID: {self.current_user_id}: {message}")

    def _logout(self):
        logger.info(f"GUI: User ID {self.current_user_id} logged out.")
        self.current_user_id = None
        self.main_todo_frame.pack_forget() # Hide main todo frame
        self.login_frame.pack(pady=20) # Show login frame again
        self.username_entry.delete(0, tk.END) # Clear fields
        self.password_entry.delete(0, tk.END)
        self.message_label.config(text="") # Clear message