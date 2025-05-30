from database import Database
import random

class ToDoList:
    def __init__(self):
        self.db = Database()
        self.db.create_tables()

    def signup(self, name, password):
        user_id = random.randint(1000, 9999)
        self.db.add_user(user_id, name, password)
        print(f'Your user ID is: {user_id}. Please remember it for future logins.')
        return user_id

    def login(self, user_id, password):
        user = self.db.get_user(user_id)
        if user and user[0] == user_id:
            print(f'Welcome User {user_id}!')
            return True
        else:
            print('Invalid user ID or password. Please try again.')
            return False

    def add_task(self, user_id, task):
        self.db.add_task(user_id, task)
        print('Task added successfully!')

    def view_tasks(self, user_id):
        tasks = self.db.get_tasks(user_id)
        if tasks:
            print('Your tasks:')
            for task in tasks:
                print(f'- {task[0]}')
        else:
            print('You have no tasks.')

    def delete_task(self, user_id, task):
        self.db.remove_task(user_id, task)
        print('Task deleted successfully!')