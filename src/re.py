from translate import translate


class MatchObject:
    def __init__(self, groups):
        self.groups_tuple = groups

        id = 0
        for group in groups:
            self[id] = group
            id += 1

    def group(self, *groupId):
        if len(groupId) == 0:
            return self.groups_tuple[0]
        if len(groupId) == 1:
            return self.groups_tuple[groupId[0]]

        result = []
        for id in groupId:
            result.append(self.groups_tuple[id])
        return tuple(result)

    # TODO: argument `default` not supported
    def groups(self, default=None):
        return self.groups_tuple[1:]


class PyRegExp:
    def __init__(self, jsStrPattern, jsTokens, jsFlags):
        self.pattern = RegExp(jsStrPattern, jsFlags)
        self.jsTokens = jsTokens
        self.jsFlags = jsFlags

    def getFirstMatch(self, txt, start=None, end=None):
        pattern = self.pattern

        if start is None:
            start = 0
        if end is None:
            end = len(txt)

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
        match = self.getFirstMatch(txt, start, end)
        if match is not None:
            return MatchObject(match)
        return match

    def match(self, txt, start=None, end=None):
        match = self.getFirstMatch(txt, start, end)
        if match is None or match.index > start:
            return None
        return MatchObject(match)

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
    jsStrPattern, jsTokens, jsFlags = translate(pyPattern)
    return PyRegExp(jsStrPattern, jsTokens, jsFlags)
