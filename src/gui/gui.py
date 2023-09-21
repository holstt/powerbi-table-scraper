import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

import pandas as pd

import src.utils as utils
from src.config import GuiConfig
from src.gui.gui_state import UiState
from src.gui.widgets.main_widget import MainWidget, UiSubmitArgs

logger = logging.getLogger(__name__)


WIDTH = 600
HEIGHT = 500
THEME_NAME = "forest-light"
THEME_PATH = f"./src/gui/theme/{THEME_NAME}.tcl"


class ScraperGui(tk.Tk):
    def __init__(
        self,
        config: GuiConfig,
        on_run_scrape: Callable[[UiSubmitArgs, Callable[[pd.DataFrame], None]], None],
    ):
        super().__init__()
        self.lang = utils.load_language(config.language)
        self.config = config
        self.on_run_scrape = on_run_scrape

        self.title(config.program_name)
        self.minsize(WIDTH, HEIGHT)
        self._load_theme()
        self.state = self._init_state(config)

        main_frame = MainWidget(
            self, self.lang, self.state, config.program_name, on_run_scrape
        )
        main_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

        self._center_window()

    def show(self):
        try:
            self.mainloop()
        except Exception as e:
            self._show_error(e)

    # Init UI state variables
    # XXX: Move to state ctor?
    def _init_state(self, config: GuiConfig) -> UiState:
        url = (
            config.default_values.url.unicode_string()
            if config.default_values.url
            else ""
        )
        output_path = (
            self.lang["placeholder_save_to_path"]
            if config.default_values.output_path is None
            else config.default_values.output_path.resolve().as_posix()
        )

        return UiState(
            url=url,
            is_headless=config.default_values.is_headless,
            output_path=output_path,
            is_processing=False,
            output_format=config.default_values.output_format,
            lang=self.lang,
        )

    def _load_theme(self):
        self.tk.call("source", THEME_PATH)
        style = ttk.Style(self)
        style.theme_use(THEME_NAME)

    def _center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate Starting X and Y coordinates for Window
        x = (screen_width / 2) - (WIDTH / 2)
        y = (screen_height / 2) - (HEIGHT / 2)

        self.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))

    # Show a message box with the exception message
    def _show_error(self, exception: Exception):
        error_message = (
            f"An error occurred, please see the program log for details.\n\nError message: "
            + str(exception)
        )

        messagebox.showerror("Error", error_message)  # type: ignore
