from translate import translate

ASCII      = A = 0b100000000
DEBUG          = 0b010000000
VERBOSE    = X = 0b001000000
DOTALL     = S = 0b000010000
MULTILINE  = M = 0b000001000
LOCALE     = L = 0b000000100
IGNORECASE = I = 0b000000010
# additional flags
JAVASCRIPT     = 0b1000000000


class Match:
    def __init__(self, rgx, groups, named_groups, txt, start_pos, end_pos):
        self._start_index = groups.index
        self._groups_list = [g if g is not js_undefined else None for g in groups]
        self._named_groups = named_groups

        self.pos = start_pos
        self.endpos = end_pos
        self.re = rgx
        self.string = txt
        self.lastindex = len(groups) - 1
        self.lastgroup = None

        for group_name, group_id in self._named_groups.items():
            if group_id == self.lastindex:
                self.lastgroup = group_name
                break

        for idx, group in enumerate(groups):
            self[idx] = group

    def group(self, *groupIds):
        if len(groupIds) == 0:
            return self._groups_list[0]

        result = []
        for id in groupIds:
            if type(id) is str:
                result.append(self._groups_list[self._named_groups[id]])
            else:
                result.append(self._groups_list[id])

        if len(result) == 1:
            return result[0]
        return tuple(result)

    def groups(self, default=None):
        return tuple([g if g is not None else default for g in self._groups_list[1:]])

    def groupdict(self, default=None):
        d = dict()
        for gName in Object.js_keys(self._named_groups):
            gId = self._named_groups[gName]
            value = self._groups_list[gId]
            d[gName] = default if value is None else value
        return d

    def end(self, group=None):
        if group is not None:
            raise Error("match.end() with argument is not supported")
        return self._start_index + self._groups_list[0].length

    def start(self, group=None):
        if group is not None:
            raise Error("match.start() with argument is not supported")
        return self._start_index

    def span(self, group=None):
        if group is not none:
            raise Error("match.span() with argument is not supported")
        return (self.start(), self.end())


class PyRegExp:
    def __init__(self, jsStrPattern, jsTokens, jsFlags, named_groups):
        self.pattern = RegExp(jsStrPattern, jsFlags)
        self.jsTokens = jsTokens
        self.jsFlags = jsFlags
        self._named_groups = named_groups

    def getFirstMatch(self, txt, start, end):
        pattern = self.pattern

        #  In python, `^` with `start` will always fail to match _unless_ `txt[start - 1]` is `\n` and multi-line is active.
        #  Interestingly, `$` with `end` works as expected and requires no special handling.
        if start != 0 and 'm' not in self.jsFlags or txt[start - 1] != '\n':
            strRgx = ''
            for token in self.jsTokens:
                if token == '^':
                    # impossible group - will always fail.
                    # we can't just return None, since the '^' might be inside something like `(foo|^)`.
                    token = '[^\S\s]'
                strRgx += token
            pattern = RegExp(strRgx, self.jsFlags)

        return txt[start:end].match(pattern)

    def search(self, txt, start=0, end=None):
        if end is None:
            end = len(txt)

        match = self.getFirstMatch(txt, start, end)
        if match is not None:
            return Match(self, match, self._named_groups, txt, start, end)
        return match

    def match(self, txt, start=0, end=None):
        if end is None:
            end = len(txt)

        match = self.getFirstMatch(txt, start, end)
        if match is None or match.index > start:
            return None
        return Match(self, match, self._named_groups, txt, start, end)

    def split(self, txt, maxsplit=None):
        if maxsplit is None:
            splitted = txt.split(self.pattern)
        else:
            splitted = txt['split'](self.pattern, maxsplit)

            consumed = 0
            for split in splitted:
                consumed += len(split)
            # if we split "test%test%test" with maxsplit 1,
            # python will give ["test", "test%test"], and js ["test", "%test%test"]
            # this last bit fixes that
            last_el = txt[consumed + 1:]
            skip = len(last_el.match(self.pattern)[0])
            splitted.append(last_el[skip:])

        return splitted

    def findall(self, txt, start=0, end=None):
        if end is None:
            end = len(txt)
        # modify pattern to match globally
        globalPattern = RegExp(self.pattern, 'g')
        # not correct? probably needs the same logic as `getFirstMatch()`, but will work for now
        txt = txt[start:end]
        result = []

        while True:
            match = globalPattern.exec(txt)
            if match:
                if (len(match) > 2):
                    result.append(tuple(match[1:]))
                elif (len(match) == 2):
                    result.append(match[1])
                else:
                    result.append(match[0])
            else:
                break

        return result


def compile(pyPattern, flags=0):
    if not flags & JAVASCRIPT:
        jsTokens, jsFlags, named_groups = translate(pyPattern)
        return PyRegExp(''.join(jsTokens), jsTokens, jsFlags, named_groups)
    return PyRegExp(pyPattern, None, '', dict())


def search(pyPattern, txt, flags=0):
    rgx = compile(pyPattern)
    return rgx.search(txt)


def match(pyPattern, txt, flags=0):
    rgx = compile(pyPattern)
    return rgx.match(txt)


def split(pyPattern, txt, maxsplit, flags=0):
    rgx = compile(pyPattern)
    return rgx.split(pyPattern, maxsplit=None)


def findall(pyPattern, txt, flags=0):
    rgx = compile(pyPattern)
    return rgx.findall(pyPattern, txt)
