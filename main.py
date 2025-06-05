import logging
import tkinter as tk
from database import Database
from commands import ToDoListApp
from GUI import ToDoListGUI 

logger = logging.getLogger(__name__)

def main():
    db_conn_instance = None
    try:
        db_conn_instance = Database()
        app = ToDoListApp(db_conn_instance)
        app.setup_database()

        root = tk.Tk()
        gui = ToDoListGUI(root, app)
        root.mainloop()

    except Exception as e:
         logger.critical(f"Application encountered a critical error: {e}", exc_info=True)
         print(f"FATAL ERROR: Application could not run. Check logs for details.")

if __name__ == "__main__":
    main()