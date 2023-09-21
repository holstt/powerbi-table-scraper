import tkinter as tk
from tkinter import BooleanVar, StringVar, ttk
from typing import Callable
from xmlrpc.client import Boolean

import src.gui.gui_utils as gui_utils


class RunButton(ttk.Button):
    def __init__(
        self,
        parent: ttk.Frame,
        lang: dict[str, str],
        is_enabled: tk.BooleanVar,
        is_processing: tk.BooleanVar,
        on_click: Callable[[], None],
    ):
        def get_button_text():
            if is_processing.get():
                return lang["button_processing"]
            else:
                return lang["button_run"]

        super().__init__(
            parent,
            text=get_button_text(),
            state=gui_utils.bool_to_state(is_enabled),
            style="Accent.TButton",
            command=on_click,
            width=20,
        )

        # Bind events
        is_enabled.trace_add(
            "write",
            lambda *_: self.configure(  # type: ignore
                state=gui_utils.bool_to_state(is_enabled)
            ),
        )
        # Get is processing depending of processing state
        is_processing.trace_add(
            "write",
            lambda *_: self.configure(text=get_button_text()),  # type: ignore
        )
