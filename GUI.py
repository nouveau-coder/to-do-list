import tkinter as tk
from tkinter import messagebox
from commands import ToDoListAppCommands # Use the renamed class

class ToDoAppGUI: # Renamed for clarity as the GUI part
    def __init__(self, root: tk.Tk, app_commands: ToDoListAppCommands):
        self.root = root
        self.root.title("To-Do List App")
        self.root.geometry("600x550") # Set a default window size
        self.todo_list_commands = app_commands # Injected commands instance
        self.user_id = None
        self.current_user_name = None

        self._create_widgets()
        # Ensure database connection is closed when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Handles window closing to ensure database connection is closed."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.todo_list_commands.db.close_connection() # Access the database instance via commands
            self.root.destroy()

    def _create_widgets(self):
        # --- Login/Signup Frame ---
        self.login_frame = tk.Frame(self.root, padx=30, pady=30, bd=2, relief="groove")
        self.login_frame.pack(pady=20, padx=20)

        tk.Label(self.login_frame, text="Username:", font=('Arial', 12)).grid(row=0, column=0, pady=10, sticky='w')
        self.username_entry = tk.Entry(self.login_frame, width=35, font=('Arial', 12))
        self.username_entry.grid(row=0, column=1, pady=10, padx=5)

        tk.Label(self.login_frame, text="Password:", font=('Arial', 12)).grid(row=1, column=0, pady=10, sticky='w')
        self.password_entry = tk.Entry(self.login_frame, show='*', width=35, font=('Arial', 12))
        self.password_entry.grid(row=1, column=1, pady=10, padx=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self._login,
                                      font=('Arial', 12), bg='#4CAF50', fg='white', width=15)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=15)

        self.signup_button = tk.Button(self.login_frame, text="Sign Up", command=self._signup,
                                       font=('Arial', 12), bg='#2196F3', fg='white', width=15)
        self.signup_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.status_label = tk.Label(self.login_frame, text="", fg="red", font=('Arial', 10))
        self.status_label.grid(row=4, columnspan=2, pady=10)

        # --- Task Management Frame (initially hidden) ---
        self.task_frame = tk.Frame(self.root, padx=20, pady=20, bd=2, relief="groove")

        self.welcome_label = tk.Label(self.task_frame, text="", font=('Arial', 16, 'bold'))
        self.welcome_label.grid(row=0, columnspan=3, pady=15)

        tk.Label(self.task_frame, text="New Task:", font=('Arial', 12)).grid(row=1, column=0, pady=10, sticky='w')
        self.task_entry = tk.Entry(self.task_frame, width=40, font=('Arial', 12))
        self.task_entry.grid(row=1, column=1, pady=10, padx=5)

        self.add_task_button = tk.Button(self.task_frame, text="Add Task", command=self._add_task,
                                         font=('Arial', 12), bg='#4CAF50', fg='white', width=15)
        self.add_task_button.grid(row=1, column=2, pady=10, padx=5)

        # --- Task Listbox with Scrollbar ---
        tk.Label(self.task_frame, text="Your Tasks:", font=('Arial', 12, 'underline')).grid(row=2, columnspan=3, pady=10, sticky='w')

        self.task_list_frame = tk.Frame(self.task_frame) # Frame for listbox and scrollbar
        self.task_list_frame.grid(row=3, columnspan=3, pady=5)

        self.task_listbox = tk.Listbox(self.task_list_frame, width=65, height=12, selectmode=tk.SINGLE,
                                      font=('Arial', 11), bd=2, relief="sunken")
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.task_list_frame, orient="vertical", command=self.task_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)

        # --- Task Action Buttons ---
        self.action_buttons_frame = tk.Frame(self.task_frame)
        self.action_buttons_frame.grid(row=4, columnspan=3, pady=15)

        self.mark_complete_button = tk.Button(self.action_buttons_frame, text="Mark Complete", command=self._mark_task_complete,
                                               font=('Arial', 11), bg='#FFC107', width=15)
        self.mark_complete_button.pack(side=tk.LEFT, padx=5)

        self.mark_pending_button = tk.Button(self.action_buttons_frame, text="Mark Pending", command=self._mark_task_pending,
                                              font=('Arial', 11), bg='#FF9800', width=15)
        self.mark_pending_button.pack(side=tk.LEFT, padx=5)

        self.delete_task_button = tk.Button(self.action_buttons_frame, text="Delete Selected Task", command=self._delete_task,
                                             font=('Arial', 11), bg='#F44336', fg='white', width=20)
        self.delete_task_button.pack(side=tk.LEFT, padx=5)

        self.logout_button = tk.Button(self.task_frame, text="Logout", command=self._logout,
                                       font=('Arial', 12), bg='#607D8B', fg='white', width=15)
        self.logout_button.grid(row=5, columnspan=3, pady=20)

    def _login(self):
        """Handles user login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._display_message("Please enter both username and password.", "red")
            return

        user_id = self.todo_list_commands.login_user(username, password)

        if user_id:
            self.user_id = user_id
            self.current_user_name = username
            self._display_message(f"Welcome, {username}!", "green")
            self._show_task_management_view()
        else:
            self._display_message("Invalid username or password. Please try again.", "red")
            self.password_entry.delete(0, 'end') # Clear password field on failed login

    def _signup(self):
        """Handles new user registration."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._display_message("Please enter both username and password for signup.", "red")
            return

        user_id = self.todo_list_commands.signup_user(username, password)

        if user_id:
            self._display_message(f'Signed up successfully! Your User ID is {user_id}. You can now log in.', "blue")
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
        else:
            self._display_message("Sign up failed. Username might already exist or a database error occurred.", "red")

    def _show_task_management_view(self):
        """Switches to the task management view."""
        self.login_frame.pack_forget()
        self.task_frame.pack(pady=20, padx=20)
        self.welcome_label.config(text=f"Welcome, {self.current_user_name}!")
        self._load_tasks() # Automatically load tasks after login

    def _load_tasks(self):
        """Loads and displays tasks for the current user in the listbox."""
        if self.user_id:
            tasks = self.todo_list_commands.get_user_tasks(self.user_id)
            self.task_listbox.delete(0, 'end')
            if tasks:
                for task, status in tasks:
                    display_text = f"{task} [{status.capitalize()}]"
                    self.task_listbox.insert('end', display_text)
                    if status == 'completed':
                        self.task_listbox.itemconfig('end', {'fg': 'gray', 'bg': '#e0ffe0'}) # Light green background
                    else:
                        self.task_listbox.itemconfig('end', {'fg': 'black', 'bg': 'white'})
            else:
                self.task_listbox.insert('end', "No tasks found. Add a new one!")
                self.task_listbox.itemconfig('end', {'fg': 'blue'})
        else:
            self._display_message("Please log in to view tasks.", "red")

    def _add_task(self):
        """Adds a new task for the current user."""
        task_description = self.task_entry.get().strip()
        if not task_description:
            self._display_message("Task description cannot be empty.", "red")
            return

        if self.user_id:
            if self.todo_list_commands.add_new_task(self.user_id, task_description):
                self._display_message("Task added successfully!", "green")
                self.task_entry.delete(0, 'end')
                self._load_tasks() # Refresh task list
            else:
                self._display_message("Failed to add task. Please try again.", "red")
        else:
            self._display_message("Please log in to add tasks.", "red")

    def _delete_task(self):
        """Deletes the selected task for the current user."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            self._display_message("Please select a task to delete.", "orange")
            return

        selected_text = self.task_listbox.get(selected_indices[0])
        # Extract original task description from display text (e.g., "Task [Status]")
        task_description_to_delete = selected_text.split(' [')[0].strip()

        if self.user_id:
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task_description_to_delete}'?")
            if confirm:
                if self.todo_list_commands.delete_user_task(self.user_id, task_description_to_delete):
                    self._display_message(f"Task '{task_description_to_delete}' deleted successfully!", "green")
                    self._load_tasks() # Refresh task list
                else:
                    self._display_message("Failed to delete task. Please try again.", "red")
        else:
            self._display_message("Please log in to delete tasks.", "red")

    def _mark_task_complete(self):
        """Marks the selected task as 'completed'."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            self._display_message("Please select a task to mark complete.", "orange")
            return

        selected_text = self.task_listbox.get(selected_indices[0])
        task_description = selected_text.split(' [')[0].strip()

        if self.user_id:
            if self.todo_list_commands.mark_task_status(self.user_id, task_description, "completed"):
                self._display_message(f"Task '{task_description}' marked complete!", "green")
                self._load_tasks() # Refresh task list
            else:
                self._display_message("Failed to mark task complete. Please try again.", "red")
        else:
            self._display_message("Please log in to update tasks.", "red")

    def _mark_task_pending(self):
        """Marks the selected task as 'pending'."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            self._display_message("Please select a task to mark pending.", "orange")
            return

        selected_text = self.task_listbox.get(selected_indices[0])
        task_description = selected_text.split(' [')[0].strip()

        if self.user_id:
            if self.todo_list_commands.mark_task_status(self.user_id, task_description, "pending"):
                self._display_message(f"Task '{task_description}' marked pending!", "green")
                self._load_tasks() # Refresh task list
            else:
                self._display_message("Failed to mark task pending. Please try again.", "red")
        else:
            self._display_message("Please log in to update tasks.", "red")

    def _logout(self):
        """Logs out the current user and returns to the login screen."""
        self.user_id = None
        self.current_user_name = None
        self.task_frame.pack_forget()
        self.login_frame.pack(pady=20, padx=20)
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.status_label.config(text="") # Clear previous status message
        self.task_listbox.delete(0, 'end') # Clear tasks on logout
        self._display_message("Logged out successfully.", "blue")

    def _display_message(self, message: str, color: str = "black"):
        """Displays a message in the status label."""
        self.status_label.config(text=message, fg=color)
        # Optionally, clear the message after a few seconds:
        # self.root.after(5000, lambda: self.status_label.config(text=""))

    def run(self):
        """Starts the Tkinter event loop."""
        self.root.mainloop()