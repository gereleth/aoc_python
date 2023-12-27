# Problem statement: https://adventofcode.com/2023/day/25

from collections import Counter
from random import randint

epsilon = 1e-8

day_title = "Snowverload"

example_input = """
jqt: rhn xhk nvd
rsh: frs pzl lsr
xhk: hfx
cmg: qnr nvd lhk bvb
rhn: xhk bvb hfx
bvb: xhk hfx
pzl: lsr hfx nvd
qnr: nvd
ntq: jqt hfx bvb xhk
nvd: lhk
lsr: lhk
rzs: qnr cmg lsr rsh
frs: qnr lhk lsr
""".strip()


def get_merged_node_id(node_merged_to, node):
    to_set = []
    while node in node_merged_to:
        other = node_merged_to[node]
        to_set.append(node)
        node = other
    for other in to_set[:-1]:
        node_merged_to[other] = node
    return node


def test_get_merged_node_id():
    merged = {1: 2, 2: 3, 3: 4, 5: 6}
    node = 1
    merged_id = get_merged_node_id(merged, node)
    assert merged_id == 4
    assert len(merged) == 4
    assert merged[1] == 4
    assert merged[2] == 4
    assert merged[3] == 4
    assert merged[5] == 6


def karger_min_cut(nodes, edges):
    # condense a graph by repeating this until only two nodes are left:
    # pop a random edge from edge list
    # merge its two ends into a single node

    # the remaining edges are those we should cut
    # two remaining nodes represent two parts of the graph after cutting
    # this process will probably lead to a min cut if run several times ))
    N = len(nodes)
    edges = list(edges)
    node_merged_to = {}
    while N > 2:
        index = randint(0, len(edges) - 1)
        a, b = edges.pop(index)
        a = get_merged_node_id(node_merged_to, a)
        b = get_merged_node_id(node_merged_to, b)
        if a == b:
            continue  # these guys have already been merged
        node_merged_to[b] = a
        N -= 1
    # condense merges data: {1:2,2:3}->{1:3,2:3}
    for key in node_merged_to:
        get_merged_node_id(node_merged_to, key)
    # should cut remaining edges
    cut = [
        (a, b) for a, b in edges if node_merged_to.get(a, a) != node_merged_to.get(b, b)
    ]
    return cut, node_merged_to


def part1(text_input: str):
    nodes = set()
    edges = []
    for line in text_input.split("\n"):
        left, rights = line.split(": ")
        rights = rights.split()
        nodes.add(left)
        nodes.update(rights)
        for right in rights:
            edges.append((left, right))
    best_cut_size = len(edges)
    while best_cut_size > 3:
        cut, merged = karger_min_cut(nodes, edges)
        best_cut_size = min(best_cut_size, len(cut))
    counts = Counter(merged.values())
    (_, count_a), (_, count_b) = counts.items()
    return (count_a + 1) * (count_b + 1)


def part2(text_input: str):
    return "=)"


def test_part1():
    assert part1(example_input) == 54
