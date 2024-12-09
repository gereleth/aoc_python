# Problem statement: https://adventofcode.com/2024/day/9

from collections import defaultdict
import heapq
from random import randint

day_title = "Disk Fragmenter"


def part1(text_input: str) -> int:
    # create disk map from input
    disk = []
    file_id = 0
    is_file = True
    for char in text_input:
        n = int(char)
        if is_file:
            disk.extend([file_id] * n)
            file_id += 1
        else:
            disk.extend([-1] * n)
        is_file = not is_file

    # do the fragmentation
    index = 0
    while index < len(disk):
        if disk[index] != -1:
            index += 1
            continue
        last = -1
        while last == -1:
            last = disk.pop()
        disk[index] = last
        index += 1

    # calculate checksum
    checksum = sum(index * file_id for index, file_id in enumerate(disk))
    return checksum


def rearrange_files_part_2(text_input: str):
    # disk map:
    # list of (id, index, size) for files
    # dict {size: heap of indexes} for empty spaces
    files = []
    empty = defaultdict(list)

    file_id = 0
    is_file = True
    index = 0
    for char in text_input:
        n = int(char)
        if is_file:
            files.append((file_id, index, n))
            file_id += 1
        elif n > 0:
            heapq.heappush(empty[n], index)
        index += n
        is_file = not is_file

    # move files into leftmost empty spaces
    for f, (file_id, file_index, file_size) in enumerate(files[::-1]):
        empty_index, empty_size = min(
            (
                (positions[0], size)
                for size, positions in empty.items()
                if len(positions) > 0 and (size >= file_size)
            ),
            default=(0, 0),
        )
        if empty_size == 0 or file_index < empty_index:
            # either nowhere to put this file at all
            # or would have to move it to the right
            continue
        # put file at the empty space
        files[-f - 1] = (file_id, empty_index, file_size)
        # remove this empty space from heap
        heapq.heappop(empty[empty_size])
        # possibly add a new leftover empty space
        new_empty_size = empty_size - file_size
        if new_empty_size > 0:
            new_empty_index = empty_index + file_size
            heapq.heappush(empty[new_empty_size], new_empty_index)

    return files


def calculate_checksum(files):
    checksum = 0
    for file_id, index, size in files:
        checksum += file_id * (size * index + size * (size - 1) // 2)
    return checksum


def part2(text_input: str) -> int:
    files = rearrange_files_part_2(text_input)
    return calculate_checksum(files)


# slow solution that I submitted from


def rearrange_files_part_2_slow(text_input: str) -> int:
    # disk map - array of (id, index, size) for files
    # and (index, size) for empty spaces
    files = []
    empty = []

    file_id = 0
    is_file = True
    index = 0
    for char in text_input:
        n = int(char)
        if is_file:
            files.append((file_id, index, n))
            file_id += 1
        else:
            empty.append((index, n))
        index += n
        is_file = not is_file

    # move files into leftmost empty spaces
    for f, (file_id, file_index, file_size) in enumerate(files[::-1]):
        for e, (empty_index, empty_size) in enumerate(empty):
            if empty_index >= file_index:
                break
            if empty_size >= file_size:
                empty[e] = (empty_index + file_size, empty_size - file_size)
                files[-f - 1] = (file_id, empty_index, file_size)
                break

    return files


def part2_slow(text_input: str) -> int:
    files = rearrange_files_part_2_slow(text_input)
    return calculate_checksum(files)


test_input = """
2333133121414131402
""".strip()


def test_part1():
    assert part1(test_input) == 1928


def test_part2():
    assert part2(test_input) == 2858


def test_part2_slow():
    assert part2_slow(test_input) == 2858


def test_relocate_to_the_right():
    # fast algo used to relocate first files to later empty spaces
    text = "65148196576"
    f1 = part2(text)
    f2 = part2_slow(text)
    assert f1 == f2
    # on this input the slow algo did that instead
    text = "784730132"
    f1 = part2(text)
    f2 = part2_slow(text)
    assert f1 == f2


def test_nudge_left():
    # used to have problems with "nudging" a file to the left
    # where it takes over some of its former space

    # the nudge should not happen
    text = "11313"
    f1 = part2(text)
    f2 = part2_slow(text)
    assert f1 == f2


# My algorithms do the exact same thing, don't they?
# ... Don't they?


def generate_random_input(num_files=6):
    res = str(randint(1, 9))
    for _ in range(num_files - 1):
        res += str(randint(0, 9)) + str(randint(1, 9))
    return res


def test_fuzzy():
    for _ in range(1000):
        text = generate_random_input(5)
        files1 = rearrange_files_part_2(text)
        files2 = rearrange_files_part_2_slow(text)
        if calculate_checksum(files1) != calculate_checksum(files2):
            print(text)
            for f1, f2 in zip(files1, files2):
                print(f1 == f2, f1, f2)
            assert False
    assert True
