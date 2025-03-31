import mysql.connector
from mysql.connector import errorcode


import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import sv_ttk
import datetime
import qrcode
from PIL import ImageTk, Image

from autocomplete import AutocompleteCombobox
from convert_functions import *


def configure_styles():
    sv_ttk.set_theme("light")
    style = ttk.Style()
    style.configure('photo.TFrame', background='#b56d26')
    style.configure('title_login.TFrame', background='maroon')


class Login:
    def __init__(self, root):
        self.db = None
        self.accountType = None
        self.root = root

        configure_styles()

        self.root.title("Login")
        self.root.state('zoomed')

        center_frame = ttk.Frame(self.root)
        center_frame.place(relx=0.5, rely=0.6, anchor='center')

        photo_frame = ttk.Frame(self.root, style='photo.TFrame')
        photo_frame.place(relx=0, rely=0.1, relwidth=1)

        try:
            photo_path = "photos/MLQU-logo-1.png"
            # Open the image using Pillow
            img = Image.open(photo_path)

            # Resize the image while maintaining the aspect ratio
            max_width, max_height = 175, 175  # Set the maximum width and height
            img.thumbnail((max_width, max_height), Image.LANCZOS)

            # Convert the resized image to a format compatible with tkinter
            photo = ImageTk.PhotoImage(img)

            # Add the photo to the label
            photo_label = ttk.Label(photo_frame, image=photo, background='#b56d26')
            photo_label.image = photo  # Keep a reference to avoid garbage collection
            photo_label.pack(pady=10)
        except FileNotFoundError:
            # If the image file is not found, display a text instead
            ttk.Label(center_frame, text="MLQU", font=('Kanit Light', 50)).grid(row=0, column=2, columnspan=2, pady=10)

        title_frame = ttk.Frame(self.root, style='title_login.TFrame')
        title_frame.place(relx=0.2, rely=0.5, relheight=1, anchor='center')

        ttk.Label(title_frame, text="Inventory \nManagement", font=('Orbitron Black', 25), justify="center", foreground='white', background='maroon').pack(expand=True, fill='both', padx=10, pady=10)

        ttk.Label(center_frame, text="Username:", font=('Kanit Light', 15)).grid(row=2, column=1, padx=10, pady=10)
        self.username_var = StringVar()
        username_entry = ttk.Entry(center_frame, textvariable=self.username_var, font=('Kanit Light', 15))
        username_entry.grid(row=2, column=2, padx=10, pady=10)
        username_entry.focus_set()

        ttk.Label(center_frame, text="Password:", font=('Kanit Light', 15)).grid(row=3, column=1, padx=10, pady=10)
        self.password_var = StringVar()
        ttk.Entry(center_frame, textvariable=self.password_var, font=('Kanit Light', 15), show="*").grid(row=3, column=2, padx=10, pady=10)

        ttk.Button(center_frame, text="Login", command=self.attempt_login).grid(row=4, column=1, columnspan=2, pady=10)
        self.root.bind('<Return>', self.attempt_login)


    def attempt_login(self, event=None):
            username = self.username_var.get()
            password = self.password_var.get()
            config = {
                "user": username,
                "password": password,
                "host": "localhost",
                "database": "inventory_database",
            }
            try:
                self.db = mysql.connector.connect(**config)
                cursor = self.db.cursor()
                cursor.execute("SELECT Super_priv FROM mysql.user WHERE user = %s", (username,))
                result = cursor.fetchone()
                if result and result[0] == 'Y':
                    self.accountType = "Admin"
                else:
                    self.accountType = "Viewer"

                print(f"Account Type: {self.accountType}")
                self.root.destroy()
                InventoryApp(self.db, self.accountType).init()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", "Invalid username or password")

            


class InventoryApp:
    def __init__(self, db, account_type):
        self.db = db
        self.account_type = account_type
    def init(self):
        self.root = tk.Tk()
        self.root.title("Inventory Database App")
        self.root.state('zoomed')
        
        configure_styles()

        header_frame = tk.Frame(self.root)
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        header = tk.Label(header_frame, text="Inventory Management", font=("Kanit Light", 46), anchor='center')
        header.grid(row=0, column=1, padx=10, pady=10)
        logout_button = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_button.grid(row=0, column=0, padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)

        tables = self.fetch_tables()
        if tables:
            frame = ttk.Frame(self.root)
            frame.place(relx=0.5, rely=0.5, anchor='center')

            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
            listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Kanit Light", 20), justify='center')
            scrollbar.config(command=listbox.yview)

            for table in tables:
                listbox.insert(tk.END, table)

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            accessedTable = AccessedTable(self.db, self.account_type, self.root)
            access_button = ttk.Button(self.root, text="Access Table",
                                       command=lambda: accessedTable.access_table(listbox.get(tk.ACTIVE)))
            access_button.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.mainloop()

    def logout(self):
        self.root.destroy()
        Login(root=tk.Tk()).root.mainloop()

    def fetch_tables(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                messagebox.showerror("Error", "Database does not exist")
            else:
                messagebox.showerror("Error", str(err))
            return []


class AccessedTable:
    def __init__(self, db, accountType, root):
        self.db = db
        self.accountType = accountType
        self.root = root
    def access_table(self, table):
        categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
        departments = ['Department 1', 'Department 2', 'Department 3', 
                    'Department 4', 'Department 5', 'Department 6']
        cursor = self.db.cursor()
        def refresh_table():
            for i in tree.get_children():
                tree.delete(i)
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)

        def fetch_employee_names():
            cursor.execute("SELECT name FROM employees")
            return [row[0] for row in cursor.fetchall()]

        def create():
            create_window = tk.Toplevel()
            create_window.title("Create Entry")

            create_window.grab_set()

            entries = []
            employee_names = fetch_employee_names()
            for i, col in enumerate(columns):
                if col.endswith('_id') or col == 'ID' or col == 'last_updated' or col == 'QR Code':
                    #Skip columns that are not needed for input
                    continue
                label = tk.Label(create_window, text=col)
                label.grid(row=i, column=0, padx=10, pady=5)

                if col == 'Assigned to':
                    entry_var = StringVar()
                    entry = AutocompleteCombobox(create_window, textvariable=entry_var)
                    entry.set_completion_list(employee_names)
                elif col == 'Department':
                    entry_var = StringVar()
                    entry = ttk.Combobox(create_window, textvariable=entry_var, values=departments, state='readonly')
                elif col == 'Category':
                    categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
                    entry_var = StringVar()
                    entry = ttk.Combobox(create_window, textvariable=entry_var, values=categories, state='readonly')
                else:
                    entry = tk.Entry(create_window)
                entry.focus_set()
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries.append((col, entry))

            def save_entry():
                try:
                    # Fetch the maximum ID and increment it
                    id_column = next(col for col in columns if col.endswith('_id') or col == 'ID')
                    cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
                    max_id = cursor.fetchone()[0]
                    if table == 'items':
                        if max_id:
                            max_id_num = int(max_id.split('-')[1])
                            new_id_num = max_id_num + 1
                            new_id = f"MLQU-{new_id_num:07d}"
                        else:
                            new_id = "MLQU-0000001"
                    else:
                        if max_id:
                            new_id = int(max_id) + 1
                        else:
                            new_id = 1

                    # Get the current date and time
                    current_datetime = datetime.datetime.now()

                    # Map alias names back to actual column names
                    actual_columns = [col if col not in alias_map else alias_map[col] for col in columns]
                    values = [new_id]

                    for col, entry in entries:
                        value = entry.get()
                        if col == 'Assigned to':
                            # Fetch the employee_id from the employees table
                            cursor.execute("SELECT employee_id FROM employees WHERE name = %s", (value,))
                            employee_id = cursor.fetchone()[0]
                            values.append(employee_id)
                        else:
                            values.append(value)

                    values.append(current_datetime)
                    actual_columns = [col for col in actual_columns if col not in ['QR Code']]
                    insert_query = f"INSERT INTO {table} (" + ", ".join(actual_columns) + ") VALUES (" + ", ".join(["%s"] * len(actual_columns)) + ")"
                    cursor.execute(insert_query, values)
                    self.db.commit()
                    refresh_table()
                    create_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", str(err))
                    return
                except mysql.connector.errors.IntegrityError as err:
                    messagebox.showerror("Employee does not exist!", str(err))
                    return

            save_button = ttk.Button(create_window, text="Save", command=save_entry)
            save_button.grid(row=len(columns), column=0, columnspan=2, pady=10)

            create_window.mainloop()

        def update():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "No item selected")
                return

            item_values = tree.item(selected_item, "values")
            update_window = tk.Toplevel()
            update_window.title("Update Entry")

            update_window.grab_set()

            entries = []
            employee_names = fetch_employee_names()
            for i, col in enumerate(columns):
                if col.endswith('_id') or col == 'ID' or col == 'last_updated' or col == 'QR Code':
                #Skip columns that are not needed for input
                    continue
                label = tk.Label(update_window, text=col)
                label.grid(row=i, column=0, padx=10, pady=5)
                if col == 'Assigned to':
                    entry_var = StringVar()
                    entry = AutocompleteCombobox(update_window, textvariable=entry_var)
                    entry.set_completion_list(employee_names)
                    entry.set(item_values[i])
                elif col == 'Department':
                    entry_var = StringVar()
                    entry = ttk.Combobox(update_window, textvariable=entry_var, values=departments, state='readonly')
                    entry.set(item_values[i])
                elif col == 'Category':
                    entry_var = StringVar()
                    entry = ttk.Combobox(update_window, textvariable=entry_var, values=categories, state='readonly')
                    entry.set(item_values[i])
                else:
                    entry = tk.Entry(update_window)
                entry.insert(0, item_values[i])
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries.append((col, entry))

            def save_changes():
                try:
                    # Get the current date and time
                    current_datetime = datetime.datetime.now()

                    # Map alias names back to actual column names
                    actual_columns = [col if col not in alias_map else alias_map[col] for col in columns]
                    # Prepare the values to be updated
                    new_values = []

                    for col, entry in entries:
                        value = entry.get()
                        if col == 'Assigned to':
                            # Fetch the employee_id from the employees table
                            cursor.execute("SELECT employee_id FROM employees WHERE name = %s", (value,))
                            employee_id = cursor.fetchone()[0]
                            new_values.append(employee_id)
                        else:
                            new_values.append(value)

                    new_values.append(current_datetime)
                    actual_columns = [col for col in actual_columns if col not in ['QR Code']]
                    update_query = f"UPDATE {table} SET " + ", ".join([f"`{col}` = %s" for col in actual_columns if not col.endswith('_id') and col != 'last_updated']) + ", `last_updated` = %s WHERE " + " AND ".join([f"`{col}` = %s" for col in actual_columns if col.endswith('_id')])
                    cursor.execute(update_query, new_values + [item_values[i] for i, col in enumerate(columns) if col.endswith('_id')])
                    self.db.commit()
                    refresh_table()
                    update_window.destroy()

                except TypeError:
                    messagebox.showerror("Error", "Please enter a valid value.")
                    return
                except mysql.connector.errors.IntegrityError as err:
                    messagebox.showerror("Employee does not exist!", str(err))
                    return
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", str(err))
                    return

            save_button = ttk.Button(update_window, text="Save", command=save_changes)
            save_button.grid(row=len(columns), column=0, columnspan=2, pady=10)

            update_window.mainloop()

        def delete():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "No item selected")
                return
            
            item_values = tree.item(selected_item, "values")
            if table == 'employees':
                employee_id = item_values[0]
                confirm = messagebox.askyesno("Confirm Delete", "Deleting this employee will set the employee column of all associated items to NULL. Do you want to proceed?")
                if confirm:
                    try:
                        # Set the employee column to NULL for associated items
                        update_query = "UPDATE items SET employee = NULL WHERE employee = %s"
                        cursor.execute(update_query, (employee_id,))
                        self.db.commit()

                        # Delete the employee
                        delete_query = f"DELETE FROM {table} WHERE " + " AND ".join([f"{col} = %s" for col in columns if col.endswith('_id')])
                        cursor.execute(delete_query, [item_values[i] for i, col in enumerate(columns) if col.endswith('_id')])
                        self.db.commit()
                        refresh_table()

                        for i in tree.get_children():
                            tree.delete(i)
                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        for row in rows:
                            tree.insert("", tk.END, values=row)
                    except mysql.connector.Error as err:
                        messagebox.showerror("Error", str(err))
                        return
            else:
                try:
                    delete_query = f"DELETE FROM {table} WHERE " + " AND ".join([f"{col} = %s" for col in columns if col.endswith('_id')])
                    cursor.execute(delete_query, [item_values[i] for i, col in enumerate(columns) if col.endswith('_id')])
                    self.db.commit()

                    for i in tree.get_children():
                        tree.delete(i)
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    for row in rows:
                        tree.insert("", tk.END, values=row)
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", str(err))
                    return


        try:

            if table == 'items':
                query = f"""
                SELECT items.item_id, serial_number AS 'Serial Number', items.item_name AS 'Item Name', 
                items.category AS Category, items.description AS Description, 
                employees.name AS 'Assigned to', items.department AS Department, items.last_updated
                FROM items
                LEFT JOIN employees ON items.employee = employees.employee_id
                """

                alias_map = {
                    'item_id': 'item_id',
                    'Serial Number': 'serial_number',
                    'Item Name': 'item_name',
                    'Category': 'category',
                    'Description': 'description',
                    'Assigned to': 'employee',
                    'Department': 'department',
                    'last_updated': 'last_updated'
                }
            else:
                query = f"SELECT * FROM {table}"
                alias_map = {}

            cursor.execute(query)

            rows = cursor.fetchall()

            
            configure_styles()
            table_window = tk.Toplevel()
            table_window.state('zoomed')
            table_window.title(f"Table: {table}")
            columns = [desc[0] for desc in cursor.description]

            self.root.withdraw()


            table_window.title(f"Table: {table}")

            # Create a frame for the search bar
            search_frame = ttk.Frame(table_window)
            search_frame.pack(fill='x', padx=10, pady=10)

            # Add a search bar
            search_label = ttk.Label(search_frame, text="Search:")
            search_label.pack(side='left', padx=(0, 5))
            search_var = StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=search_var)
            search_entry.pack(side='left', fill='x', expand=True)



            # Add a clear button to the search bar
            clear_button = ttk.Button(search_frame, text='X', command=lambda: clear_search())
            clear_button.place(in_=search_entry, relx=1.0, rely=0.5, anchor="e")
            clear_button.place_forget()

            def clear_search():
                search_var.set("")
                search()

            def update_clear_button(*args):
                if search_var.get():
                    clear_button.place(in_=search_entry, relx=1.0, rely=0.5, anchor="e")
                else:
                    clear_button.place_forget()

            search_var.trace_add("write", update_clear_button)

            
            # Create a Treeview to display the rows
            tree = ttk.Treeview(table_window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
                tree.column(col, width=100, anchor='center')

            def sort_column(tree, col, reverse):
                try:
                    # Add the column heading to the search bar
                    search_var.set(f"{col}: ")
                    search_entry.icursor(len(search_var.get()))  # Move cursor to the end of the text
                    search_entry.focus_set()


                    data_list = [(tree.set(child, col), child) for child in tree.get_children('')]
                    data_list.sort(reverse=reverse, key=lambda x: (float(x[0]) if x[0].replace('.', '', 1).isdigit() else x[0].lower()))
                    for index, (val, child) in enumerate(data_list):
                        tree.move(child, '', index)
                    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))
                except TypeError:
                    pass


            def validate_search_entry(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
                # Allow deletion of the entire text
                if action == '1' and index == '0' and text == '':
                    return True
                # Prevent editing the column heading part
                if action == '1' and index != '0' and search_var.get().startswith(f"{search_var.get().split(': ')[0]}: "):
                    # Allow modifications after the column heading
                    col_heading = f"{search_var.get().split(': ')[0]}: "
                    if value_if_allowed.startswith(col_heading):
                        return True
                    return False
                return True

            validate_command = search_entry.register(validate_search_entry)
            search_entry.config(validate="key", validatecommand=(validate_command, '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))

            def search(event=None):
                search_text = search_var.get()
                if ": " in search_text:
                    col, val = search_text.split(": ", 1)
                    for item in tree.get_children():
                        tree.delete(item)
                    for row in rows:
                        if col in columns and val.lower() in str(row[columns.index(col)]).lower():
                            tree.insert("", tk.END, values=row)
                else:
                    # If the search bar is empty, display all rows
                    for item in tree.get_children():
                        tree.delete(item)
                    for row in rows:
                        tree.insert("", tk.END, values=row)

            search_entry.bind("<KeyRelease>", search)
            
            qr_images = {}
            for row in rows:
                # Generate QR code for the row
                # Include item_id, serial_number, item_name, assigned_to, department in the QR code
                qr_data = f"{row[0]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}"
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)

                # Create QR code image with transparent background
                img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

                    # Make the white background transparent
                datas = img.getdata()
                new_data = []
                for item in datas:
                    if item[:3] == (255, 255, 255):
                        new_data.append((255, 255, 255, 0))  # Change all white (also consider shades of whites)
                    else:
                        new_data.append(item)
                img.putdata(new_data)

                qr_file = f"qr_{row[0]}.png"
                img.save(qr_file)
                qr_image = ImageTk.PhotoImage(img)
                qr_images[row[0]] = qr_image  # Store the image reference to prevent garbage collection
                tree.insert("", tk.END, values=row)

            if self.accountType == "Admin":
                button_frame = ttk.Frame(table_window)
                button_frame.pack(pady=10)
                create_button = ttk.Button(button_frame, text="Create Entry", command=create)
                create_button.grid(row=0, column=0, padx=5)
                update_button = ttk.Button(button_frame, text="Update Entry", command=update)
                update_button.grid(row=0, column=1, padx=5)
                delete_button = ttk.Button(button_frame, text="Delete Entry", command=delete)
                delete_button.grid(row=0, column=2, padx=5)

            # Add a scrollbar to the Treeview
            tree_scroll = ttk.Scrollbar(table_window, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=tree_scroll.set)
            tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(expand=True, fill='both')

            tree.pack(expand=True, fill='both')

            convertbtn_frame = ttk.Frame(table_window)
            convertbtn_frame.pack(pady=10)
            pdf_button = ttk.Button(convertbtn_frame, text="Convert to PDF", command=lambda: convert_to_pdf(table, tree, columns))
            pdf_button.grid(row=0, column=0, padx=5)
            excel_button = ttk.Button(convertbtn_frame, text="Convert to Excel", command=lambda: convert_to_excel(table, rows, columns))
            excel_button.grid(row=0, column=1, padx=5)
            if table == 'items':
                qr_button = ttk.Button(convertbtn_frame, text="Generate QR PDF", command=lambda: generate_qr_pdf(table, tree))
                qr_button.grid(row=0, column=2, padx=5)

            back_button = ttk.Button(convertbtn_frame, text="Back", command=lambda: back_to_main(table_window))
            back_button.grid(row=1, column=0, columnspan=3, pady=10)

            table_window.protocol("WM_DELETE_WINDOW", lambda: close_application(table_window))
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))
            return
        
        def back_to_main(table_window):
            table_window.destroy()
            self.root.deiconify()
            self.root.state('zoomed')

        def close_application(table_window):
            table_window.destroy()
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = Login(root)
    root.mainloop()