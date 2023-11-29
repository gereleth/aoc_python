# Problem statement: https://adventofcode.com/2015/day/5

day_title = "Doesn't He Have Intern-Elves For This?"

VOWELS = "aeiou"
FORBIDDEN = {"ab", "cd", "pq", "xy"}


def has_enough_vowels(string):
    n = 0
    for char in string:
        n += char in VOWELS
        if n >= 3:
            return True
    return False


def test_has_enough_vowels():
    assert has_enough_vowels("aaa") is True
    assert has_enough_vowels("aa") is False
    assert has_enough_vowels("xyzyzy") is False


def has_doubles(string):
    for char1, char2 in zip(string[:-1], string[1:]):
        if char1 == char2:
            return True
    return False


def test_has_doubles():
    assert has_doubles("xxx") is True
    assert has_doubles("xyz") is False
    assert has_doubles("abcdee") is True


def has_forbidden(string):
    for char1, char2 in zip(string[:-1], string[1:]):
        if char1 + char2 in FORBIDDEN:
            return True
    return False


def test_has_forbidden():
    assert has_forbidden("abcd") is True
    assert has_forbidden("acbd") is False
    assert has_forbidden("dfdfdfxydf") is True
    assert has_forbidden("dfdfdfxdydf") is False


def is_nice_1(string):
    return (
        has_enough_vowels(string) and has_doubles(string) and not has_forbidden(string)
    )


def test_is_nice_1():
    assert is_nice_1("ugknbfddgicrmopn") is True
    assert is_nice_1("aaa") is True
    assert is_nice_1("jchzalrnumimnmhp") is False
    assert is_nice_1("haegwjzuvuyypxyu") is False
    assert is_nice_1("dvszwmarrgswjxmb") is False


def part1(text_input):
    total = 0
    for line in text_input.split("\n"):
        total += is_nice_1(line)
    return total


def test_part_1():
    text = """
ugknbfddgicrmopn
aaa
jchzalrnumimnmhp
haegwjzuvuyypxyu
dvszwmarrgswjxmb
""".strip()
    assert part1(text) == 2


def has_repeating_pair(string):
    seen_pairs = {}
    length = len(string)
    for i, (char1, char2) in enumerate(zip(string[:-1], string[1:])):
        pair = char1 + char2
        first_position = seen_pairs.get(pair, length)
        if first_position <= i - 2:
            return True
        if pair not in seen_pairs:
            seen_pairs[pair] = i
    return False


def test_has_repeating_pair():
    assert has_repeating_pair("aa") is False
    assert has_repeating_pair("aaa") is False
    assert has_repeating_pair("aaaa") is True
    assert has_repeating_pair("aabbccddaaee") is True
    assert has_repeating_pair("ababab") is True


def has_triplet(string):
    for i, char in enumerate(string[:-2]):
        if char == string[i + 2]:
            return True
    return False


def test_has_triplet():
    assert has_triplet("aa") is False
    assert has_triplet("abcdefg") is False
    assert has_triplet("aaa") is True
    assert has_triplet("aaaa") is True
    assert has_triplet("abcdedcba") is True
    assert has_triplet("abcded") is True


def is_nice_2(string):
    return has_repeating_pair(string) and has_triplet(string)


examples = [
    ("ugknbfddgicrmopn", 1, None),
    ("aaa", 1, None),
    ("jchzalrnumimnmhp", 0, None),
    ("haegwjzuvuyypxyu", 0, None),
    ("dvszwmarrgswjxmb", 0, None),
    ("qjhvhtzxzqqjkmpb", None, 1),
    ("xxyxx", None, 1),
    ("uurcxstgmygtbstg", None, 0),
    ("ieodomkazucvgmuy", None, 0),
]


def test_is_nice_2():
    assert is_nice_2("qjhvhtzxzqqjkmpb") is True
    assert is_nice_2("xxyxx") is True
    assert is_nice_2("uurcxstgmygtbstg") is False
    assert is_nice_2("ieodomkazucvgmuy") is False


def part2(text_input):
    total = 0
    for line in text_input.split("\n"):
        total += is_nice_2(line)
    return total


def test_part_2():
    text = """
qjhvhtzxzqqjkmpb
xxyxx
uurcxstgmygtbstg
ieodomkazucvgmuy
""".strip()
    assert part2(text) == 2
