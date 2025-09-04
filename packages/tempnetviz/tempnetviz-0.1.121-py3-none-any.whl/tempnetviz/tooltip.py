import tkinter as tk

class ToolTip(object):
    def __init__(self, widget, text='widget info', delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # delay in milliseconds
        self.tipwindow = None
        self._after_id = None  # to store after() id
        self.widget.bind("<Enter>", self.schedule_tip)
        self.widget.bind("<Leave>", self.cancel_tip)

    def schedule_tip(self, event=None):
        # Schedule showing the tooltip after delay
        self._after_id = self.widget.after(self.delay, self.show_tip)

    def cancel_tip(self, event=None):
        # Cancel scheduled tooltip or hide existing one
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self.hide_tip()

    def show_tip(self):
        # Show tooltip only if it doesn't already exist
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert") if self.widget.bbox("insert") else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
