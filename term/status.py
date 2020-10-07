from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Window, BufferControl


class StatusWindow(Window):
    def __init__(self):
        self.buffer = Buffer()
        self.control = BufferControl(buffer=self.buffer)
        super().__init__(content=self.control)