import logging
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any

from src.config import OutputFormat

logger = logging.getLogger(__name__)


class PathWidget(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        lang: dict[str, str],
        path: tk.StringVar,
        output_format: tk.StringVar,
    ):
        super().__init__(
            parent,
        )

        self.path = path
        self.output_format = output_format

        path_label = ttk.Label(self, text=lang["label_save_to_path"] + ":", anchor="w")

        # Make a readonly entry
        entry = ttk.Entry(
            self,
            textvariable=self.path,
            state="readonly",
        )
        # Move cursor to end of entry
        entry.xview_moveto(1)

        browse_button = ttk.Button(
            self,
            text=lang["button_browse"],
            command=self._browse_file_location,
        )
        # Configure grid layout
        path_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        entry.grid(row=0, column=1, padx=0, sticky="we")
        browse_button.grid(row=0, column=2, padx=(5, 0), sticky="we")
        self.columnconfigure(1, weight=1)  # Let col 1 stretch to fill the frame

        # Bind events
        # Move view to end of entry (in case of long path)
        path.trace_add("write", lambda *_: entry.xview_moveto(1))  # type: ignore

    # Open a file dialog to select a file location
    def _browse_file_location(self, *args: Any):
        logger.debug("Opening file dialog to select a file location")

        # Determine default extension and file types based on output format
        match self.output_format.get():
            case OutputFormat.EXCEL.value:
                default_extension = ".xlsx"
                file_types = [("Excel files", "*.xlsx")]
            case OutputFormat.CSV.value:
                default_extension = ".csv"
                file_types = [("CSV files", "*.csv")]
            case _:
                raise ValueError(f"Invalid output format: {self.path.get()}")

        filepath_str = filedialog.asksaveasfilename(
            # initialdir=self.state.output_path.get(), # XXX: Consider using if default path is set
            filetypes=file_types,
            defaultextension=default_extension,
        )
        if filepath_str:
            self.path.set(filepath_str)
