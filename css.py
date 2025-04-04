import sv_ttk
from tkinter import ttk
from tkinter import messagebox


def configure_styles():
    sv_ttk.use_light_theme()
    style = ttk.Style()
    style.configure('photo.TFrame', background='#b56d26')
    style.configure('title_login.TFrame', background='maroon')
    style.configure('tables.TFrame', background='#b56d26')
    style.configure('TButton', font=('Kanit Light', 16), padding=10)
    style.configure('tables.TButton', font=('Kanit', 17))
    style.configure('tablesHeader.TFrame', background='maroon')

if __name__ == '__main__':
    messagebox.showwarning('Warning', 'Wrong way to run the module. Run the index.py file instead.')