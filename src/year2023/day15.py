# Problem statement: https://adventofcode.com/2023/day/15

day_title = "Lens Library"

example_input = """
rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7
""".strip()


def holiday_ascii_hash(text):
    res = 0
    for char in text:
        if char == "\n":
            continue
        n = ord(char)
        res += n
        res *= 17
        res = res % 256
    return res


def test_holiday_ascii():
    assert holiday_ascii_hash("rn=1") == 30
    assert holiday_ascii_hash("cm-") == 253


def part1(text_input):
    steps = text_input.split(",")
    total = sum(holiday_ascii_hash(step) for step in steps)
    return total


def part2(text_input):
    boxes = [[] for _ in range(256)]
    # follow instruction to put lenses in boxes
    for step in text_input.replace("\n", "").split(","):
        if step.endswith("-"):
            label = step[:-1]
            operation = "-"
        else:
            label = step[:-2]
            operation = step[-2]
            strength = int(step[-1])
        box_index = holiday_ascii_hash(label)
        box = boxes[box_index]
        if operation == "=":
            replace_idx = next(
                (
                    i
                    for i, (lens_label, lens_strength) in enumerate(box)
                    if lens_label == label
                ),
                -1,
            )
            if replace_idx >= 0:
                box[replace_idx] = (label, strength)
            else:
                box.append((label, strength))
        elif operation == "-":
            boxes[box_index] = [lens for lens in box if lens[0] != label]
    # sum up total focusing power
    total = 0
    for box_index, lenses in enumerate(boxes):
        for li, (label, strength) in enumerate(lenses):
            total += (box_index + 1) * (li + 1) * strength
    return total


def test_part1():
    assert part1(example_input) == 1320


def test_part2():
    assert part2(example_input) == 145
