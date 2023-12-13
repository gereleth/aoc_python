# Problem statement: https://adventofcode.com/2023/day/12

from functools import cache

day_title = "Hot Springs"

example_input = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
""".strip()


def fits(chars: str, num: int, index: int):
    """
    Check if we can place a span of size num at index in chars
    """
    cc = chars[index : index + num]
    if len(cc) < num or "." in cc:
        return False
    before = index - 1
    if before > 0 and chars[before] == "#":
        return False
    after = index + num
    if after < len(chars) and chars[after] == "#":
        return False
    return True


def test_fits():
    assert fits("???", 1, 0)
    assert fits("???", 1, 1)
    assert fits("???", 1, 2)
    assert not fits("???", 1, 3)
    assert fits("?#??", 2, 0)
    assert fits("?#??", 2, 1)
    assert not fits("?#??", 2, 2)


def count_single_num_placements(chars, num):
    """
    Count ways we can place a single span of size num in this string
    """
    first_broken = next((i for i, c in enumerate(chars) if c == "#"), len(chars))
    if first_broken < len(chars):
        start = first_broken - num + 1
        end = first_broken
        n = 0
        for index in range(start, end + 1):
            if fits(chars, num, index):
                n += int("#" not in chars[index + num + 1 :])
        return n
    n = 0
    for c, char in enumerate(chars[: len(chars) - num + 1]):
        if char == ".":
            continue
        n += fits(chars, num, c)
    return n


def test_count_single_too_short():
    assert count_single_num_placements("", 1) == 0
    assert count_single_num_placements("", 2) == 0
    assert count_single_num_placements("", 3) == 0
    assert count_single_num_placements("?", 2) == 0
    assert count_single_num_placements("?", 3) == 0
    assert count_single_num_placements("??", 3) == 0


def test_count_single_questions():
    assert count_single_num_placements("????", 1) == 4
    assert count_single_num_placements("??????", 1) == 6
    assert count_single_num_placements("????", 2) == 3
    assert count_single_num_placements("??????", 2) == 5
    assert count_single_num_placements("????", 3) == 2
    assert count_single_num_placements("??????", 3) == 4


def test_count_single_with_dots():
    assert count_single_num_placements("?..?", 1) == 2
    assert count_single_num_placements("....", 1) == 0
    assert count_single_num_placements("?..?", 2) == 0
    assert count_single_num_placements("?.??", 2) == 1
    assert count_single_num_placements("???.??", 3) == 1
    assert count_single_num_placements("???.????", 3) == 3


def test_count_single_with_brokens():
    assert count_single_num_placements("#???", 1) == 1
    assert count_single_num_placements(".#..", 1) == 1
    assert count_single_num_placements(".##.", 1) == 0
    assert count_single_num_placements(".#...?#?.", 1) == 0
    assert count_single_num_placements("?#??????", 2) == 2
    assert count_single_num_placements("??#.??", 3) == 1
    assert count_single_num_placements("???.?##?", 3) == 2


@cache
def place_to_the_left(chars, nums):
    """
    Place each span as far left as possible
    Returns list of start indexes for every span
    Or an empty list if placing is impossible
    """
    num, *other_nums = nums
    for c, char in enumerate(chars[: len(chars) - num + 1]):
        if c > 0 and chars[c - 1] == "#":
            break
        if fits(chars, num, c):
            leftover_chars = chars[c + num + 1 :]
            if len(other_nums) > 0:
                other_placements = place_to_the_left(leftover_chars, tuple(other_nums))
                if len(other_placements) == len(other_nums):
                    return [c] + [c + num + 1 + o for o in other_placements]
            elif "#" in leftover_chars:
                continue
            else:
                return [c]
    return []


def test_place_to_the_left():
    assert tuple(place_to_the_left("???", (1,))) == (0,)
    assert tuple(place_to_the_left("???", (1, 1))) == (0, 2)
    assert tuple(place_to_the_left("???", (1, 2))) == tuple()
    assert tuple(place_to_the_left("?#???", (1, 2))) == (1, 3)
    assert tuple(place_to_the_left("?.????", (2, 1))) == (2, 5)
    assert tuple(place_to_the_left("?.?.?.", (2, 1))) == tuple()
    assert tuple(place_to_the_left("????.#..????", (1, 4))) == (5, 8)


def place_to_the_right(chars, nums):
    """
    Place each span as far right as possible
    Returns list of rightmost start indexes for every span
    Or an empty list if placing is impossible
    """
    rnums = tuple(reversed(nums))
    rchars = "".join(reversed(chars))
    placements = place_to_the_left(rchars, rnums)
    if len(placements) == 0:
        return placements
    return [len(chars) - num - i for num, i in zip(nums, reversed(placements))]


def test_place_to_the_right():
    assert tuple(place_to_the_right("???", (1,))) == (2,)
    assert tuple(place_to_the_right("???", (1, 1))) == (0, 2)
    assert tuple(place_to_the_right("???", (1, 2))) == tuple()
    assert tuple(place_to_the_right("?#???", (1, 2))) == (1, 3)
    assert tuple(place_to_the_right("?.????", (2, 1))) == (2, 5)
    assert tuple(place_to_the_right("?.??????", (2, 1))) == (4, 7)
    assert tuple(place_to_the_right("?.?.?.", (2, 1))) == tuple()
    assert tuple(place_to_the_right("????.#..????", (1, 4))) == (5, 8)


@cache
def count_solutions(chars, nums):
    if len(nums) == 0:
        return int("#" not in chars)
    if len(nums) == 1:
        return count_single_num_placements(chars, nums[0])
    lefts = place_to_the_left(chars, nums)
    rights = place_to_the_right(chars, nums)
    if len(lefts) < len(nums):
        return 0
    # attempt to split task into subtasks that can be solved independently
    # For example, in "??....?? 1,1" the ones don't care about each other
    # So we can split the task into two and then multiply their solution counts.
    # With splits part 2 takes 2.1 s on my machine
    # Without splits it's... 2.2 seconds
    # I thought the benefit would be more significant =)
    splits = [(chars, nums)]
    splits = []
    num_start = 0
    char_start = 0
    for i, (num, left, right) in enumerate(zip(nums, lefts, rights)):
        next_left = lefts[i + 1] if i + 1 < len(nums) else len(chars) + 1
        can_split = right + num < (next_left)
        if can_split:
            if left < right:
                nums_before = nums[num_start : i + 1]
                chars_before = chars[char_start : right + num]
            else:
                # this span is fully solved, don't include it in prev segment
                nums_before = nums[num_start:i]
                chars_before = chars[char_start:left]
            splits.append((chars_before, nums_before))
            char_start = next_left
            num_start = i + 1
    if len(splits) == 0:
        raise ValueError("no splits")
    elif len(splits) > 1:
        # we could split up the task into independent portions
        # total solution count is given by the product of their solution counts
        total = 1
        for split_chars, split_nums in splits:
            total *= count_solutions(split_chars.strip("."), split_nums)
            if total == 0:
                return 0
        return total
    else:
        # no luck splitting up, so we have to branch out
        # look for a span in the middle (to minimize the size of leftovers)
        # try every possible placement and sum the solution counts
        total = 0
        i = len(nums) // 2
        num = nums[i]
        for place in range(lefts[i], rights[i] + 1):
            if fits(chars, num, place):
                chars_before = chars[0 : max(0, place - 1)].strip(".")
                nums_before = nums[0:i]
                count_before = count_solutions(chars_before, nums_before)
                chars_after = chars[place + num + 1 :].strip(".")
                nums_after = nums[i + 1 :]
                count_after = count_solutions(chars_after, nums_after)
                total += count_after * count_before
        return total


def unfold(line, n=5):
    a, b = line.split()
    return "?".join([a] * n) + " " + ",".join([b] * n)


def parse(line):
    chars, nums = line.split()
    nums = tuple(int(i) for i in nums.split(","))
    return chars, nums


def test_count_solutions():
    assert count_solutions(*parse("? 1")) == 1
    assert count_solutions(*parse("?? 1")) == 2
    assert count_solutions(*parse("??? 1,1")) == 1
    assert count_solutions(*parse("??.??.?? 1,2,1")) == 4
    assert count_solutions(*parse("???.??????????? 1,3,1,3")) == 31
    assert count_solutions(*parse("??.?###????????? 2,4,4")) == 9
    assert count_solutions(*parse("#??????????# 1,3,3,1")) == 3
    assert count_solutions(*parse("#??????????# 1,3,3,1")) == 3


def test_part1_1():
    ans = [1, 4, 1, 1, 4, 10]
    for line, cnt in zip(example_input.split("\n"), ans):
        assert count_solutions(*parse(line)) == cnt
        print("...")


def test_part_2():
    ans = [1, 16384, 1, 16, 2500, 506250]
    for i, (line, cnt) in enumerate(zip(example_input.split("\n"), ans)):
        assert count_solutions(*parse(unfold(line))) == cnt


def part1(text_input):
    total = 0
    for line in text_input.split("\n"):
        total1 = count_solutions(*parse(line))
        total += total1
    return total


def part2(text_input):
    total = 0
    for line in text_input.split("\n"):
        total2 = count_solutions(*parse(unfold(line)))
        total += total2
    return total
