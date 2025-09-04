from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox

def show_error_message(parent, message):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText(message)
    msg_box.exec()

def show_finished_popup(parent, message, title):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()

def wrap_text(name: str, max_num: int) -> str:
    if len(name) > max_num:
        return f"...{name[-max_num:]}"
    return name


import functools
import datetime
import builtins

def gui_logger(package_name="Numbers and Brightness"):
    def decorator(func):
        @functools.wraps(func)

        def wrapper(*args, **kwargs):
            original_print = builtins.print
            
            def custom_print(*args, **kwargs):
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = " ".join(str(arg) for arg in args)
                formatted_message = f"[{package_name}] [{timestamp}] {message}"
                original_print(formatted_message, **kwargs)
            
            try:
                builtins.print = custom_print
                return func(*args, **kwargs)
            finally:
                builtins.print = original_print

        return wrapper
    return decorator