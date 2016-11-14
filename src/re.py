from translate import translate


class MatchObject:
    def __init__(self, rgx, groups, named_groups, txt, start_pos, end_pos):
        self.start_index = groups.index
        self.groups_list = groups.map(lambda g: g if g is not void(0) else None)
        self.named_groups = named_groups
        # part of re api
        self.pos = start_pos
        self.endpos = end_pos
        self.re = rgx
        self.string = txt
        self.lastindex = len(groups) - 1
        self.lastgroup = None
        for gName in Object.js_keys(self.named_groups):
            gId = self.named_groups[gName]
            if gId == self.lastindex:
                self.lastgroup = gName
                break

        id = 0
        for group in groups:
            self[id] = group
            id += 1

    def group(self, *groupIds):
        if len(groupIds) == 0:
            return self.groups_list[0]

        result = []
        for id in groupIds:
            if type(id) is str:
                result.append(self.groups_list[self.named_groups[id]])
            else:
                result.append(self.groups_list[id])

        if len(result) == 1:
            return result[0]
        return result

    def groups(self, default=None):
        return self.groups_list[1:].map(lambda g: g if g is not None else default)

    def groupdict(self, default=None):
        d = dict()
        for gName in Object.js_keys(self.named_groups):
            gId = self.named_groups[gName]
            value = self.groups_list[gId]
            d[gName] = default if value is None else value
        return d

    def end(self, group=None):
        if group is not None:
            raise Error("match.end() with argument is not supported")
        return self.start_index + self.groups_list[0].length

    def start(self, group=None):
        if group is not None:
            raise Error("match.start() with argument is not supported")
        return self.start_index

    def span(self, group=None):
        if group is not none:
            raise Error("match.span() with argument is not supported")
        return (self.start(), self.end())


class PyRegExp:
    def __init__(self, jsStrPattern, jsTokens, jsFlags, named_groups):
        self.pattern = RegExp(jsStrPattern, jsFlags)
        self.jsTokens = jsTokens
        self.jsFlags = jsFlags
        self.named_groups = named_groups

    def getFirstMatch(self, txt, start, end):
        pattern = self.pattern

        if start is 0:
            match = txt.match(pattern)

        #  In python, `^` with `start` will allways fail to match _unless_ `txt[start - 1]` is `\n` and multi-line is active.
        #  Interestingly, `$` with `end` works as expected and requires no special handling.
        elif 'm' not in self.jsFlags or txt[start - 1] != '\n':
            strRgx = ''
            for token in self.jsTokens:
                if token == '^':
                    # impossible group - will allways fail.
                    # we can't just return None, since the '^' might be inside something like `(foo|^)`.
                    token = '[^\S\s]'
                strRgx += token
            pattern = RegExp(strRgx, self.jsFlags)

        match = txt[start:end].match(pattern)

        if match is None:
            return None
        return match

    def search(self, txt, start=None, end=None):
        if start is None:
            start = 0
        if end is None:
            end = len(txt)

        match = self.getFirstMatch(txt, start, end)
        if match is not None:
            return MatchObject(self, match, self.named_groups, txt, start, end)
        return match

    def match(self, txt, start=None, end=None):
        if start is None:
            start = 0
        if end is None:
            end = len(txt)

        match = self.getFirstMatch(txt, start, end)
        if match is None or match.index > start:
            return None
        return MatchObject(self, match, self.named_groups, txt, start, end)

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

    def findall(self, txt, start=0, end=0 / 0):
        globalPattern = RegExp(self.patter, 'g')
        matches = txt.match(globalPattern)
        while txt.index(matches[0]) < start:
            matches = matches[1:]
        # while txt.index(matches[len(matches) - 1]) + 


def compile(pyPattern):
    jsStrPattern, jsTokens, jsFlags, named_groups = translate(pyPattern)
    return PyRegExp(jsStrPattern, jsTokens, jsFlags, named_groups)
