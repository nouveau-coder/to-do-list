# gui.py

import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime, date # Needed for date handling in GUI

from commands import ToDoListApp
# Database is imported here for type hinting, though the ToDoListApp is passed the instance
from database import Database

logger = logging.getLogger(__name__)

class ToDoListGUI:
    def __init__(self, master: tk.Tk, app: ToDoListApp):
        self.master = master
        self.app = app
        self.current_user_id = None # Store the logged-in user's ID

        master.title("ToDo List Application")
        master.geometry("600x550") # Increased size slightly for new buttons and actions

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

        # IMPORTANT: Added selectmode=tk.SINGLE to allow selecting items for update/delete
        self.task_listbox = tk.Listbox(self.task_list_frame, height=10, width=50, bd=0, selectmode=tk.SINGLE)
        self.task_listbox.pack(side="left", fill="both", expand=True)

        self.task_scrollbar = tk.Scrollbar(self.task_list_frame)
        self.task_scrollbar.pack(side="right", fill="y")

        # Link scrollbar to listbox
        self.task_listbox.config(yscrollcommand=self.task_scrollbar.set)
        self.task_scrollbar.config(command=self.task_listbox.yview)

        # Store task data for easy access (e.g., when updating/deleting)
        self.tasks_data = [] # Will store a list of dictionaries (task details from DB)

        # --- Refresh Task Display ---
        self._refresh_tasks_display()

        # --- Task Action Buttons (Update/Delete) ---
        self.action_buttons_frame = tk.Frame(self.main_todo_frame)
        self.action_buttons_frame.pack(pady=5)

        self.update_button = tk.Button(self.action_buttons_frame, text="Update Selected Task", command=self._show_update_task_dialog)
        self.update_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(self.action_buttons_frame, text="Delete Selected Task", command=self._delete_selected_task)
        self.delete_button.pack(side="left", padx=5)


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
        tasks, message = self.app.get_user_tasks(self.current_user_id) # This expects a list of dicts and a message

        if tasks: # If tasks list is not empty
            self.tasks_data = tasks # Store the raw task data (list of dictionaries)
            for i, task in enumerate(self.tasks_data):
                # Ensure due_date is handled gracefully if None or not present
                due_date_str = task.get('due_date')
                if due_date_str:
                    # If it's a datetime.date object, format it
                    if isinstance(due_date_str, date):
                        due_date_str = due_date_str.strftime('%Y-%m-%d')
                    # If it's a string from the DB, use it directly (though DB should return date obj if column type is DATE)
                else:
                    due_date_str = "No Date"

                # Ensure priority is handled gracefully if None or not present
                priority_str = task.get('priority')
                if priority_str is None:
                    priority_str = "N/A"

                display_text = (
                    f"ID: {task.get('id')}, Task: {task.get('task')}, "
                    f"Status: {task.get('task_status').capitalize() if task.get('task_status') else 'N/A'}, " # Capitalize for display, handle None
                    f"Due: {due_date_str}, Priority: {priority_str}"
                )
                self.task_listbox.insert(tk.END, display_text)
            logger.info("GUI: Task list refreshed successfully.")
        else: # If tasks list is empty or None
            self.tasks_data = [] # Clear stored data if no tasks
            # Display the message returned by get_user_tasks (e.g., "No tasks found")
            self.task_listbox.insert(tk.END, message)
            logger.info("GUI: No tasks to display or error retrieving tasks.")

    def _add_new_task(self):
        task_name = self.new_task_entry.get()
        due_date = self.new_due_date_entry.get() # Comes as string from entry
        priority_str = self.new_priority_entry.get()

        if not task_name.strip():
            messagebox.showerror("Input Error", "Task name cannot be empty.")
            logger.warning(f"GUI: Attempted to add empty task name for user ID: {self.current_user_id}.")
            return

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

    # --- Helper to get selected task ID ---
    def _get_selected_task_id(self):
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a task from the list.")
            return None

        selected_index = selected_indices[0]
        if selected_index < len(self.tasks_data):
            return self.tasks_data[selected_index]['id']
        return None # Should not happen if indices are valid and tasks_data is populated

    # --- Delete Task Method ---
    def _delete_selected_task(self):
        task_id_to_delete = self._get_selected_task_id()
        if task_id_to_delete is None:
            return # Error message already shown by _get_selected_task_id

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Task ID: {task_id_to_delete}?"):
            message = self.app.delete_task(self.current_user_id, task_id_to_delete)

            if "Success" in message:
                messagebox.showinfo("Success", message)
                self._refresh_tasks_display() # Refresh the list after deletion
                logger.info(f"GUI: Task ID {task_id_to_delete} deleted successfully for user ID: {self.current_user_id}.")
            else:
                messagebox.showerror("Error", message)
                logger.error(f"GUI: Failed to delete Task ID {task_id_to_delete} for user ID: {self.current_user_id}: {message}")

    # --- Update Task Dialog and Logic ---
    def _show_update_task_dialog(self):
        task_id_to_update = self._get_selected_task_id()
        if task_id_to_update is None:
            return

        selected_task = next((task for task in self.tasks_data if task['id'] == task_id_to_update), None)
        if not selected_task:
            messagebox.showerror("Error", "Could not retrieve details for selected task.")
            logger.error(f"GUI: Task ID {task_id_to_update} not found in current tasks_data for update.")
            return

        # --- Create a new top-level window for updating ---
        update_window = tk.Toplevel(self.master)
        update_window.title(f"Update Task ID: {task_id_to_update}")
        update_window.geometry("350x300") # Adjusted size
        update_window.transient(self.master) # Make it appear on top of the main window
        update_window.grab_set() # Disable interaction with the main window

        update_frame = tk.Frame(update_window, padx=15, pady=15)
        update_frame.pack(fill="both", expand=True)

        # Labels and Entry fields for updating task details
        tk.Label(update_frame, text="Task Name:").grid(row=0, column=0, sticky="w", pady=5)
        task_name_var = tk.StringVar(value=selected_task.get('task', ''))
        task_name_entry = tk.Entry(update_frame, textvariable=task_name_var, width=30)
        task_name_entry.grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(update_frame, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=5)
        current_due_date = selected_task.get('due_date')
        if current_due_date and isinstance(current_due_date, date):
            current_due_date = current_due_date.strftime('%Y-%m-%d')
        else:
            current_due_date = "" # Empty string if no date
        due_date_var = tk.StringVar(value=current_due_date)
        due_date_entry = tk.Entry(update_frame, textvariable=due_date_var, width=30)
        due_date_entry.grid(row=1, column=1, sticky="ew", padx=5)

        tk.Label(update_frame, text="Priority (0-10):").grid(row=2, column=0, sticky="w", pady=5)
        priority_var = tk.StringVar(value=str(selected_task.get('priority', ''))) # Convert int to str for entry
        priority_entry = tk.Entry(update_frame, textvariable=priority_var, width=30)
        priority_entry.grid(row=2, column=1, sticky="ew", padx=5)

        tk.Label(update_frame, text="Status (pending/completed):").grid(row=3, column=0, sticky="w", pady=5)
        status_var = tk.StringVar(value=selected_task.get('task_status', 'pending'))
        status_option_menu = tk.OptionMenu(update_frame, status_var, "pending", "completed")
        status_option_menu.grid(row=3, column=1, sticky="ew", padx=5)


        # --- Update Button ---
        def perform_update():
            updated_task_name = task_name_var.get()
            updated_due_date = due_date_var.get()
            updated_priority_str = priority_var.get()
            updated_status = status_var.get()

            updated_priority = None
            if updated_priority_str:
                try:
                    updated_priority = int(updated_priority_str)
                except ValueError:
                    messagebox.showerror("Input Error", "Priority must be an integer.")
                    logger.warning(f"GUI: Invalid priority input '{updated_priority_str}' during update.")
                    return
            
            # If task name is empty, treat as None for update
            if not updated_task_name.strip():
                updated_task_name = None
            
            # If due date is empty, treat as None for update
            if not updated_due_date.strip():
                updated_due_date = None


            # Call the update_task method from ToDoListApp
            message = self.app.update_task(
                user_id=self.current_user_id,
                task_id=task_id_to_update,
                task_name=updated_task_name,
                due_date=updated_due_date,
                priority=updated_priority,
                task_status=updated_status # Pass the status
            )

            if "Success" in message or "Info" in message: # Info for no changes needed
                messagebox.showinfo("Update Result", message)
                update_window.destroy() # Close the update window
                self._refresh_tasks_display() # Refresh the main list
                logger.info(f"GUI: Task ID {task_id_to_update} updated for user ID: {self.current_user_id}.")
            else:
                messagebox.showerror("Update Error", message)
                logger.error(f"GUI: Failed to update Task ID {task_id_to_update} for user ID: {self.current_user_id}: {message}")

        update_button = tk.Button(update_frame, text="Apply Update", command=perform_update)
        update_button.grid(row=4, column=0, columnspan=2, pady=10)

        update_frame.grid_columnconfigure(1, weight=1) # Allow entry field to expand

        update_window.protocol("WM_DELETE_WINDOW", update_window.destroy) # Handle window close

    def _logout(self):
        logger.info(f"GUI: User ID {self.current_user_id} logged out.")
        self.current_user_id = None
        self.main_todo_frame.pack_forget() # Hide main todo frame
        self.login_frame.pack(pady=20) # Show login frame again
        self.username_entry.delete(0, tk.END) # Clear fields
        self.password_entry.delete(0, tk.END)
        self.message_label.config(text="")