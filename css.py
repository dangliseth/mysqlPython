import sv_ttk
from tkinter import ttk
from tkinter import messagebox


def configure_styles():
    sv_ttk.use_light_theme()
    style = ttk.Style()
    style.configure('photo.TFrame', background='#b56d26')
    style.configure('title_login.TFrame', background='maroon')
    style.configure('tables.TFrame')
    style.configure('TButton', font=('Kanit Light', 16), padding=10)
    style.configure('tables.TButton', font=('Kanit', 17))
    style.configure('tablesHeader.TFrame')
    style.configure('design.TFrame', background='#552A00')

if __name__ == '__main__':
    messagebox.showwarning('Warning', 'Wrong way to run the module. Run the index.py file instead.')