# Problem statement: https://adventofcode.com/2023/day/23

from util.inputs import movechars_dr_dc
import heapq
import networkx as nx

day_title = "A Long Walk"

example_input = """
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
""".strip()

opposite = {">": "<", "<": ">", "^": "v", "v": "^"}


class HikingArea:
    def __init__(self, text_input, slippery=True):
        self.map = text_input.split("\n")
        self.slippery = slippery
        self.R = len(self.map)
        self.C = len(self.map[0])
        self.start = (0, 1)
        self.finish = (self.R - 1, self.C - 2)
        self.graph = nx.DiGraph()
        self.explore_graph()

        # for every node calculate how much distance it could contribute to the path
        # take two longest edges from this node and average their lengths
        self.best_path_contribution = {}
        for node in self.graph.nodes:
            costs = sorted(cost for _, _, cost in self.graph.edges(node, data="cost"))[
                -2:
            ]
            self.best_path_contribution[node] = (
                sum(costs) / len(costs) if len(costs) > 0 else 0
            )

    def explore_graph(self):
        self.graph.add_node(0, position=self.start)
        self.graph.add_node(1, position=self.finish)
        next_node_id = 2
        queue = [(self.start, 0, "", 0)]
        done = set()
        node_positions = {self.finish: 1}
        while len(queue) > 0:
            (r0, c0), from_node, path, edge_direction = queue.pop()
            done.add((r0, c0))
            can_move = set()
            for direction, (dr, dc) in movechars_dr_dc.items():
                new_edge_direction = edge_direction
                r, c = r0 + dr, c0 + dc
                # is it an existing node
                if (r, c) in node_positions and node_positions[(r, c)] != from_node:
                    if edge_direction >= 0:
                        self.graph.add_edge(
                            from_node,
                            node_positions[(r, c)],
                            cost=len(path) + 1,
                            path=path + direction,
                        )
                    if edge_direction <= 0:
                        self.graph.add_edge(
                            node_positions[(r, c)],
                            from_node,
                            cost=len(path) + 1,
                            path="".join(reversed(path + direction)),
                        )
                # is it out of bounds
                if r < 0 or r >= self.R or c < 0 or c >= self.C:
                    continue
                # is it not a path or already visited
                char = self.map[r][c]
                if (r, c) in done or char == "#":
                    continue
                # if slippery and an arrow - set edge direction, one way street
                if self.slippery and char != ".":
                    if direction == char:
                        new_edge_direction = 1
                    else:
                        new_edge_direction = -1
                # can move there!
                can_move.add((r, c, direction, new_edge_direction))
            # multiple move options mean this should be a node
            if len(can_move) > 1:
                node_positions[(r0, c0)] = next_node_id
                self.graph.add_node(next_node_id, position=(r0, c0))
                if edge_direction >= 0:
                    self.graph.add_edge(
                        from_node, next_node_id, cost=len(path), path=path
                    )
                if edge_direction <= 0:
                    self.graph.add_edge(
                        next_node_id,
                        from_node,
                        cost=len(path),
                        path="".join(reversed(path)),
                    )
                from_node = next_node_id
                next_node_id += 1
                path = ""
                edge_direction = 0
            for pos in can_move:
                r, c, direction, edge_direction = pos
                queue.append(((r, c), from_node, path + direction, edge_direction))

    def next_states(self, state):
        last_node, visited, cost, upper_bound = state
        for last_node, neighbour, extra_cost in self.graph.out_edges(
            last_node, data="cost"
        ):
            if neighbour in visited:
                continue
            new_upper_bound = (
                upper_bound
                + extra_cost
                - (
                    self.best_path_contribution[last_node]
                    + self.best_path_contribution[neighbour]
                )
                / 2
            )
            yield (
                neighbour,
                visited.union((neighbour,)),
                cost + extra_cost,
                new_upper_bound,
            )

    def find_longest_path(self):
        start_node = 0
        finish_node = 1
        cost = 0
        ub = (
            sum(self.best_path_contribution.values())
            - self.best_path_contribution[finish_node]
        )
        # take the obvious steps to the finish node
        while len(self.graph.in_edges(finish_node)) == 1:
            (n1, n2, ecost), *_ = self.graph.in_edges(finish_node, data="cost")
            neighbour = n1 if n2 == finish_node else n2
            cost += ecost
            ub += ecost - self.best_path_contribution[neighbour]
            finish_node = neighbour
        queue = [(0, (start_node, set((start_node,)), cost, ub))]
        heapq.heapify(queue)
        bestlength = -1
        i = 1

        while len(queue) > 0:
            i += 1
            priority, prev_state = heapq.heappop(queue)
            if prev_state[-1] < bestlength:
                continue
            # if i % 1000 == 0:
            #     last_node, visited, cost, upper_bound = prev_state
            #     print(
            #         i,
            #         bestlength,
            #         priority,
            #         len(queue),
            #         cost,
            #         upper_bound,
            #     )
            for state in self.next_states(prev_state):
                last_node, visited, cost, upper_bound = state
                if last_node == finish_node:
                    if cost > bestlength:
                        bestlength = cost
                        # print(i, bestlength, priority, len(queue))
                        continue
                if upper_bound < bestlength:
                    continue
                priority = -upper_bound  # continue the path with the best potential
                # priority = -cost  # continue the longest path
                heapq.heappush(queue, (priority, state))
        # print(f"Total iterations {i}")
        return bestlength


def part1(text_input: str):
    area = HikingArea(text_input, slippery=True)
    result = area.find_longest_path()
    return result


def part2(text_input):
    area = HikingArea(text_input, slippery=False)
    result = area.find_longest_path()
    return result


def test_part1():
    assert part1(example_input) == 94


def test_part2():
    assert part2(example_input) == 154
