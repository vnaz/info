import os
import re


class XFolder:
    def __init__(self, path):
        assert os.path.isdir(path)
        self.Path = path

    def files(self, search=None, regex=None, func=None):
        if regex is not None:
            try:
                regex = re.compile(regex)
            except:
                regex = None

        if func is not None and not hasattr(func, '__call__'):
            func = None

        if regex is None and func is None and search is None:
            search = ""

        result = XList()
        for p, _, files in os.walk(self.Path):
            for f in files:
                if (regex is not None and regex.match(f)) or \
                        (func is not None and func(f)) or \
                        (search is not None and search in f):
                    result.append(XFile("%s/%s" % (p, f)))
        return result


class XFile:
    def __init__(self, path):
        if not os.path.exists(path):
            raise Exception("%s not found" % path)
        self.Path = path
        self.File = None

    def contents(self):
        return open(self.Path, "r").read()

    def filter(self, func):
        f = open(self.Path, "r")
        result = func(f)
        f.close()
        return result

    def contains(self, search=None, regex=None, func=None):
        if regex is not None:
            try:
                regex = re.compile(regex)
            except:
                regex = None

        if func is not None and not hasattr(func, '__call__'):
            func = None

        for line in self:
            if (regex is not None and regex.match(line)) or \
                    (func is not None and func(line)) or \
                    (search is not None and search in line):
                return True

        return False

    def lines(self, search=None, regex=None, func=None):
        result = XList()

        if regex is not None:
            try:
                regex = re.compile(regex)
            except:
                regex = None

        if func is not None and not hasattr(func, '__call__'):
            func = None

        for line in self:
            if func is not None:
                line = func(line)
                if line is not None and line != "":
                    result.append(line)

            if (regex is not None and regex.match(line)) or \
                    (search is not None and search in line):
                result.append(line)

        return result

    def f(self, search=None, regex=None, func=None):
        result = XList()

        if regex is not None:
            try:
                regex = re.compile(regex)
            except:
                regex = None

        if func is not None and not hasattr(func, '__call__'):
            func = None

        f = open(self.Path, "r")
        content = f.read()

        if regex is not None:
            for x in regex.findall(content):
                result.append(x)

        if func is not None:
            for x in func(content):
                result.append(x)

        f.close()
        return result

    def __iter__(self):
        if self.File is None:
            self.File = open(self.Path, "r")
        assert isinstance(self.File, file)

        for result in self.File:
            yield result
        self.File.close()
        self.File = None

    def __contains__(self, item):
        return self.contain(item)

    def __repr__(self):
        return self.Path


class XDict(dict):
    def __init__(self, seq=(), parent=None, k_out=str, v_out=str, **kwargs):
        if not hasattr(seq, "__iter__"):
            seq = (seq,)
        super(XDict, self).__init__(seq, **kwargs)
        self._parent = parent
        self._key_out = k_out
        self._val_out = v_out

    def __getattr__(self, item):
        if hasattr(super(XDict, self), item):
            return getattr(super(XDict, self), item)

        result = XDict((), self, self._key_out, self._val_out)
        for key, val in self.iteritems():
            result[key] = getattr(val, item, None)
        return result

    def __call__(self, *args, **kwargs):
        result = XDict((), self, self._key_out, self._val_out)
        for key, val in self.iteritems():
            if hasattr(val, '__call__'):
                try:
                    result[key] = val(*args, **kwargs)
                except:
                    result[key] = None
        return result

    def __repr__(self):
        result = ""
        for key in sorted(self.keys()):
            x = self[key]

            x = self._val_out(x)
            if "\n" in x:
                x = "\n\t".join(x.split("\n"))

            result += "%s:\n\t%s\n" % (self._key_out(key), x)
        return result


class XList(list):
    def __init__(self, iterable=(), parent=None, out=str, pout=None):
        if not hasattr(iterable, "__iter__"):
            iterable = (iterable,)
        super(XList, self).__init__(iterable)
        self._parent = parent
        self._out = out
        self._pout = pout

    def clean(self):
        result = XList((), self._parent, self._out, self._pout)
        for X in self:
            if X is None:
                continue
            if isinstance(X, list) and len(X) == 0:
                continue
            result.append(X)
        return result

    def sort(self, cmp=None, key=None, reverse=False):
        return XList(sorted(self, cmp, key, reverse), self._parent, self._out, self._pout)

    def filter(self, func):
        result = XList((), self, self._out, self._pout)
        for X in self:
            if isinstance(X, XList):
                result.append(X.filter(func))
            else:
                if func(X):
                    result.append(X)
        return result

    def map(self, func):
        result = XList((), self, self._out, self._pout)
        for X in self:
            if isinstance(X, XList):
                result.append(X.map(func))
            else:
                result.append(func(X))
        return result

    def group(self, func):
        result = XDict((), self)
        for X in self:
            group_key = func(X)
            if group_key in result:
                result[group_key].append(X)
            else:
                result[group_key] = XList(X, self, self._out, self._pout)
        return result

    def out(self, func):
        self._out = func
        return self

    def __getslice__(self, i, j):
        result = XList((), self._parent, self._out, self._pout)
        for X in super(XList, self).__getslice__(i, j):
            result.append(X)
        return result

    def __getattr__(self, item):
        if hasattr(super(XList, self), item):
            return getattr(super(XList, self), item)

        result = XList((), self, self._out, self._pout)
        for X in self:
            result.append(getattr(X, item, None))
        return result

    def __call__(self, *args, **kwargs):
        result = XList((), self, self._out, self._pout)
        for X in self:
            if hasattr(X, '__call__'):
                result.append(X(*args, **kwargs))
        return result

    def __str__(self):
        return "\n".join(map(self._out, self))

    def __repr__(self):
        result = ""

        count = len(self)
        fmt = "%" + str(len(str(count))) + "s) "
        for i, x in enumerate(self):
            prefix = ""
            if count > 1:
                prefix = fmt % i

            if not isinstance(x, str):
                if self._pout is not None and self._parent is not None:
                    x = self._pout(self._parent[i]) + self._out(x)
                else:
                    x = self._out(x)

            if prefix != "" and "\n" in x:
                x = ("\n" + " " * len(prefix)).join(x.split("\n"))

            result += "%s%s\n" % (prefix, x)
        return result
