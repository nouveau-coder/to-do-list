# main.py
import tkinter as tk
from database import Database
from commands import ToDoListApp
from GUI import ToDoAppGUI
from tkinter import messagebox # Import messagebox for error display

def main():
    # 1. Initialize the database connection
    # Corrected: changed 'username' to 'user' to match Database.__init__
    db = Database()

    # Check if database connection was successful before proceeding
    if not db.con or not db.con.is_connected():
        print("Application cannot start: Failed to connect to the database.")
        root = tk.Tk()
        root.withdraw() # Hide the main window
        messagebox.showerror("Database Error", "Failed to connect to the database. Please ensure MySQL is running and credentials are correct.")
        root.destroy()
        return

    # 2. Ensure necessary tables are created in the database
    db.create_tables()

    # 3. Initialize the application commands/logic layer, injecting the database instance
    app_commands = ToDoListApp(db)

    # 4. Initialize the GUI, injecting the commands layer
    root = tk.Tk()
    app = ToDoAppGUI(root, app_commands)

    # 5. Run the GUI application
    app.run()

    # The database connection will be closed by app._on_closing when the GUI window is closed.
    # If the app exits unexpectedly, you might want a more robust cleanup.
    # A simple 'finally' block can ensure this:
    # try:
    #     app.run()
    # finally:
    #     db.close_connection() # Ensure connection is closed even if app.run() crashes

if __name__ == "__main__":
    main()