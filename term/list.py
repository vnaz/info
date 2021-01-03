from prompt_toolkit.application import get_app
from prompt_toolkit.data_structures import Point
from prompt_toolkit.formatted_text import to_formatted_text, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import UIControl, UIContent, Window
from prompt_toolkit.mouse_events import MouseEvent


class ListControl(UIControl):
    def __init__(self, collection:tuple=[]):
        self.collection = collection
        self.offset = 0
        self.index = 0
        self.column = 0

        self.labels = []
        self.columns = [str]
        self.widths = []
        self.split = None

        self.keys = KeyBindings()
        self.height = 0
        self.width = 0

        @self.keys.add('left')
        def key_up(event):
            self.index = max(self.index - self.height, 0)

        @self.keys.add('right')
        def key_up(event):
            self.index = min(self.index + self.height, len(self.collection) - 1)

        @self.keys.add('up')
        def key_up(event):
            self.index = max(self.index - 1, 0)

        @self.keys.add('down')
        def key_down(event):
            self.index = min(self.index + 1, len(self.collection) - 1)

    def is_focusable(self) -> bool:
        return True

    def get_key_bindings(self):
        return self.keys

    def mouse_handler(self, event: MouseEvent) -> "NotImplementedOrNone":
        get_app().layout.current_control = self
        self.index = event.position.y
        if len(self.columns) < len(self.widths):
            x = 0
            for i, w in enumerate(self.widths):
                if x < event.position.x < x + w:
                    if i > len(self.columns):
                        self.index += self.height * i
                        break
                x += w
        return super().mouse_handler(event)

    def create_content(self, width: int, height: int) -> "UIContent":
        self.height = height
        self.width = width

        cursor = Point(0, self.index)
        if len(self.labels) > 0:
            cursor = Point(0, self.index + 2)
            self.height -= 2

        if not self.split is None:
            column_width = (width - self.split) // self.split
            self.widths = [column_width for _ in range(0, self.split)]
            self.split = None
        elif len(self.widths) == 0:
            self.widths = [self.width]

        if self.index < self.offset or self.index > self.offset + (len(self.widths) - len(self.columns) +1) * self.height - 1:
            self.offset = (self.index // self.height) * self.height

        def get_line(line: int) -> StyleAndTextTuples:
            text = to_formatted_text('')
            for column in range(0, len(self.widths)):
                index = self.offset + line
                value = style = ''
                if len(self.labels) > 0 and line < 2:
                    if line == 0:
                        value = self.labels[column] if len(self.labels) > column else self.labels[-1]
                    else:
                        value = '-' * self.widths[column]
                else:
                    if column > len(self.columns)-1:
                        index = self.offset + line + self.height * (column - len(self.columns) + 1)
                        provider = self.columns[-1]
                    else:
                        provider = self.columns[column]

                    if len(self.labels) > 0:
                        index -= 2

                    if index < len(self.collection):
                        value = str(provider(self.collection[index]))

                    if index == self.index:
                        style = 'bg:#888888 #ffffff'

                if len(value) > self.widths[column]:
                    value = '%s...' % str(value)[0:max(0, self.widths[column]-3)]

                if len(self.widths) > 1:
                    value = value.rjust(self.widths[column], ' ')

                text += to_formatted_text(' ' if column > 0 else '') + to_formatted_text(value, style)
            return text

        return UIContent(
            cursor_position=cursor,
            get_line=get_line,
            line_count=height,
        )

class ListWindow(Window):
    def __init__(self, content):
        self.control = ListControl(content)
        super().__init__(content=self.control)