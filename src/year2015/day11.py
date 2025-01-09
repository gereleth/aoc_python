# Problem statement: https://adventofcode.com/2015/day/11

from itertools import pairwise

day_title = "Corporate Policy"

letters = "abcdefghijklmnopqrstuvwxyz"


class Password:
    increasing = {a: b for a, b in zip(letters[:-1], letters[1:])}
    increasing["z"] = None

    increments = {**increasing}
    increments["z"] = "a"

    def __init__(self, password: str, forbidden="iol"):
        self.letters = list(password)
        # skip forbidden letters when incrementing
        for char in forbidden:
            i = ord(char)
            self.increments[chr(i - 1)] = chr(i + 1)

    @property
    def has_increasing(self):
        increases = 0
        for a, b in pairwise(self.letters):
            if b == self.increasing[a]:
                increases += 1
                if increases == 2:
                    return True
            else:
                increases = 0

    @property
    def has_pairs(self):
        pair_at = -10
        for i, (a, b) in enumerate(pairwise(self.letters)):
            if a == b and pair_at < i - 1:
                if pair_at == -10:
                    pair_at = i
                else:
                    return True
        return False

    @property
    def is_valid(self):
        return self.has_increasing and self.has_pairs

    def increment(self):
        L = len(self.letters)
        for i, letter in enumerate(reversed(self.letters)):
            self.letters[L - 1 - i] = self.increments[letter]
            if letter != "z":
                break
        return self

    def __str__(self):
        return "".join(self.letters)


def test_has_increasing():
    assert Password("abc").has_increasing
    assert not Password("abd").has_increasing
    assert Password("hijklmmn").has_increasing
    assert not Password("abbceffg").has_increasing
    assert Password("xyz").has_increasing
    assert not Password("yzab").has_increasing


def test_has_pairs():
    assert Password("xxyy").has_pairs
    assert Password("abaabbcd").has_pairs
    assert Password("aaaa").has_pairs
    assert not Password("aaa").has_pairs


def test_increment():
    assert str(Password("abcdefgh").increment()) == "abcdefgj"
    assert str(Password("abcdefgz").increment()) == "abcdefha"
    assert str(Password("abcdefzz").increment()) == "abcdegaa"
    assert str(Password("abcdezzz").increment()) == "abcdfaaa"


def part1(text_input):
    password = Password(text_input).increment()
    while not password.is_valid:
        password.increment()
    return str(password)


def part2(text_input):
    a = part1(text_input)
    b = part1(a)
    return b
