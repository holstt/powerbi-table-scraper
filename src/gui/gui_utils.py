import random
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Literal, Optional


# Show a message box with the exception message
def show_error(exception: Exception):
    error_message = (
        f"An error occurred, please see the program log for details.\n\nError message: "
        + str(exception)
    )

    messagebox.showerror("Error", error_message)  # type: ignore


def bool_to_state(bool: tk.BooleanVar):
    return tk.NORMAL if bool.get() else tk.DISABLED


def set_widget_state_recursive(
    parent: tk.Widget,
    state: Literal["normal", "disabled"],
    exclude: Optional[list[type]] = None,
):
    if exclude is None:
        exclude = []

    for child in parent.winfo_children():
        # Continue if type of child is in exclude
        if any(isinstance(child, t) for t in exclude):
            continue

        if "state" in child.keys():
            child.configure(state=state)  # type: ignore
        else:
            set_widget_state_recursive(child, state, exclude)  # type: ignore


# DEBUG: Color a widget background
def color_widget(widget: ttk.Widget):
    style = ttk.Style()
    style.configure("Red.TFrame", background="red")  # type: ignore
    widget.configure(style="Red.TFrame")  # type: ignore


# def set_widget_colors(parent: Any) -> None:
#     """Recursively set a random background color for every widget."""
#     for child in parent.winfo_children():
#         try:
#             child.configure(bg=random_color())
#         except tk.TclError:
#             # Some widgets might not support the 'bg' option, so we pass in case of error
#             pass
#         set_widget_colors(child)  # Recursive call to handle child's children


# def random_color() -> str:
#     """Generate a random hex color."""
#     return "#{:02x}{:02x}{:02x}".format(
#         random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
#     )

# def set_widget_highlight(parent):
#     """Recursively set a random highlight background and border for every widget."""
#     for child in parent.winfo_children():
#         try:
#             color = random_color()
#             child.configure(highlightbackground=color, highlightthickness=2)
#         except tk.TclError:
#             pass
#         set_widget_highlight(child)  # Recursive call
