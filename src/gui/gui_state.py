import tkinter as tk

from src.config import OutputFormat


class UiState:
    def __init__(
        self,
        url: str,
        is_headless: bool,
        output_path: str,
        is_processing: bool,
        output_format: OutputFormat,
        lang: dict[str, str],  # XXX: Find better solution
    ):
        self.lang = lang
        # Create state variables that UI can bind/subscribe to

        # Selected values/inputs
        self.url_input = tk.StringVar(value=url)
        self.is_headless_input = tk.BooleanVar(value=is_headless)
        self.output_path_input = tk.StringVar(value=output_path)
        self.output_format_input = tk.StringVar(value=output_format.value)

        # Other state variables
        self.is_processing = tk.BooleanVar(value=is_processing)

        # DERIVED STATE VARIABLES
        # Validate when input changes
        self.is_input_valid = tk.BooleanVar(value=self._is_input_valid())
        self.output_path_input.trace_add("write", lambda *_: self.is_input_valid.set(self._is_input_valid()))  # type: ignore
        self.url_input.trace_add("write", lambda *_: self.is_input_valid.set(self._is_input_valid()))  # type: ignore

        self.is_view_enabled = tk.BooleanVar(value=not is_processing)

        # Disable view when processing
        self.is_processing.trace_add("write", lambda *_: self.is_view_enabled.set(not self.is_processing.get()))  # type: ignore

    # Validate input
    def _is_input_valid(self) -> bool:
        is_url_valid = not self.url_input.get().strip() == ""
        is_output_path_valid = (
            not self.output_path_input.get().strip() == ""
            and not self.output_path_input.get()
            == self.lang["placeholder_save_to_path"]
        )

        return is_url_valid and is_output_path_valid
