import re


def run(autoTester):
    # Flag Tests
    autoTester.check(re.T)
    autoTester.check(re.I)
    autoTester.check(re.IGNORECASE)
    autoTester.check(re.M)
    autoTester.check(re.MULTILINE)
    autoTester.check(re.S)
    autoTester.check(re.DOTALL)
    autoTester.check(re.U)
    autoTester.check(re.UNICODE)
    autoTester.check(re.X)
    autoTester.check(re.VERBOSE)
    autoTester.check(re.A)
    autoTester.check(re.ASCII)

    autoTester.check(re.match(r'(?P<name>foo)', 'foo').group('name'))
    autoTester.check(re.fullmatch(r'(?P<name>foo)(?P=name)', 'foofoo').group())

    # conditionals
    rgx = re.compile(r'(a)?(b)?(?(1)a|c)(?(2)b)')
    autoTester.check(rgx.match('abab').group())
    autoTester.check(rgx.match('aa').group())
    autoTester.check(rgx.match('bcb').group())
    autoTester.check(rgx.match('c').group())
    autoTester.check(rgx.match('abcb'))
    rgx = re.compile(r'(a)?(b)?(?(1)a|c)(?(2)b|d)')
    autoTester.check(rgx.match('abab').group())
    autoTester.check(rgx.match('aad').group())
    autoTester.check(rgx.match('bcb').group())
    autoTester.check(rgx.match('cd').group())

    autoTester.check(re.search(r'a{,2}', '').group())
    autoTester.check(re.search(r'a{,2}', 'aab').group())
    autoTester.check(re.search(r'(?:a{,2})', 'aab').group())

    autoTester.check(re.search(r'.$',           'abc\ndef\n').group())
    autoTester.check(re.search(r'a(?#foobar)b', 'ab').group())
    autoTester.check(re.search(r'(?i)aba',      'aBA').group())
    autoTester.check(re.search(r'(?s).*',       'ab\n\ndef').group())

    # start/end stuff

    rgx = re.compile('foo')
    autoTester.check(rgx.match('foobar').group())
    autoTester.check(rgx.match('_foobar'))
    autoTester.check(rgx.match('baz'))
    autoTester.check(rgx.match('_foobar', 1).group())
    autoTester.check(rgx.match('foobar', 0, 2))
    autoTester.check(re.compile('^a').match('aa', 1))

    rgx = re.compile('f?oo?')
    autoTester.check(rgx.match('foo', 0, 2).group())
    autoTester.check(rgx.match('foo', 1).group())
    autoTester.check(re.compile(r'^ab').match('\nab', 1))
    autoTester.check(re.compile(r'(?m)^ab').match('\nab', 1).group())
    autoTester.check(re.compile(r'(?m)(^|x)ab').match('\nab', 1).group())
    autoTester.check(re.compile(r'(^|x)ab').match('\nab', 1))
    autoTester.check(re.compile(r'[^a]').match('bb', 1).group())

    match = re.compile(r'()(?P<name>foo)').match('foo')
    autoTester.check(match.group('name'))
    autoTester.check(match.lastgroup)
    autoTester.check(match.lastindex)
    autoTester.check(match.groupdict()['name'])

    match = re.compile(r"(\w)(\w)(\w)").match("abc")
    autoTester.check(match.group(0))
    autoTester.check(match.group(1))
    autoTester.check(match.group(1, 2))
    autoTester.check(match.group(2, 1))

    match = re.compile(r"(\d+)\.?(\d+)?").match("24")
    #autoTester.check(match.groups())
    autoTester.check(match.groups(0))
    autoTester.check(match.group(2))
    match = re.compile(r"abc").search("__abc__")
    autoTester.check(match.start())
    autoTester.check(match.end())

    # findall
    finds = re.compile(r"a(?P<name>.)(.)").findall("a12a34a56")
    autoTester.check(finds[0])
    autoTester.check(finds[1])
    autoTester.check(finds[2])

    rgx = re.compile(r"\W+")
    txt = 'Words, words, words.'
    autoTester.check(rgx.split(txt))
    autoTester.check(rgx.split(txt, 1))
