# ToDo List Application

## Description
A simple yet robust desktop ToDo List application built with Python and Tkinter for the GUI, and a MySQL database for persistent storage. This application allows users to register, log in, and manage their personal tasks including adding, viewing, updating (task name, due date, priority, and status), and deleting tasks.

## Features
* User Registration and Authentication (Login/Logout)
* Add New Tasks with details like task name, due date, and priority.
* View all tasks for the logged-in user.
* Update existing tasks (modify task name, due date, priority, and mark as 'pending' or 'completed').
* Delete tasks.
* Persistent storage using MySQL database.
* Intuitive Graphical User Interface (GUI) using Tkinter.

## Screenshots
*(Once your application is fully functional and styled, you can add screenshots here. This greatly enhances the README.)*

![Login Screen](path/to/your/login_screenshot.png)
![Main ToDo List Screen](path/to/your/main_todo_screenshot.png)
*(Replace `path/to/your/login_screenshot.png` with the actual path or URL to your image)*

## Installation

### Prerequisites
* Python 3.x (e.g., Python 3.11)
* MySQL Server (e.g., MySQL 8.0)
* `pip` (Python package installer)

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/todo-list-app.git](https://github.com/your-username/todo-list-app.git)
    cd todo-list-app
    ```
    *(Replace `https://github.com/your-username/todo-list-app.git` with your actual repository URL)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You'll need to create a `requirements.txt` file. See the "Generate requirements.txt" section below.)*

4.  **MySQL Database Setup:**
    * Create a new MySQL database for the application (e.g., `todo_app_db`).
    * Create a MySQL user with privileges for this database (e.g., `todo_user`).
    * Note down the database name, username, and password.

5.  **Configure environment variables:**
    * Create a `.env` file in the root of your project directory.
    * Add your database connection details to this file:
        ```
        DB_HOST=localhost
        DB_USER=your_mysql_user
        DB_PASSWORD=your_mysql_password
        DB_NAME=todo_app_db
        ```
        *(Replace `your_mysql_user`, `your_mysql_password`, and `todo_app_db` with your actual details.)*
    * Ensure `.env` is ignored by Git (you've already done this!).

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Register or Log In:**
    * If you're a new user, register with a unique username and password.
    * If you already have an account, log in.

3.  **Manage Tasks:**
    * **Add Task:** Enter task details (name, optional due date, optional priority) and click "Add Task".
    * **View Tasks:** Your tasks will be displayed in the listbox.
    * **Update Task:** Select a task from the list, click "Update Selected Task", modify details in the pop-up, and click "Apply Update". You can also change the status to 'completed'.
    * **Delete Task:** Select a task from the list and click "Delete Selected Task".

## File Structure

.
├── .env                # Environment variables for database connection (ignored by Git)
├── .gitignore          # Specifies intentionally untracked files to ignore
├── commands.py         # Contains the application's business logic and command-line interface (CLI) interactions.
├── database.py         # Handles all database interactions (MySQL).
├── GUI.py              # Implements the Graphical User Interface using Tkinter.
├── main.py             # The main entry point of the application.
├── README.md           # This file.
└── requirements.txt    # Lists Python dependencies.


## Technologies Used
* Python 3
* Tkinter (Python's standard GUI library)
* MySQL Connector/Python
* `python-dotenv` (for loading environment variables)
* `bcrypt` (for password hashing)

## Future Enhancements
* Task filtering and sorting (by status, due date, priority).
* User profiles and settings.
* Notifications for upcoming due dates.
* More robust input validation and error handling in GUI.
* Search functionality for tasks.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
*(You'll need to create a `LICENSE.md` file in your repository if you choose the MIT license or any other open-source license.)*

---