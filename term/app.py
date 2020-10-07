from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, VSplit, HSplit

from term.editor import EditorWindow
from term.list import ListWindow
from term.status import StatusWindow

class App(Application):
    app = None
    def __init__(self):
        if not App.app is None:
            return App.app

        self.list = ListWindow([str(x*50) for x in range(1, 100)])
        self.status = StatusWindow()
        self.editor = EditorWindow()
        self.layout = Layout(HSplit([VSplit([self.list, self.editor]), self.status]))
        self.keys = KeyBindings()

        x = Buffer()
        x.text = open(__file__, "r").read()
        self.editor.content.buffer = x

        @self.keys.add('c-q')
        def key_exit(event):
            event.app.exit()

        @self.keys.add('tab')
        def focus_next(event):
            event.app.layout.focus_next()

        @self.keys.add('s-tab')
        def focus_previous(event):
            event.app.layout.focus_previous()

        super().__init__(key_bindings=self.keys, layout=self.layout, full_screen=True, mouse_support=True)
        App.app = self