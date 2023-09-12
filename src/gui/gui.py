import logging
import os
import random
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable

import pandas as pd

import src.utils as utils
from src.config import GuiConfig, OutputFormat

logger = logging.getLogger(__name__)


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
        default_url: str,
        on_run_scrape: Callable[[UiSubmitArgs, Callable[[pd.DataFrame], None]], None],
    ):
        self.lang = utils.load_language(config.language)
        self.config = config
        self.on_run_scrape = on_run_scrape
        self.default_url = default_url
        self.root = tk.Tk()
        self.root.title(config.program_name)
        self.root.minsize(WIDTH, HEIGHT)

        # Load theme
        style = ttk.Style(self.root)
        self.root.tk.call("source", THEME_PATH)
        style.theme_use(THEME_NAME)


        # TODO: Add log stream to program output frame
        # program_output_frame = ttk.LabelFrame(
        #     self.root, text="Program Output", padding=(20, 10)
        # )
        # program_output_frame.grid(
        #     row=1, column=0, padx=(20, 10), pady=10, sticky="nsew"
        # )

        # Init UI state variables
        self.state = UiState(
            url=default_url,
            is_headless=False,
            output_path=self.lang["placeholder_save_to_path"],
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
        self.run_button = self._create_run_button(main_frame)

        # Bind variable changes to widget updates
        self.state.is_working.trace_add("write", self._on_working_changed)
        self.state.url.trace_add("write", self._on_submit_args_changed)
        self.state.output_path.trace_add("write", self._on_submit_args_changed)
        # self.state.output_path.trace_add("write", self._on_output_path_changed)

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

    def _center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate Starting X and Y coordinates for Window
        x = (screen_width / 2) - (WIDTH / 2)
        y = (screen_height / 2) - (HEIGHT / 2)

        self.root.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))

    # def _on_output_path_changed(self, *args: Any):
    #     if self.state.output_path.get() == "":
    #         self.path_entry.configure(text=self.lang["path_placeholder"], fg="grey")
    #     else:
    #         self.path_entry.configure(text=self.state.output_path.get(), fg="black")

    def _on_submit_args_changed(self, *args: Any):
        # Do some basic input validation
        is_input_valid = (
            not self.state.url.get().strip() == ""
            and not self.state.output_path.get()
            == self.lang["placeholder_save_to_path"]
            and not self.state.output_path.get().strip() == ""
        )
        # Enable run button if input is valid
        self.run_button.configure(state="normal" if is_input_valid else "disabled")

    def show(self):
        self.root.mainloop()

    def create_main_frame(self, root: tk.Tk) -> ttk.Frame:
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        MARGIN = 20

        # Create spacers for margins
        ttk.Frame(self.root, width=MARGIN + 10).grid(
            row=0, column=0, sticky="nsew"
        )  # Left spacer
        ttk.Frame(self.root, width=MARGIN + 10).grid(
            row=0, column=2, sticky="nsew"
        )  # Right spacer
        ttk.Frame(self.root, height=MARGIN).grid(
            row=0, column=1, sticky="nsew"
        )  # Top spacer
        ttk.Frame(self.root, height=MARGIN).grid(
            row=2, column=1, sticky="nsew"
        )  # Bottom spacer

        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=1, sticky="nsew")
        main_frame.pack_propagate(
            False
        )  # Prevent widgets from determining the frame's size

        return main_frame

    def create_title(self, main_frame: ttk.Frame) -> ttk.Label:
        title_label = ttk.Label(
            main_frame, text=self.config.program_name, font=("Arial", 16)
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

        # # Make a clickable entry label to select a path
        # path_entry = tk.Label(
        #     path_frame,
        #     relief="sunken",
        #     anchor="w",
        #     fg="grey",
        #     padx=2,
        #     textvariable=self.state.output_path,
        # )

        # # Make label act like a button
        # path_entry.bind("<Button-1>", self._browse_file_location)

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

    def _create_run_button(self, frame: ttk.Frame) -> ttk.Button:
        def on_run_button_click() -> None:
            self.state.is_working.set(True)
            self.on_run_scrape(
                UiSubmitArgs(
                    url=self.state.url.get(),
                    is_headless=self.state.is_headless.get(),
                    output_path=Path(self.state.output_path.get()),
                    output_format=OutputFormat.EXCEL,  # XXX: Always excel for now
                ),
                self.on_scrape_complete,
            )

        # Run button
        run_button = ttk.Button(
            frame,
            text=self.lang["button_run"],
            width=20,
            command=on_run_button_click,
            state="disabled",
            style="Accent.TButton",
        )
        run_button.pack(pady=10, anchor="center")
        return run_button

    # Open a file dialog to select a file location
    def _browse_file_location(self, *args: Any):
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
        messagebox.showerror("Error", str(exception))  # type: ignore

    # Updates the widgets when working (we cant bind state variables directly to widget states, it seems?)
    def _on_working_changed(self, *args: Any):
        status = "disabled" if self.state.is_working.get() else "normal"
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
