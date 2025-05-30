import tkinter as tk
from commands import ToDoList

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.todo_list = ToDoList()
        self.user_id = None
        
        self.create_widgets()

    def create_widgets(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=10)

        tk.Label(self.login_frame, text="User ID:").grid(row=0, column=0)
        self.user_id_entry = tk.Entry(self.login_frame)
        self.user_id_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2)

        self.signup_button = tk.Button(self.login_frame, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=3, columnspan=2)

        self.task_frame = tk.Frame(self.root)
        
    def login(self):
        user_id = int(self.user_id_entry.get())
        password = self.password_entry.get()
        
        if self.todo_list.login(user_id, password):
            self.user_id = user_id
            self.show_task_management()

    def signup(self):
        name = self.user_id_entry.get()
        password = self.password_entry.get()
        
        if name and password:
            user_id = self.todo_list.signup(name, password)
            if user_id:
                self.user_id_entry.delete(0, 'end')
                self.password_entry.delete(0, 'end')
                print(f'Signed up successfully! Your User ID is {user_id}.')

    def show_task_management(self):
        self.login_frame.pack_forget()
        self.task_frame.pack(pady=10)

        tk.Label(self.task_frame, text="Task:").grid(row=0, column=0)
        self.task_entry = tk.Entry(self.task_frame)
        self.task_entry.grid(row=0, column=1)

        self.add_task_button = tk.Button(self.task_frame, text="Add Task", command=self.add_task)
        self.add_task_button.grid(row=0, column=2)

        self.view_tasks_button = tk.Button(self.task_frame, text="View Tasks", command=self.view_tasks)
        self.view_tasks_button.grid(row=1, columnspan=3)
        
        self.delete_task_button = tk.Button(self.task_frame, text="Delete Task", command=self.delete_task)
        self.delete_task_button.grid(row=2, columnspan=3)
        
        self.task_listbox = tk.Listbox(self.task_frame, width=50)
        self.task_listbox.grid(row=3, columnspan=3, pady=10)
    
    def add_task(self):
        task = self.task_entry.get()
        if task and self.user_id:
            self.todo_list.add_task(self.user_id, task)
            self.task_entry.delete(0, 'end')
            self.view_tasks()
    
    def view_tasks(self):
        if self.user_id:
            tasks = self.todo_list.view_tasks(self.user_id)
            self.task_listbox.delete(0, 'end')
            for task in tasks:
                self.task_listbox.insert('end', task[0])
    
    def delete_task(self):
        selected_task = self.task_listbox.curselection()
        if selected_task and self.user_id:
            task = self.task_listbox.get(selected_task)
            self.todo_list.delete_task(self.user_id, task)
            self.view_tasks()
            self.task_listbox.delete(selected_task)

    def run(self):
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = ToDoApp(root)
    app.run()

if __name__ == "__main__":
    main()    
    

    



