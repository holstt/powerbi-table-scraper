import logging
import os
import random
import threading
import time
import tkinter as tk
import traceback
from dataclasses import dataclass
from pathlib import Path
from threading import ExceptHookArgs, Thread
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any, Callable

import pandas as pd
from typing_extensions import override

import src.utils as utils
from src.config import GuiConfig, OutputFormat

logger = logging.getLogger(__name__)


# Writes the log to the given text widget
class LogToWidgetHandler(logging.Handler):
    def __init__(self, widget: tk.Text):
        logging.Handler.__init__(self)
        self.text_widget = widget

    @override
    def emit(self, record: logging.LogRecord):
        # Enable editing of the text widget in order to insert the log
        self.text_widget.configure(state=tk.NORMAL)

        if record.exc_info:
            # Format exception
            exc_type, exc_value, exc_traceback = record.exc_info
            exc_str = "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )
            # Insert exception
            self.text_widget.insert(tk.END, exc_str + "\n")

        else:
            self.text_widget.insert(tk.END, str(record.msg) + "\n")

        self.text_widget.configure(state=tk.DISABLED)
        self.text_widget.see(tk.END)  # Scroll to the bottom of the text widget


class UiState:
    def __init__(self, url: str, is_headless: bool, output_path: str, is_working: bool):
        self.url = tk.StringVar(value=url)
        self.is_headless = tk.BooleanVar(value=is_headless)
        self.output_path = tk.StringVar(value=output_path)
        self.is_working = tk.BooleanVar(value=is_working)


@dataclass(frozen=True)
class UiSubmitArgs:
    url: str
    is_headless: bool
    output_path: Path
    output_format: OutputFormat


WIDTH = 600
HEIGHT = 500
THEME_NAME = "forest-light"
THEME_PATH = f"./src/gui/theme/{THEME_NAME}.tcl"


class ScraperGui:
    def __init__(
        self,
        config: GuiConfig,
        on_run_scrape: Callable[[UiSubmitArgs, Callable[[pd.DataFrame], None]], None],
    ):
        self.lang = utils.load_language(config.language)
        self.config = config
        self.on_run_scrape = on_run_scrape
        self.root = tk.Tk()
        self.root.title(config.program_name)
        self.root.minsize(WIDTH, HEIGHT)

        # Load theme
        style = ttk.Style(self.root)
        self.root.tk.call("source", THEME_PATH)
        style.theme_use(THEME_NAME)

        # Init UI state variables
        self.state = UiState(
            url=config.default_values.url.unicode_string()
            if config.default_values.url
            else "",
            is_headless=config.default_values.is_headless,
            output_path=self.lang["placeholder_save_to_path"]
            if config.default_values.output_path is None
            else config.default_values.output_path.absolute().as_posix(),
            is_working=False,
        )

        # Widget setup
        main_frame = self.create_main_frame(self.root)
        self.title_label = self.create_title(main_frame)
        self.url_frame, self.url_label, self.url_entry = self.create_url_frame(
            main_frame
        )
        (
            self.path_frame,
            self.path_label,
            self.path_entry,
            self.path_browse_button,
        ) = self.create_path_frame(main_frame)
        self.headless_checkbox = self._create_headless_checkbox(main_frame)
        self.log_frame = self._create_log_frame(main_frame)
        self.run_button = self._create_run_button(main_frame)

        # Bind variable changes to widget updates
        self.state.is_working.trace_add("write", self._on_working_changed)
        self.state.url.trace_add("write", self._on_submit_args_changed)
        self.state.output_path.trace_add("write", self._on_submit_args_changed)

        # Center the window
        self._center_window()

        # Set colors (debug)
        # self.set_widget_colors(self.root)

        # self.root.configure(background="green")
        # main_frame.configure(background="red")
        # title_label.configure(background="blue")
        # url_label.configure(background="yellow")
        # url_entry.configure(background="purple")
        # url_frame.configure(background="cyan")

    def _create_log_frame(self, main_frame: ttk.Frame):
        log_frame = ttk.Frame(
            main_frame,
        )
        # Label
        log_label = ttk.Label(log_frame, text=self.lang["label_program_log"] + ":")
        log_label.pack(anchor="w", pady=(0, 5))

        # Border: Use entry to get themed border as no Text ttk widget exists
        log_border = ttk.Entry(log_frame, state="readonly")
        log_border.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)

        # Text with scrollbar and no border
        log_text = ScrolledText(
            log_border,
            state=tk.DISABLED,
            border=0,
            wrap="word",
            height=10,  # XXX Setting height will cause widget to expand (fill) correctly without pushing widgets below it out of frame. Not sure why
        )
        log_text.pack(padx=5, pady=5, anchor=tk.CENTER, fill=tk.BOTH, expand=True)

        log_frame.pack(pady=10, anchor=tk.CENTER, fill=tk.BOTH, expand=True)

        # Connect to root logger
        root_logger = logging.getLogger()
        handler = LogToWidgetHandler(log_text)
        root_logger.addHandler(handler)

    def _center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate Starting X and Y coordinates for Window
        x = (screen_width / 2) - (WIDTH / 2)
        y = (screen_height / 2) - (HEIGHT / 2)

        self.root.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))

    def _is_input_valid(self) -> bool:
        return (
            not self.state.url.get().strip() == ""
            and not self.state.output_path.get().strip() == ""
            and not self.state.output_path.get()
            == self.lang["placeholder_save_to_path"]
        )

    def _on_submit_args_changed(self, *args: Any):
        # Enable run button if input is valid
        self.run_button.configure(
            state=tk.NORMAL if self._is_input_valid() else tk.DISABLED
        )

    def show(self):
        try:
            self.root.mainloop()
        except Exception as e:
            self._show_error(e)

    def create_main_frame(self, root: tk.Tk) -> ttk.Frame:
        main_frame = ttk.Frame(root)
        main_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        return main_frame

    def create_title(self, main_frame: ttk.Frame) -> ttk.Label:
        title_label = ttk.Label(
            main_frame,
            text=self.config.program_name,
            font=("Arial", 16),
        )
        title_label.pack(pady=10, anchor="center")
        return title_label

    def create_url_frame(self, main_frame: ttk.Frame):
        url_frame = ttk.Frame(main_frame)
        url_label = ttk.Label(url_frame, text=self.lang["label_url"] + ":", anchor="w")
        url_entry = ttk.Entry(url_frame, textvariable=self.state.url)

        url_label.grid(row=0, column=0, sticky="w", padx=0)
        url_entry.grid(
            row=0, column=1, padx=(5, 0), sticky="we"
        )  # Fill the entry horizontally
        url_frame.columnconfigure(1, weight=1)  # Let col 1 stretch to fill the frame
        url_frame.pack(pady=10, fill=tk.X)
        return url_frame, url_label, url_entry

    def create_path_frame(self, main_frame: ttk.Frame):
        path_frame = ttk.Frame(main_frame)
        path_label = ttk.Label(
            path_frame, text=self.lang["label_save_to_path"] + ":", anchor="w"
        )

        # Make a readonly entry
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.state.output_path,
            state="readonly",
        )

        path_browse_button = ttk.Button(
            path_frame,
            text=self.lang["button_browse"],
            command=self._browse_file_location,
        )
        # Configure grid layout
        path_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        path_entry.grid(row=0, column=1, padx=0, sticky="we")
        path_browse_button.grid(row=0, column=2, padx=(5, 0), sticky="we")
        path_frame.columnconfigure(1, weight=1)  # Let col 1 stretch to fill the frame
        path_frame.pack(pady=10, fill=tk.X)

        return path_frame, path_label, path_entry, path_browse_button

    def _create_headless_checkbox(self, main_frame: ttk.Frame):
        headless_checkbox = ttk.Checkbutton(
            main_frame,
            text=self.lang["label_run_headless"],
            variable=self.state.is_headless,
        )
        headless_checkbox.pack(pady=5, anchor="w")
        return headless_checkbox

    # This will be executed in the background thread i.e. raise exception in this method will not be caught by the main thread
    def on_thread_exception(self, args: ExceptHookArgs):
        self.state.is_working.set(False)
        logger.exception(args.exc_value)
        self._show_error(args.exc_value)  # type: ignore

    def _create_run_button(self, frame: ttk.Frame) -> ttk.Button:
        def on_run_button_click() -> None:
            logger.debug("Run button clicked. Starting scrape in a separate thread...")
            self.state.is_working.set(True)

            # Run the scrape process in a separate thread to keep the UI responsive

            thread = Thread(
                target=self.on_run_scrape,
                args=(
                    UiSubmitArgs(
                        url=self.state.url.get(),
                        is_headless=self.state.is_headless.get(),
                        output_path=Path(self.state.output_path.get()),
                        output_format=OutputFormat.EXCEL,  # XXX: Always excel for now
                    ),
                    self.on_scrape_complete,
                ),
                daemon=True,  # Kill the thread when the program exits
            )
            threading.excepthook = self.on_thread_exception
            thread.start()

        # Run button
        run_button = ttk.Button(
            frame,
            text=self.lang["button_run"],
            width=20,
            command=on_run_button_click,
            state=(tk.NORMAL if self._is_input_valid() else tk.DISABLED),
            style="Accent.TButton",
        )
        run_button.pack(pady=10, anchor="center")
        return run_button

    # Open a file dialog to select a file location
    def _browse_file_location(self, *args: Any):
        logger.debug("Opening file dialog to select a file location")
        filepath_str = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if filepath_str:
            self.state.output_path.set(filepath_str)

    def random_color(self) -> str:
        """Generate a random hex color."""
        return "#{:02x}{:02x}{:02x}".format(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

    def set_widget_colors(self, parent: Any) -> None:
        """Recursively set a random background color for every widget."""
        for child in parent.winfo_children():
            try:
                child.configure(bg=self.random_color())
            except tk.TclError:
                # Some widgets might not support the 'bg' option, so we pass in case of error
                pass
            self.set_widget_colors(child)  # Recursive call to handle child's children

    # def set_widget_highlight(parent):
    #     """Recursively set a random highlight background and border for every widget."""
    #     for child in parent.winfo_children():
    #         try:
    #             color = random_color()
    #             child.configure(highlightbackground=color, highlightthickness=2)
    #         except tk.TclError:
    #             pass
    #         set_widget_highlight(child)  # Recursive call

    def on_scrape_complete(self, table: pd.DataFrame):
        logger.debug("Showing scrape complete dialog")
        self.state.is_working.set(False)
        self._show_scrape_complete_dialog(table)

    # Show a message box when scraping is complete
    def _show_scrape_complete_dialog(self, table: pd.DataFrame):
        # Play a beep sound
        self.root.bell()

        response = messagebox.askyesno(  # type: ignore
            self.lang["title_task_complete"],
            self.lang["message_task_complete"].format(
                rows_scraped=len(table), columns_scraped=len(table.columns)
            ),
        )
        if response:
            # Open file directory
            file_path = Path(self.state.output_path.get())
            os.startfile(file_path.parent.absolute())

    # Show a message box with the exception message
    def _show_error(self, exception: Exception):
        error_message = (
            f"An error occurred, please see the program log for details.\n\nError message: "
            + str(exception)
        )

        messagebox.showerror("Error", error_message)  # type: ignore

    # Updates the widgets when working (we cant bind state variables directly to widget states, it seems?)
    def _on_working_changed(self, *args: Any):
        status = tk.DISABLED if self.state.is_working.get() else tk.NORMAL
        logger.debug(f"Setting widgets to status: {status}")
        self.url_entry.configure(state=status)
        # self.path_entry.configure(state=status)
        self.path_browse_button.configure(state=status)
        self.headless_checkbox.configure(state=status)
        self.run_button.configure(state=status)

        if self.state.is_working.get():
            # self.path_entry.configure(text=self.state.output_path.get(), fg="black")
            self.run_button.configure(text=self.lang["button_processing"])
        else:
            # self.path_entry.configure(
            #     text=self.lang["placeholder_save_to_path"], fg="grey"
            # )
            self.run_button.configure(text=self.lang["button_run"])
