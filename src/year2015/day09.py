# Problem statement: https://adventofcode.com/2015/day/9
# A TSP-like problem but it's a tiny one so I just went with a full search
import re
import itertools

day_title = "All in a Single Night"

line_regex = re.compile(r"(.+?) to (.+?) = (\d+)")


def parse_input(text):
    distances = {}
    cities = set()
    for line in text.split("\n"):
        city1, city2, distance = re.findall(line_regex, line)[0]
        distance = int(distance)
        distances[(city1, city2)] = distance
        distances[(city2, city1)] = distance
        cities.update((city1, city2))
    return distances, list(cities)


def best_route_length(cities, distances, want_min=True):
    i = 0
    sign = 1 if want_min else -1
    best_route_len = sum(distances.values())
    # best_route = None
    for route in itertools.permutations(cities):
        if route[0] > route[-1]:
            # this breaks symmetry because every route we can also do in reverse
            continue
        i += 1
        route_len = sum(
            sign * distances[(city1, city2)]
            for city1, city2 in zip(route[:-1], route[1:])
        )
        if route_len < best_route_len:
            # print(route, route_len, i)
            # best_route = route
            best_route_len = route_len
    return sign * best_route_len


def part1(text_input):
    distances, cities = parse_input(text_input)
    answer = best_route_length(cities, distances, want_min=True)
    return answer


def part2(text_input):
    distances, cities = parse_input(text_input)
    answer = best_route_length(cities, distances, want_min=False)
    return answer
