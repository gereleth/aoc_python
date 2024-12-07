# Problem statement: https://adventofcode.com/2024/day/5

from typing import List, DefaultDict, Set
from collections import defaultdict

day_title = "Print Queue"


def parse_input(text_input: str):
    rules_text, updates_text = text_input.split("\n\n")
    rules = defaultdict(set)
    for rule in rules_text.split("\n"):
        a, b = rule.split("|")
        rules[a].add(b)
    updates = [update.split(",") for update in updates_text.split("\n")]
    return rules, updates


def is_ordered(update: List[str], after: DefaultDict[str, Set[str]]) -> bool:
    for i1, p1 in enumerate(update[:-1]):
        for i2 in range(i1 + 1, len(update)):
            p2 = update[i2]
            if p1 in after[p2]:
                return False
    return True


def part1(text_input: str) -> int:
    rules, updates = parse_input(text_input)
    total = 0
    for update in updates:
        if is_ordered(update, rules):
            total += int(update[len(update) // 2])
    return total


def reorder(update: List[str], rules: DefaultDict[str, Set[str]]) -> List[str]:
    """Merge sort list of pages according to rules"""
    # we could make this even more efficient by only sorting the parts
    # that contain the middle element
    # but this is fast enough for me =)
    to_sort = [(0, set(update))]
    while len(to_sort) > 0:
        index, unordered = to_sort.pop()
        page = unordered.pop()
        before = unordered.difference(rules[page])
        after = unordered.intersection(rules[page])
        page_index = index + len(before)
        update[page_index] = page
        if len(before) == 1:
            update[index] = before.pop()
        elif len(before) > 0:
            to_sort.append((index, before))
        if len(after) == 1:
            update[page_index + 1] = after.pop()
        elif len(after) > 0:
            to_sort.append((page_index + 1, after))
    return update


def part2(text_input: str) -> int:
    rules, updates = parse_input(text_input)
    total = 0
    for update in updates:
        if not is_ordered(update, rules):
            update = reorder(update, rules)
            total += int(update[len(update) // 2])
    return total


test_input = """
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 143


def test_part2():
    assert part2(test_input) == 123
