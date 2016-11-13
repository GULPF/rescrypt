VERBOSE = False


class Token:
    def __init__(self, name, paras=[], pure=False):
        self.name  = name
        self.paras = paras
        self.pure = pure
        # tmp until I have thought of something better
        self.isModeGroup = False

    def resolve(self):
        paras = ''
        for para in self.paras:
            paras += str(para)

        return self.name + paras


def translate(rgx):
    stack = []
    queue = list(rgx)

    jsFlags = ''
    pyFlags = 'iLmsux'

    dotsMatchAll = False

    while True:
        high = len(stack) - 1

        s0 = stack[high]     if len(stack) > 0 else Token('')
        s1 = stack[high - 1] if len(stack) > 1 else Token('')
        s2 = stack[high - 2] if len(stack) > 2 else Token('')

        if VERBOSE:
            for token in stack:
                print(token.resolve(), '\t', end='')
            print()

        if s1.name == '\\':
            if s0.name == 'A':
                stack[-2:] = [Token('^')]

            elif s0.name == 'a':
                stack[-2:] = [Token('\\07')]

            elif s0.name == 'Z':
                stack[-2:] = [Token('$')]

            else:
                stack[-2:] = [Token('\\' + s0.name)]

        elif s0.name == '$' and s0.pure:
            stack[high] = Token('(?=\\n?$)')

        elif s1.name == '{':
            if s0.name == ',' and len(s1.paras) == 0:
                s1.paras.append('0')
                s1.paras.append(',')
            else:
                if s0.name == '}':
                    s1.paras.append('}')
                    s1.name = s1.resolve()
                    s1.paras = []
                else:
                    s1.paras.append(s0.name)

            stack = stack[:-1]

        elif s1.name == '[' and s0.name == '^':
            stack[-2:] = [Token('[^')]

        elif s1.name == '(' and s0.name == '?':
            stack[-2:] = [Token('(?')]

        elif s1.name in ['*', '+', '?'] and s0.name == '?':
            stack[-2:] = [Token(s1.name + '?')]

        elif s1.isModeGroup and s0.name == ')':
            stack = stack[:-2]

        elif s1.name == '(?':
            if s0.name in pyFlags:
                if s0.name == 'i':
                    jsFlags += 'i'
                elif s0.name == 'm':
                    jsFlags += 'm'
                elif s0.name == 's':
                    # handled at end of method
                    dotsMatchAll = True
                else:
                    raise Error('Unsupported flag: ' + s0.name)

                stack.pop()
                s1.isModeGroup = True

            else:
                stack[-2:] = [Token('(?' + s0.name)]

        elif s1.name == '(?#':
            if s0.name == ')':
                stack = stack[:-2]
            else:
                stack = stack[:-1]

        # the shift in 'shift-reduce''
        else:
            if not queue:
                break

            stack.append(Token(queue[0], [], True))
            queue = queue[1:]

    resolvedTokens = []
    res = ''
    idx = 0

    for token in stack:
        stringed = token.resolve()
        if dotsMatchAll and stringed == '.':
            stringed = '[\s\S]'
            resolvedTokens[idx] = '[\s\S]'
        res += stringed
        resolvedTokens.append(stringed)
        idx += 1
    return res, resolvedTokens, jsFlags
