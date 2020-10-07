from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Window, NumberedMargin, BufferControl
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

class EditorWindow(Window):
    def __init__(self):
        self.buffer = Buffer()
        self.lexer = PygmentsLexer(PythonLexer)
        self.control = BufferControl(buffer=self.buffer, lexer=self.lexer)
        self.margin = NumberedMargin
        super().__init__(content=self.control,left_margins=[NumberedMargin()])
