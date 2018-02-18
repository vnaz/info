import re


class Token:
    def __init__(self, **params):
        self.name = None
        self.value = None

        self.start = None
        self.end = None

        self.left = None
        self.right = None
        self.top = None
        self.bottom = None

        self.update(**params)

    def clone(self, **params):
        tmp = self.__dict__.copy()
        tmp.update(params)
        return Token(**tmp)

    def update(self, **params):
        for param in params:
            if hasattr(self, param):
                setattr(self, param, params[param])

    def connect(self, token, side = None, replace = False):
        assert isinstance(token, Token)
        if side is None:
            if token.start <= token.end < self.start:
                side = 'left'
            elif token.start >= token.end > self.end:
                side = 'right'
            elif token.start > self.start and token.end < self.end:
                side = 'bottom'
            elif token.start < self.start and token.end > self.end:
                side = 'top'
            else:
                raise Exception('can not detect relation')

        assert side in ('left', 'right', 'bottom', 'top')
        if replace:
            setattr(self, side, token)
        else:
            old = getattr(self, side)

            if isinstance(old, list):
                old.append(token)
            elif old is not None:
                setattr(self, side, [old, token])
            else:
                setattr(self, side, token)

    def nearby(self, side='right'):
        value = getattr(self, side)
        if isinstance(value, list):
            return value
        elif value is not None:
            return [value]
        return []

    def __str__(self):
        return '%s[%s, %s] - %s' % (self.name, self.start, self.end, self.value)

    def __repr__(self):
        return self.__str__()


class Rule:
    def __init__(self, *args, **params):
        self.args = args
        self.name = self.__class__.__name__
        for key in params:
            setattr(self, key, params[key])

    def apply(self, token, parser):
        return None


class XParser:
    def __init__(self, filename=None):
        self.filename = filename
        self.file = None

        self.handlers = {}
        self.rules = []

        # @var Token
        self.begin = self.current = self.final = None

        # lexer state
        self.pos = None
        self.skip = ' \t\n'
        self.split = ' \t\n`+-=~|!@#$%^&*()[]{}<>,.?:;"\'\\/'

    def __iter__(self):
        self.current = self.begin
        return self

    def next(self):
        if (self.current is None) or (self.current == self.final):
            raise StopIteration
        else:
            assert isinstance(self.current, Token)
            result = self.current
            for token in self.current.nearby('right'):
                self.current = token
                break
            return result

    def token(self, **params):
        self.final = Token(**params)
        if self.current is not None:
            for rule in self.rules:
                res = rule.apply(self.current, self)
                if isinstance(res, Token):
                    self.current = res
                    left = res.nearby('left')
                    if len(left) == 0:
                        self.begin = self.current = res
                    else:
                        for token in left:
                            assert isinstance(token, Token)
                            token.connect(res, 'right', True)

            self.final.connect(self.current, 'left')
            self.current.connect(self.final, 'right')

        self.current = self.final
        return self.current

    def parse(self, filename=None):
        if filename is not None:
            self.filename = filename
        self.file = file(self.filename)

        char = None
        self.begin = t = self.token(name='lex', value='', start=0, end=0)
        while char != '':
            char = self.file.read(1)
            if char in self.split:
                if len(t.value) > 0:
                    t = self.token(name='lex', value='', start=t.end, end=t.end)
                if char not in self.skip:
                    t.update(value=char, end=t.end+1)
                    t = self.token(name='lex', value='', start=t.end, end=t.end)
            else:
                t.update(value=t.value+char, end=t.end+1)
        self.file.close()


class Lex(Rule):
    def __init__(self, value, *args, **params):
        Rule.__init__(self, **params)
        self.value = value

    def apply(self, token, parser):
        if not isinstance(token, Token):
            return None
        if token.value == self.value:
            return token.clone(name=self.name)


class Re(Rule):
    def __init__(self, value, *args, **params):
        Rule.__init__(self, **params)
        self.value = re.compile(value)

    def apply(self, token, parser):
        if not isinstance(token, Token):
            return False
        if self.value.match(token.value):
            return token.clone(name=self.name)


class Seq(Rule):
    def __init__(self, *args, **params):
        Rule.__init__(self, **params)
        self.args = []
        for arg in args:
            if not isinstance(arg, Rule):
                self.args.insert(0, Lex(arg))
            else:
                self.args.insert(0, arg)

    def apply(self, token, parser):
        result = token.clone(name=self.name, value=[])
        tmp = None
        options = [token]
        for arg in self.args:
            for option in options:
                tmp = arg.apply(option, parser)
                if tmp is not None:
                    break
            if not isinstance(tmp, Token):
                return None
            result.value.append(tmp)
            options = tmp.nearby('left')
        result.left = tmp.left
        result.start = tmp.start
        return result


parser = XParser('test.php')
parser.rules.append(Seq(Lex('<'), Lex('?'), Re('php')))
parser.split = parser.split.replace('$', '')
parser.parse()
for x in parser:
    print x
