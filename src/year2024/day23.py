# Problem statement: https://adventofcode.com/2024/day/23

import networkx as nx
from collections import defaultdict

day_title = "LAN Party"


def part1(text_input: str) -> int:
    edges = [line.split("-") for line in text_input.split("\n")]
    neighbors = defaultdict(set)
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    triplets = set()
    for a, neighbors_a in neighbors.items():
        if not a.startswith("t"):
            continue
        for b in neighbors_a:
            common_cs = neighbors[b].intersection(neighbors_a)
            for c in common_cs:
                triplets.add(tuple(sorted((a, b, c))))
    return len(triplets)


# Tried doing part 1 through nx too but this is 40x slower than my first solution
def part1_networkx(text_input: str) -> int:
    lines = text_input.split("\n")
    graph = nx.Graph(line.split("-") for line in lines)
    total = 0
    for clique in nx.enumerate_all_cliques(graph):
        if len(clique) < 3:
            continue
        elif len(clique) == 3:
            total += any(name.startswith("t") for name in clique)
        else:
            break
    return total


# I read about Bron-Kerbosch algorithm... And didn't feel like implementing it.
def part2(text_input: str) -> int:
    lines = text_input.split("\n")
    graph = nx.Graph(line.split("-") for line in lines)
    nodes = max(nx.find_cliques(graph), key=len)
    return ",".join(sorted(nodes))


test_input = """
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn
""".strip()


def test_part1():
    assert part1(test_input) == 7


def test_part2():
    assert part2(test_input) == "co,de,ka,ta"
