import logging
import os
import random
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from threading import ExceptHookArgs, Thread
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any, Callable

import pandas as pd

import src.utils as utils
from src.config import GuiConfig, OutputFormat
from src.gui.widget_loghandler import LogToWidgetHandler
from src.gui.widgets.url_frame import UrlWidget


class FormatSelectionWidget(ttk.LabelFrame):
    def __init__(
        self,
        parent: ttk.Frame,
        label_text: str,
        output_format: tk.StringVar,
    ):
        super().__init__(
            parent,
            text=label_text,
        )

        for i, format in enumerate(OutputFormat):
            # Create radio button
            format_radiobutton = ttk.Radiobutton(
                self,
                text=format.value,
                variable=output_format,
                value=format.value,
            )
            format_radiobutton.grid(row=0, column=i, padx=10, pady=5, sticky="we")
