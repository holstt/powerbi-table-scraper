import logging
import os
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from threading import ExceptHookArgs, Thread
from tkinter import messagebox, ttk
from typing import Any, Callable

import pandas as pd

import src.gui.gui_utils as gui_utils
from src.config import OutputFormat
from src.gui.gui_state import UiState
from src.gui.widgets.format_widget import FormatSelectionWidget
from src.gui.widgets.log_widget import LogWidget
from src.gui.widgets.path_widget import PathWidget
from src.gui.widgets.run_button import RunButton
from src.gui.widgets.url_frame import UrlWidget

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UiSubmitArgs:
    url: str
    is_headless: bool
    output_path: Path
    output_format: OutputFormat


class MainWidget(ttk.Frame):
    def __init__(
        self,
        root: tk.Tk,
        lang: dict[str, str],
        state: UiState,
        program_name: str,
        on_run_scrape: Callable[[UiSubmitArgs, Callable[[pd.DataFrame], None]], None],
    ):
        super().__init__(root)
        self.lang = lang
        self.ui_state = state
        self._on_run_scrape = on_run_scrape

        title_label = ttk.Label(
            self,
            text=program_name,
            font=("Arial", 16),
        )

        url_widget = UrlWidget(
            self,
            self.lang["label_url"] + ":",
            self.ui_state.url_input,
        )

        format_selection_widget = FormatSelectionWidget(
            self,
            self.lang["label_output_format"],
            self.ui_state.output_format_input,
        )

        path_widget = PathWidget(
            self,
            self.lang,
            self.ui_state.output_path_input,
            self.ui_state.output_format_input,
        )

        headless_checkbox = ttk.Checkbutton(
            self,
            text=self.lang["label_run_headless"],
            variable=self.ui_state.is_headless_input,
        )

        log_widget = LogWidget(self, self.lang["label_program_log"] + ":")

        run_button = RunButton(
            self,
            self.lang,
            is_enabled=self.ui_state.is_input_valid,
            is_processing=self.ui_state.is_processing,
            on_click=self.on_run_button_click,
        )

        # Create layout
        title_label.grid(row=0, column=0, pady=10)
        url_widget.grid(row=1, column=0, pady=10, sticky="we")
        format_selection_widget.grid(row=2, column=0, pady=10, sticky="we")
        path_widget.grid(row=3, column=0, pady=10, sticky="we")
        headless_checkbox.grid(row=4, column=0, pady=5, sticky="w")
        log_widget.grid(row=5, column=0, pady=10, sticky="nsew")
        run_button.grid(row=6, column=0, pady=10)

        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)

        # Bind variable changes to widget updates
        self.ui_state.is_processing.trace_add("write", self._on_processing_changed)

    def on_run_button_click(self) -> None:
        logger.debug("Run button clicked. Starting scrape in a separate thread...")
        self.ui_state.is_processing.set(True)

        # Run the scrape process in a separate thread to keep the UI responsive
        thread = Thread(
            target=self._on_run_scrape,
            args=(
                UiSubmitArgs(
                    url=self.ui_state.url_input.get(),
                    is_headless=self.ui_state.is_headless_input.get(),
                    output_path=Path(self.ui_state.output_path_input.get()),
                    output_format=OutputFormat(self.ui_state.output_format_input.get()),
                ),
                self.on_scrape_complete,
            ),
            daemon=True,  # Kill the thread when the program exits
        )
        threading.excepthook = self.on_thread_exception
        thread.start()

    # This will be executed in the background thread i.e. raise exception in this method will not be caught by the main thread
    def on_thread_exception(self, args: ExceptHookArgs):
        self.ui_state.is_processing.set(False)
        logger.exception(args.exc_value)
        self._show_error(args.exc_value)  # type: ignore

    def on_scrape_complete(self, table: pd.DataFrame):
        logger.debug("Showing scrape complete dialog")
        self.ui_state.is_processing.set(False)
        self._show_scrape_complete_dialog(table)

    # Show a message box when scraping is complete
    def _show_scrape_complete_dialog(self, table: pd.DataFrame):
        # Play a beep sound
        self.bell()

        response = messagebox.askyesno(  # type: ignore
            self.lang["title_task_complete"],
            self.lang["message_task_complete"].format(
                rows_scraped=len(table), columns_scraped=len(table.columns)
            ),
        )
        if response:
            # Open file directory
            file_path = Path(self.ui_state.output_path_input.get())
            os.startfile(file_path.parent.absolute())

    # Update all widgets to reflect the current processing state
    def _on_processing_changed(self, *args: Any):
        status = tk.DISABLED if self.ui_state.is_processing.get() else tk.NORMAL
        logger.debug(f"Setting widgets to status: {status}")
        # Recursively apply status to all widgets
        # Exclude all widgets that should not change status/manages its own status
        gui_utils.set_widget_state_recursive(self, status, exclude=[LogWidget])
