from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, VSplit, HSplit, FloatContainer, Float
from prompt_toolkit.widgets import Dialog, Button, Label

from .editor import EditorWindow
from .list import ListWindow
from .status import StatusWindow

class App(Application):
    app = None
    def __init__(self):
        if not App.app is None:
            return App.app

        self.list = ListWindow(["test %s" % str(x*50) for x in range(1, 100)])
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

        @self.keys.add('escape')
        def key_exit(event):
            self.dialog("Are you sure want to exit?", "Quit", 'No', None, [
                Button(text="Yes", handler=event.app.exit)])

        @self.keys.add('tab')
        def focus_next(event):
            event.app.layout.focus_next()

        @self.keys.add('s-tab')
        def focus_previous(event):
            event.app.layout.focus_previous()

        @self.keys.add('f1')
        def f1(event):
            self.layout = Layout(self.list)

        @self.keys.add('f2')
        def f2(event):
            self.layout = Layout(VSplit([self.list, self.editor]))

        @self.keys.add(':')
        def ctrl_colon(event):
            event.app.layout.focus(self.status)

        super().__init__(key_bindings=self.keys, layout=self.layout, full_screen=True, mouse_support=True)
        App.app = self

    def dialog(self, message, title='', button_name='OK', button_handler=None, buttons=[]):
        original_layout = self.layout

        def no_handler() -> None:
            if not button_handler is None:
                button_handler()
            self.layout = original_layout

        dialog = Dialog(
            title=title,
            body=Label(text=message, dont_extend_height=True),
            buttons=buttons + [Button(text=button_name, handler=no_handler)],
            width=100
        )
        self.layout = Layout(FloatContainer(self.layout.container, floats=[Float(dialog.container)]), focused_element=dialog)