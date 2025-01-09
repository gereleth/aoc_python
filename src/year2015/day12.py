# Problem statement: https://adventofcode.com/2015/day/12

import re
import json

day_title = "JSAbacusFramework.io"


def part1(text_input):
    total = 0
    for match in re.finditer(r"(-?\d+)", text_input):
        total += int(match.group())
    return total


def test_part1():
    assert part1("[1,2,3]") == 6
    assert part1('{"a":2,"b":4}') == 6
    assert part1("[[[3]]]") == 3
    assert part1('{"a":{"b":4},"c":-1}') == 3


def part2(text_input):
    data = json.loads(text_input)
    if not isinstance(data, list):
        data = [data]
    total = 0
    while data:
        item = data.pop()
        if isinstance(item, list):
            data.extend(item)
        elif isinstance(item, dict):
            has_red = any(v == "red" for v in item.values())
            if not has_red:
                data.extend(item.values())
        elif isinstance(item, int):
            total += item
    return total


def test_part2():
    assert part2("""[1,{"c":"red","b":2},3]""") == 4
    assert part2("""[1,"red","b",2,3]""") == 6
