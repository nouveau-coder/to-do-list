import GUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = GUI.ToDoApp(root)
    app.run()

if __name__ == "__main__":
    main()  