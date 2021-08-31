from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Window, BufferControl
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.mouse_events import MouseEvent
from pygments.lexers.python import PythonLexer
from code import InteractiveConsole

from ast import Expression, AST, Expr, parse

class ReplWindow(Window):

    def __init__(self):
        self.buffer = Buffer()
        self.lexer = PygmentsLexer(PythonLexer)
        self.keys = KeyBindings()
        self.control = BufferControl(buffer=self.buffer, lexer=self.lexer, key_bindings=self.keys)
        self.console = InteractiveConsole()

        @self.keys.add(Keys.Tab)
        def on_key(event):
            self.buffer.insert_text("    ")

        @self.keys.add(Keys.Down)
        def on_key(event):
            if self.buffer.cursor_position == len(self.buffer.text):
                self.buffer.insert_text("\n")
            else:
                self.buffer.cursor_down()

        @self.keys.add(Keys.Enter)
        def on_key(event):
            try:
                ast = parse(self.buffer.text)
                expr = None
                if len(ast.body) == 1 and isinstance(ast.body[0], Expr):
                    expr = Expression(ast.body[0].value)
                else:
                    if len(ast.body) > 1 and hasattr(ast.body[-1], 'value'):
                        expr = Expression(ast.body[-1].value)

                if expr is None:
                    exec(self.buffer.text)
                else:
                    code = compile(expr, '<input>', 'eval')
                    val = eval(code)
                    globals()['_'] = val
                    self.buffer.text = str(val)
            except Exception as e:
                self.buffer.text = str(e)

        self.get_line_prefix = lambda line, y: ">>> " if line == 0 else "... "

        self.control.mouse_handler_orig = self.control.mouse_handler
        def tmp(mouse_event: MouseEvent):
            get_app().layout.current_control = self.control
            self.control.mouse_handler_orig(mouse_event)
        self.control.mouse_handler = tmp

        super().__init__(content=self.control, get_line_prefix=self.get_line_prefix)
