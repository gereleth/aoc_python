# Problem statement: https://adventofcode.com/2024/day/5

from typing import List

day_title = "Print Queue"


def parse_input(text_input: str):
    rules_text, updates_text = text_input.split("\n\n")
    rules = set(tuple(map(int, rule.split("|"))) for rule in rules_text.split("\n"))
    updates = [list(map(int, update.split(","))) for update in updates_text.split("\n")]
    return rules, updates


def is_ordered(update: List[int], rules) -> bool:
    for i1, p1 in enumerate(update[:-1]):
        for i2 in range(i1 + 1, len(update)):
            p2 = update[i2]
            if (p2, p1) in rules:
                return False
    return True


def part1(text_input: str) -> int:
    rules, updates = parse_input(text_input)
    total = 0
    for update in updates:
        if is_ordered(update, rules):
            total += update[len(update) // 2]
    return total


def get_correct_order(rules):
    # chip away at the rules list by looking for pages that always come first
    # or always come last
    rules = list(rules)
    firsts = []
    lasts = []
    while len(rules) > 0:
        rules_count = len(rules)
        before = set(a for a, _ in rules)
        after = set(b for _, b in rules)
        middles = before.intersection(after)
        first = before.difference(middles)
        last = after.difference(middles)
        firsts.append(first)
        lasts.append(last)
        rules = [(a, b) for (a, b) in rules if a not in first and b not in last]
        if len(rules) == rules_count:
            # happens with the full set of rules from the task input =)
            raise ValueError("No ordering found, rules might be cyclic")
        elif len(rules) == 0:
            firsts.append(middles)
    return [page for pages in firsts for page in pages] + [
        page for pages in lasts[::-1] for page in pages
    ]


def reorder(update, rules):
    update = set(update)
    relevant = set((a, b) for (a, b) in rules if a in update and b in update)
    correct = get_correct_order(relevant)
    return [i for i in correct if i in update]


def part2(text_input: str) -> int:
    rules, updates = parse_input(text_input)
    total = 0
    for update in updates:
        if not is_ordered(update, rules):
            update = reorder(update, rules)
            total += update[len(update) // 2]
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
