VERBOSE = False


class Group:
    def __init__(self, start, end, klass):
        self.start = start
        self.end = end
        self.klass = klass

    def __repr__(self):
        return str((self.start, self.end, self.klass))


def generate_group_spans(tokens):
    group_info = []

    idx = 0
    for token in tokens:
        if token.name.startswith('('):
            group_info.append(Group(idx, None, token.name))
        elif token.name == ')':
            for group in reversed(group_info):
                if group.end is None:
                    group.end = idx
        idx += 1
    return group_info


def get_capture_group(group_info, named_groups, group_ref):
    try:
        id = int(group_ref)
    except:
        id = named_groups[group_ref]
    search = 0
    for group in group_info:
        if group.klass == '(':
            search += 1
            if search == id:
                return group


# Splits conditionals into multiple regex parts.
def split_if_else(tokens, group_info, named_groups):
    for group in group_info:
        if group.klass == '(?<':
            iff = tokens[:]
            els = tokens[:]
            con_start = group.start
            con_end   = group.end

            ref = tokens[con_start + 1].name
            capture_group = get_capture_group(group_info, named_groups, ref)
            capture_group_modifier = tokens[capture_group.end + 1]

            if capture_group_modifier.name in ['?', '*'] or capture_group_modifier.name.startswith('{0,'):
                if capture_group_modifier.name == '?':
                    iff[capture_group.end + 1].name = ''
                elif capture_group_modifier.name == '*':
                    iff[capture_group.end + 1].name = '+'
                elif capture_group_modifier.name.startswith('{0,'):
                    iff[capture_group.end + 1].name[0:3] = '{1,'

                for idx in range(con_start, con_end):
                    if tokens[idx].name == '|':
                        els.pop(con_end)
                        iff[idx:con_end + 2] = []
                        iff[con_start:con_start + 3] = []
                        els[con_start:idx + 1] = []
                        els[capture_group.start:capture_group.end + 1] = [Token('('), Token(')')]
                        break

                tokens = iff
                tokens.append(Token('|'))
                tokens.extend(els)

            else:  # the easy case - 'else' is impossible
                past_iff = False
                for idx in range(con_start, con_end):
                    if iff[idx].name == '|':
                        iff = tokens[:idx]
                        iff.extend(tokens[con_end + 1:])
                        break
                iff.pop(con_start)
                iff.pop(con_start)
                iff.pop(con_start)
                tokens = iff
            break
    return tokens


class Token:
    def __init__(self, name, paras=None, pure=False):
        if paras is None:
            paras = []
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


def shift_reduce(stack, queue, named_groups, js_flags, dots_match_all):
    py_flags = 'iLmsux'
    done = False
    high = len(stack) - 1

    s0 = stack[high]     if len(stack) > 0 else Token('')
    s1 = stack[high - 1] if len(stack) > 1 else Token('')
    s2 = stack[high - 2] if len(stack) > 2 else Token('')

    if VERBOSE:
        for token in stack:
            console.log(token.resolve(), '\t', end='')
        console.log('')

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
        stack.pop()
        stack.extend([Token('(?='), Token('\\n'), Token('?'), Token('$'), Token(')')])

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
        if s0.name in py_flags:
            if s0.name == 'i':
                js_flags += 'i'
            elif s0.name == 'm':
                js_flags += 'm'
            elif s0.name == 's':
                # handled at end of method
                dots_match_all = True
            else:
                raise Error('Unsupported flag: ' + s0.name)

            stack.pop()
            s1.isModeGroup = True

        else:
            if s0.name == '(':
                s0.name = '<'

            newToken = Token('(?' + s0.name)
            stack[-2:] = [newToken]

    elif s1.name == '(?<':
        if s0.name == ')':
            stack[-1:] = [Token(''.join(s1.paras)), Token('>')]
            s1.paras = []
        else:
            s1.paras.append(s0.name)
            stack.pop()

    elif s1.name == '(?P':
        stack[-2:] = [Token('(?P' + s0.name)]

    elif s1.name == '(?P<':
        if s0.name == '>':
            named_groups[''.join(s1.paras)] = len(named_groups) + 1
            stack[-2:] = [Token('(')]
        else:
            s1.paras.append(s0.name)
            stack.pop()

    elif s1.name == '(?P=':
        if s0.name == ')':
            stack[-2:] = [Token('\\' + named_groups[s1.paras[0]])]
        elif not s1.paras:
            s1.paras.append(s0.name)
            stack.pop()
        else:
            s1.paras[0] += s0.name
            stack.pop()

    elif s1.name == '(?#':
        if s0.name == ')':
            stack = stack[:-2]
        else:
            stack = stack[:-1]

    # the shift in 'shift-reduce''
    else:
        if not queue:
            done = True
        else:
            stack.append(Token(queue[0], [], True))
            queue = queue[1:]

    return stack, queue, js_flags, dots_match_all, done


def translate(rgx):
    stack = []
    queue = list(rgx)

    js_flags = ''
    named_groups = {}

    dots_match_all = False
    nloop = 0

    while True:
        nloop += 1
        if nloop > 50:
            console.log("Failed to parse...")
            break

        stack, queue, js_flags, dots_match_all, done = shift_reduce(stack, queue, named_groups, js_flags, dots_match_all)
        if done:
            break

    group_info = generate_group_spans(stack)
    stack = split_if_else(stack, group_info, named_groups)

    resolvedTokens = []

    for token in stack:
        stringed = token.resolve()
        if dots_match_all and stringed == '.':
            stringed = '[\s\S]'
        resolvedTokens.append(stringed)
    return ''.join(resolvedTokens), resolvedTokens, js_flags, named_groups, group_info

pattern = r"^(<)?(\w+@\w+(?:\.\w+)+)(?(1)>|$)"
# pattern = r"(a)?(b)?(?(1)a|c)(?(2)b|d)"
print(pattern)
js_pattern, tokens, js_flags, named_groups, group_info = translate(pattern)
print(js_pattern)
print(' # '.join(tokens))
print(group_info)
