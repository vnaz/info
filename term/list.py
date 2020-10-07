from prompt_toolkit.data_structures import Point
from prompt_toolkit.formatted_text import to_formatted_text, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import UIControl, UIContent, Window

from term.app import App

class ListControl(UIControl):
    def __init__(self, collection=[]):
        self.collection = collection
        self.index = 0
        self.keys = KeyBindings()
        self.mode = "list" # multi"
        self.multi_start = 0
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

    def move_cursor_down(self) -> None:
        App.app.layout.focus(self)

    def is_focusable(self) -> bool:
        return True

    def get_key_bindings(self):
        return self.keys

    def create_content(self, width: int, height: int) -> "UIContent":
        self.height = height
        self.width = width

        cursor = Point(0, self.index)
        lines = height
        get_line_func = None

        if self.mode == 'multi':
            offset = self.multi_start
            column_widths = []
            separator = " | "

            size = 0
            while size < width:
                column_width = 0
                for i in range(offset, offset + height):
                    column_width = max(column_width, len(self.collection[i]))
                offset += height
                size += column_width + len(separator)
                column_widths.append(column_width)

            # extra = " " * (width - (size - column_widths[-1]))
            # separator = extra + separator

            def get_line(line: int) -> StyleAndTextTuples:
                data = []
                for c in range(0, len(column_widths)):
                    text = ""
                    if c * height + line < len(self.collection):
                        text += self.collection[c * height + line]
                    data.append(text.rjust(column_widths[c]))
                text = separator.join(data)
                return to_formatted_text(text)

            get_line_func = get_line
            cursor = Point(sum([x + len(separator) for x in column_widths[:(self.index-self.multi_start) // height]]),
                           (self.index-self.multi_start) % height)
        else:
            lines = len(self.collection)
            def get_line(line: int) -> StyleAndTextTuples:
                text = style = ""
                if line < len(self.collection):
                    text = to_formatted_text(self.collection[line])
                if line == self.index:
                    style = "bg:#888888 #ffffff"
                return to_formatted_text(text, style)

            get_line_func = get_line

        return UIContent(
            cursor_position=cursor,
            get_line=get_line_func,
            line_count=lines,
        )

class ListWindow(Window):
    def __init__(self, content):
        self.control = ListControl(content)
        super().__init__(content=self.control)