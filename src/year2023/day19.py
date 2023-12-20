# Problem statement: https://adventofcode.com/2023/day/19

from util.segments import Segment1D

day_title = "Aplenty"

example_input = """
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}
""".strip()


def parse_input(text_input: str):
    workflows_text, parts_text = text_input.split("\n\n")

    parts = []
    for line in parts_text.split("\n"):
        part = {}
        props = line[1:-1].split(",")
        for prop in props:
            key, value = prop.split("=")
            part[key] = int(value)
        parts.append(part)

    workflows = {}
    for line in workflows_text.split("\n"):
        name, conds = line[:-1].split("{")
        workflows[name] = []
        for cond in conds.split(","):
            if ":" in cond:
                check, destination = cond.split(":")
                property = check[0]  # x, m, a or s
                comparison = check[1]  # < or >
                value = int(check[2:])  # compare with this
                workflows[name].append(
                    ("check", (property, comparison, value), destination)
                )
            else:
                workflows[name].append(("send", None, cond))
    return workflows, parts


def fits(part, property, comparison, value):
    property_value = part[property]
    return (comparison == "<" and property_value < value) or (
        comparison == ">" and property_value > value
    )


def part1(text_input: str):
    workflows, parts = parse_input(text_input)
    first_workflow_key = "in"
    total = 0
    for part in parts:
        workflow_key = first_workflow_key
        while True:
            workflow = workflows[workflow_key]
            destination = None
            for step, data, send_to in workflow:
                if step == "send":
                    destination = send_to
                    break
                if fits(part, *data):
                    destination = send_to
                    break
            if destination == "A":
                total += sum(part.values())
                break
            elif destination == "R":
                break
            else:
                workflow_key = destination
    return total


def split_parts(parts, property, comparison, value):
    segment = parts[property]
    if comparison == "<":
        other_segment = Segment1D(1, value - 1)
    else:
        other_segment = Segment1D(value + 1, 4000)
    yes_segment = segment.intersection(other_segment)
    no_segment = segment.difference(other_segment)[0]
    yes_parts = {**parts, property: yes_segment}
    no_parts = {**parts, property: no_segment}
    return yes_parts, no_parts


def total_combinations(parts):
    total = 1
    for segment in parts.values():
        total *= len(segment)
    return total


def part2(text_input: str):
    workflows, _ = parse_input(text_input)
    parts = {
        "a": Segment1D(1, 4000),
        "x": Segment1D(1, 4000),
        "s": Segment1D(1, 4000),
        "m": Segment1D(1, 4000),
    }
    total = 0
    queue = [("in", parts)]
    while len(queue) > 0:
        workflow_key, parts = queue.pop()
        if workflow_key == "A":
            total += total_combinations(parts)
            continue
        elif workflow_key == "R":
            continue
        workflow = workflows[workflow_key]
        destination = None
        for step, data, send_to in workflow:
            if step == "send":
                destination = send_to
                break
            property, comparison, value = data
            yes_parts, no_parts = split_parts(parts, property, comparison, value)
            queue.append((send_to, yes_parts))
            parts = no_parts
        queue.append((destination, parts))
    return total


def test_part1():
    assert part1(example_input) == 19114


def test_part2():
    assert part2(example_input) == 167409079868000
