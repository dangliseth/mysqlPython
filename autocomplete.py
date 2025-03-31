import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self._handle_keyrelease)
        self['values'] = self._completion_list

    def set(self, value):
        if value in self._completion_list:
            self.delete(0, tk.END)
            self.insert(0, value)
            self.icursor(tk.END)
        else:
            print(f"Warning: '{value}' not found in completion list.")
            self.delete(0, tk.END)

    def _autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())

        user_input = self.get().lower()
        _hits = [item for item in self._completion_list if item.lower().startswith(user_input)]

        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits

        if _hits:
            self._hit_index = (self._hit_index + delta) % len(_hits)
            self.delete(0, tk.END)
            self.insert(0, _hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def _handle_keyrelease(self, event):
        if event.state & 0x4 and event.keysym == 'a':  # Check if Ctrl is pressed and 'a' is the key
            self.select_range(0, tk.END)
            return "break"

        if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down'):
            return

        if event.keysym == 'Return' or event.keysym == 'Tab':
            self._autocomplete()
        else:
            self.position = self.index(tk.END)
            user_input = self.get().lower()
            self._hits = [item for item in self._completion_list if item.lower().startswith(user_input)]
            # Update the values for the dropdown but do not show it automatically
            if self._hits:
                self.delete(0, tk.END)
                self.insert(0, self._hits[0])
                self.select_range(len(user_input), tk.END)
                self['values'] = self._hits
        if event.keysym == 'Up':
            self._autocomplete(-1)
        elif event.keysym == 'Down':
            self._autocomplete(1)

        self.icursor(self.index(tk.END))
        self.focus_set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    messagebox.showwarning('Warning', 'Wrong way to run the module. Run the index.py file instead.')