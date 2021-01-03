from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Window, NumberedMargin, BufferControl
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent
from pygments.lexers.python import PythonLexer

class EditorWindow(Window):
    def __init__(self):
        self.buffer = Buffer()
        self.lexer = PygmentsLexer(PythonLexer)
        self.keys = KeyBindings()
        self.control = BufferControl(buffer=self.buffer, lexer=self.lexer)
        self.margin = NumberedMargin

        self.control.mouse_handler_orig = self.control.mouse_handler
        def tmp(mouse_event: MouseEvent):
            get_app().layout.current_control = self.control
            self.control.mouse_handler_orig(mouse_event)
        self.control.mouse_handler = tmp

        super().__init__(content=self.control,left_margins=[NumberedMargin()])
