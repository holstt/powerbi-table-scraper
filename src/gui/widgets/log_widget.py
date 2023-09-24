import logging
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from src.gui.widget_loghandler import LogToWidgetHandler


class LogWidget(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        label_text: str,
    ):
        super().__init__(parent)

        # Label
        log_label = ttk.Label(
            self,
            text=label_text,
        )

        # Border: Use entry to get themed border as no Text ttk widget exists
        log_border = ttk.Entry(self, state="readonly")

        # Text with scrollbar and no border
        log_text = ScrolledText(
            self,
            state=tk.DISABLED,
            border=0,
            wrap="word",
        )

        # Layout
        log_label.grid(row=0, column=0, sticky="nw", padx=0, pady=(0, 5))
        log_border.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        log_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Connect widget to output of root logger
        root_logger = logging.getLogger()
        handler = LogToWidgetHandler(log_text)
        root_logger.addHandler(handler)
