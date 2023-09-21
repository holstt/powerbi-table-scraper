import logging
import tkinter as tk
import traceback

from typing_extensions import override


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

        self.text_widget.see(tk.END)  # Scroll to the bottom of the text widget
        self.text_widget.configure(state=tk.DISABLED)
