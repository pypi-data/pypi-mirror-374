import tkinter as tk
from tkinter import ttk

class MultiSelectDropdown:
    def __init__(self, parent, choices, button_text="Select graph file(s)", max_height=300, apply_callback = None):
        self.root = parent
        self.choices = choices
        self.max_height = max_height
        self.callback = apply_callback
        # Button to open the popup
        self.button = ttk.Button(parent, text=button_text, command=self.toggle_popup, width=20)
        self.button.pack(padx=10, pady=10)

        # Create popup window
        self.popup = tk.Toplevel(self.root)
        self.popup.withdraw()
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.configure(bd=1, relief=tk.SOLID, background="#f0f0f0")

        # Main frame for popup content
        main_frame = ttk.Frame(self.popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all, width=10).pack(side=tk.LEFT, padx=2)
        self.apply_btn = ttk.Button(button_frame, text="Apply", command=self.on_apply, width=8).pack(side=tk.RIGHT, padx=2)

        # Listbox frame with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, font=('TkDefaultFont', 9), 
                                 relief=tk.FLAT, highlightthickness=1, activestyle='none')
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind('<Double-Button-1>', lambda e: self.on_apply())
        self.listbox.bind('<Return>', lambda e: self.on_apply())
        
        self.refresh_listbox()
        
    def refresh_listbox(self):
        self.listbox.delete(0,tk.END)
        self.all_items = self.choices.copy()
        for item in self.all_items:
            self.listbox.insert(tk.END, item)

    def toggle_popup(self):
        """Toggle popup visibility"""
        if self.popup.winfo_viewable():
            self.popup.withdraw()
        else:
            x = self.button.winfo_rootx()
            y = self.button.winfo_rooty() + self.button.winfo_height()
            width = max(300, self.button.winfo_width() + 50)
            height = min(self.max_height, len(self.choices) * 20 + 120)
            
            self.popup.geometry(f"{width}x{height}+{x}+{y}")
            self.popup.deiconify()
            
    def select_all(self):
        """Select all items in listbox"""
        self.listbox.selection_set(0, tk.END)

    def clear_all(self):
        """Clear all selections"""
        self.listbox.selection_clear(0, tk.END)

    def on_apply(self):
        """Handle apply button click"""
        self.popup.withdraw()
        if self.callback is not None:
            self.callback()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph Selection Demo")
    root.geometry("400x300")
    choices = [f"graph_layer_{i:02d}.csv" for i in range(1, 31)]
    dropdown = MultiSelectDropdown(root, choices, button_text="Select Graph Files")
    info_label = tk.Label(root, text="The dropdown will appear below the button\nwith search, select all, and apply features.", 
                         justify=tk.LEFT, pady=20)
    info_label.pack()
    root.mainloop()