from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Window, BufferControl


class StatusWindow(Window):
    def __init__(self):
        self.buffer = Buffer()
        self.control = BufferControl(buffer=self.buffer)

        self.control.mouse_handler_orig = self.control.mouse_handler
        def tmp(event):
            get_app().layout.current_control = self.control
            self.control.mouse_handler_orig(event)

        self.control.mouse_handler = tmp
        super().__init__(content=self.control)