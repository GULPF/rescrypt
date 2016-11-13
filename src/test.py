from re import compile

good = []
bad  = []


def htmlTag(info):
    return "<{0} class={1}>{2}</{0}>".format(info["tag"], info["class"], info["content"])


def testRegExp(desc, pyPattern, input, output):
    rgx = compile(pyPattern)
    m = rgx.search(input)
    if m.group(0) == output:
        good.append(desc)
    else:
        bad.append((desc, rgx.pattern + m.groups(0) + " != " + output))


def eq(desc, v1, v2):
    if v1 == v2:
        good.append(desc)
    else:
        # TODO: replace with something smart
        if v1.groups:
            v1 = "match"
        bad.append((desc, v1 + " ==  " + v2))


def neq(desc, v1, v2):
    if v1 != v2:
        good.append(desc)
    else:
        bad.append((desc, v1 + " != " + v2))


def arrayEq(desc, arr1, arr2):
    if len(arr1) != len(arr2):
        bad.append((desc, "[" + arr1 + "] == [" + arr2 + "]"))

    for i in range(0, len(arr1)):
        if arr1[i] != arr2[i]:
            bad.append((desc, "[" + arr1 + "] == [" + arr2 + "]"))
            return
    good.append(desc)


badPrefix  = htmlTag({"tag": "span", "class": "bad", "content": "--"})
goodPrefix = htmlTag({"tag": "span", "class": "good", "content": "++"})


def printResult():
    for desc in bad:
        log(badPrefix + "[" + desc[0] + "]" + htmlTag({"tag": "span", "class": "bad", "content": desc[1]}))

    log()

    for desc in good:
        log(goodPrefix + "[" + desc + "]")


def log(*parts):
    el = document.getElementById("out")
    html = ""
    for msg in parts:
        html += htmlTag({"tag": "span", "class": "element", "content": msg})
    el.innerHTML += html + "<br>"


def browserTest():
    testRegExp("Bell character",        r"\a",           "--",          "")
    testRegExp("Python $",              r".$",           "abc\ndef\n",  "f")
    testRegExp("Comment group",         r"a(?#foobar)b", "ab",          "ab")
    testRegExp("Repeat",                r"a{,2}",        "aab",         "aa")
    testRegExp("Repeat in group",       r"(?:a{,2})",    "aab",         "aa")
    testRegExp("Escaped repeat",        r"\{,2}",        "{,2}",        "{,2}")
    testRegExp("Case-switch group",     r"(?i)aba",      "aBA",         "aBA")
    testRegExp("Single-line group",     r"(?s).*",       "ab\n\ndef",   "ab\n\ndef")
    testRegExp("Single-line group with literal dot",   r"(?s)\.",  "_._", ".")
    testRegExp("Look-ahead",            r"ab(?=c)",      "abc",         "ab")
    testRegExp("Named group", r"(?P<name>foo)", "foo", "foo")

    try:
        m = compile(r"(?)")
        bad.append(("(?) should fail", ""))
    except:
        good.append("(?) should fail")

    # re.match
    rgx = compile("foo")
    neq("Simple match", rgx.match("foobar"),  None)
    eq("Match later", rgx.match("_foobar"), None)
    eq("Failed match", rgx.match("baz"), None)
    neq("Match later with offset", rgx.match("_foobar", 1), None)
    eq("Failed match due to end", rgx.match("foobar", 0, 2), None)
    eq("Failed match due to start", compile("^a").match("aa", 1), None)
    rgx = compile("f?oo?")
    neq("Prunned match due to end", rgx.match("foo", 0, 2), None)
    neq("Prunned match due to start", rgx.match("foo", 1), None)
    eq("Failed ^ with start", compile("^ab").match("\nab", 1), None)
    neq("^ with start", compile("(?m)^ab").match("\nab", 1), None)
    neq("^ in group with start", compile("(?m)(^|x)ab").match("\nab", 1), None)
    eq("^ in group with start without multi-line", compile("(^|x)ab").match("\nab", 1), None)
    neq("Inverted set with start", compile("[^a]").match("bb", 1), None)

    # re.split
    rgx = compile("\W+")
    splitted = rgx.split('Words, words, words.')
    arrayEq("Simple split", splitted, ['Words', 'words', 'words', ''])
    splitted = rgx.split('Words, words, words.', 1)
    arrayEq("Split with limit", splitted, ['Words', 'words, words.'])

    # match object
    m = compile(r"(\w)(\w)(\w)").match("abc")
    eq("group(0)", m.group(0), "abc")
    eq("group(1)", m.group(1), "a")
    arrayEq("group(1, 2)", m.group(1, 2), ["a", "b"])
    arrayEq("group(2, 1)", m.group(2, 1), ["b", "a"])
    eq("group 0 access by brackets", m[0], "abc")
    eq("group 1 access by brackets", m[1], "a")
    m = compile(r"(?P<name>foo)").match("foo")
    eq("group('name')", m.group('name'), "foo")

    printResult()

browserTest()
