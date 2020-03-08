from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import NumberedMargin, Layout
from prompt_toolkit.layout.containers import Window, Float, FloatContainer, ConditionalContainer, HSplit, VSplit
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.widgets import Dialog, Button, Label, FormattedTextToolbar

buffer = Buffer()
command_buffer = Buffer(
    # accept_handler=handle_action,
    enable_history_search=True,
    # completer=create_command_completer(self),
    # history=commands_history,
    multiline=True)
command_line = Window(
    BufferControl(buffer=command_buffer),
    height=lambda: command_buffer.text.count("\n") + 1,
    get_line_prefix=lambda x, y: ": " if x == 0 else "> ")
status_bar = FormattedTextToolbar("status", style="fg: #000000 bg:#bcbcbc")
editor = Window(content=BufferControl(buffer=buffer), left_margins=[NumberedMargin()])
keys = KeyBindings()
layout = Layout(HSplit([VSplit([HSplit([editor, status_bar])]), command_line]))
app = Application(key_bindings=keys, layout=layout, full_screen=True)


@keys.add('tab')
def focus_next(event) -> None:
    event.app.layout.focus_next()


@keys.add('s-tab')
def focus_previous(event) -> None:
    event.app.layout.focus_previous()


@keys.add('c-a')
def _tab(event):
    original_layout = app.layout

    def ok_button() -> None:
        app.layout = original_layout

    dialog = Dialog(
        title="title",
        body=Label(text="some text", dont_extend_height=True),
        buttons=[Button(text="ok", handler=ok_button)],
        width=100
    )
    app.layout = Layout(FloatContainer(editor, floats=[Float(dialog.container)]))


@keys.add('c-q')
def _exit(event):
    event.app.exit()

app.run()