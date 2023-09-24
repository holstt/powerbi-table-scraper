import tkinter as tk
from tkinter import ttk

from src.gui.gui_utils import bool_to_state


class UrlWidget(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        label_text: str,
        url: tk.StringVar,
    ):
        super().__init__(
            parent,
        )

        # Create widgets
        self.url_label = ttk.Label(self, text=label_text, anchor="w")
        self.url_entry = ttk.Entry(self, textvariable=url)

        # Create layout
        self.url_label.grid(row=0, column=0, sticky="w", padx=0)
        self.url_entry.grid(
            row=0, column=1, padx=(5, 0), sticky="we"
        )  # Fill the entry horizontally
        self.columnconfigure(
            1, weight=1
        )  # Let url entry (col 1) stretch to fill the frame
