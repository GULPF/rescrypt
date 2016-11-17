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

    rgx = re.compile(r"(a)?(b)?(?(1)a|c)(?(2)b)")
    autoTester.check(rgx.match('abab').group())
    autoTester.check(rgx.match('aa').group())
    autoTester.check(rgx.match('bcb').group())
    autoTester.check(rgx.match('c').group())
    autoTester.check(rgx.match('abcb'))

    rgx = re.compile(r"(a)?(b)?(?(1)a|c)(?(2)b|d)")
    autoTester.check(rgx.match("abab").group())
    autoTester.check(rgx.match("aad").group())
    autoTester.check(rgx.match("bcb").group())
    autoTester.check(rgx.match("cd").group())