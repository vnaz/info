import re
import io


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

    def forward(self, side, single=False):
        result = []
        value = getattr(self, side)
        if isinstance(value, list):
            result = value
        elif value is not None:
            result = [value]

        if single:
            if len(result) > 0:
                result = result[0]
            else:
                result = None

        return result

    def __str__(self):
        return '%s{%s, %s}: %s' % (self.name, self.start, self.end, self.value)

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
    def __init__(self, source=None, rules=list()):
        self.source = source

        self.handlers = {}
        self.rules = rules

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
            for token in self.current.forward('right'):
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
                    left = res.forward('left')
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

    def parse(self, source=None):
        if source is not None:
            self.source = source

        if isinstance(self.source, str):
            self.source = io.BytesIO(self.source)

        char = None
        self.begin = t = self.token(name='lex', value='', start=0, end=0)
        while char != '':
            char = self.source.read(1)
            if char in self.split:
                if len(t.value) > 0:
                    t = self.token(name='lex', value='', start=t.end+1, end=t.end+1)
                if char not in self.skip:
                    t.update(value=char, end=t.end+1)
                    t = self.token(name='lex', value='', start=t.end, end=t.end)
            else:
                t.update(value=t.value+char, end=t.end+1)
        self.source.close()


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
        tokens = [token]
        for arg in self.args:
            for option in tokens:
                assert isinstance(arg, Rule)
                tmp = arg.apply(option, parser)
                if tmp is not None:
                    break
            if not isinstance(tmp, Token):
                return None
            result.value.insert(0, tmp)
            tokens = tmp.forward('left')
        result.left = tmp.left
        result.start = tmp.start
        return result


class Block(Rule):
    def __init__(self, start, end, escape=None, mode=None, **params):
        self.start = start if isinstance(start, Rule) else Lex(start)
        self.end = end if isinstance(end, Rule) else Lex(end)
        self.escape = end if isinstance(escape, Rule) else Lex(escape)
        self.stack = []
        Rule.__init__(self, **params)

    def apply(self, token, parser):
        if isinstance(self.escape, Rule):
            if isinstance(self.escape.apply(token.forward('left', True), parser), Token):
                return None

        if len(self.stack) > 0:
            tmp = self.end.apply(token, parser)
            if isinstance(tmp, Token):
                begin = self.stack.pop()
                result = Token(name=self.name, value=[], start=begin.start, end=tmp.end, left=begin.left) # !!!
                while isinstance(tmp, Token) and tmp != begin:
                    result.value.insert(0, tmp)
                    tmp = tmp.forward('left', True)
                return result

        tmp = self.start.apply(token, parser)
        if isinstance(tmp, Token):
            self.stack.append(tmp)
            return tmp


class Repeat(Rule):
    def __init__(self, rule, min=0, max=0, **params):
        self.rule = rule if isinstance(rule, Rule) else Lex(rule)
        self.min = min
        self.max = max
        self.previous = None
        Rule.__init__(self, **params)

    def apply(self, token, parser):
        result = None
        cnt = 1
        tmp = self.rule.apply(token, parser)
        while isinstance(tmp, Token) and cnt < self.min and self.max > cnt:
            if tmp.forward('left', True) == self.previous:
                self.previous.value.append(tmp)
                self.previous.end = tmp.end
                return self.previous
            else:
                if result is None:
                    result = Token(name=self.name, value=[tmp], start=tmp.start, end=tmp.end)
        return result


class Or(Rule):
    def apply(self, token, parser):
        for arg in self.args:
            assert isinstance(arg, Rule)
            tmp = arg.apply(token, parser)
            if isinstance(tmp, Token):
                return tmp.clone(name=self.name, value=[])
        return None


class And(Rule):
    def apply(self, token, parser):
        for arg in self.args:
            assert isinstance(arg, Rule)
            tmp = arg.apply(token, parser)
            if not isinstance(tmp, Token):
                return None
        return token.clone(name=self.name, value=[])


class Not(Rule):
    def apply(self, token, parser):
        for arg in self.args:
            assert isinstance(arg, Rule)
            if arg.apply(token, parser) is not None:
                return None
        return token.clone(name=self.name, value=[])


class Any(Rule):
    def apply(self, token, parser):
        return token

# parser = XParser(file('test.php'))
parser = XParser("""
<?php if (x == (10 * 22) ) { 
    echo 'something to test'; 
}
""")

parser.rules.append(Seq(Lex('<'), Lex('?'), Lex('php'), name='php'))
parser.rules.append(Block("'", "'", "\\", name='string'))
parser.rules.append(Block("{", "}", name='scope'))
parser.rules.append(Block("(", ")", name='bracket'))

parser.parse()
for x in parser:
    print x
