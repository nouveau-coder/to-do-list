import tkinter as tk
from tkinter import messagebox
import logging

from commands import ToDoListApp
from database import Database

logger = logging.getLogger(__name__)

class ToDoListGUI:
    def __init__(self, master: tk.Tk, app: ToDoListApp):
        self.master = master
        self.app = app

        master.title("ToDo List Application")
        master.geometry("400x300")

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
        self.login_frame.pack_forget() 
        self.main_todo_frame = tk.Frame(self.master, padx=20, pady=20)
        self.main_todo_frame.pack(pady=20)
        tk.Label(self.main_todo_frame, text=f"Welcome, User ID: {user_id}!").pack(pady=10)
        tk.Label(self.main_todo_frame, text="This is your ToDo list.").pack(pady=5)
