# Problem statement: https://adventofcode.com/2015/day/10

day_title = "Elves Look, Elves Say"


def iter_repeating_groups(string):
    # '11222311' -> '11', '222', '3', '11'
    group = string[0]
    for char in string[1:]:
        if group[0] == char:
            group += char
        else:
            yield group
            group = char
    yield group


def look_and_say(string):
    result = ""
    for group in iter_repeating_groups(string):
        result += str(len(group)) + group[0]
    return result


def test_look_and_say():
    assert look_and_say("1") == "11"
    assert look_and_say("11") == "21"
    assert look_and_say("21") == "1211"
    assert look_and_say("1211") == "111221"
    assert look_and_say("111221") == "312211"


def part1(text_input):
    string = text_input.strip()
    for i in range(40):
        string = look_and_say(string)
    return len(string)


def part2(text_input):
    string = text_input.strip()
    for i in range(50):
        string = look_and_say(string)
    return len(string)
