# Problem statement: https://adventofcode.com/2015/day/8

from ast import literal_eval
import json

day_title = "Matchsticks"


def code_string_difference(string):
    code_len = len(string)
    str_len = len(literal_eval(string))
    return code_len - str_len


def test_compute_difference():
    assert code_string_difference(r'""') == 2
    assert code_string_difference(r'"abc"') == 2
    assert code_string_difference(r'"aaa\"aaa"') == 3
    assert code_string_difference(r'"\x27"') == 5


def part1(text_input):
    diff = 0
    for line in text_input.split("\n"):
        diff += code_string_difference(line)
    return diff


def encode_code(string):
    return json.dumps(string)


def test_encode_code():
    assert encode_code(r'""') == r'"\"\""'
    assert encode_code(r'"abc"') == r'"\"abc\""'
    assert encode_code(r'"aaa\"aaa"') == r'"\"aaa\\\"aaa\""'
    assert encode_code(r'"\x27"') == r'"\"\\x27\""'


def part2(text_input):
    diff = 0
    for line in text_input.split("\n"):
        diff += len(encode_code(line)) - len(line)
    return diff


def test_part2():
    text = r"""
""
"abc"
"aaa\"aaa"
"\x27"
    """.strip()
    assert part2(text) == 19
