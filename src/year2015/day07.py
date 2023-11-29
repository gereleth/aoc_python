# Problem statement: https://adventofcode.com/2015/day/7

day_title = "Some Assembly Required"

operations = {
    "NOT": lambda x: (~x) & 0xFFFF,
    "AND": lambda x, y: x & y,
    "OR": lambda x, y: x | y,
    "LSHIFT": lambda x, n: (x << n) & 0xFFFF,
    "RSHIFT": lambda x, n: x >> n,
    "IDENT": lambda x: x,
}


def compute_signals(text_input, overrides={}):
    signals = {}
    computations = {}
    for line in text_input.split("\n"):
        left, right = line.split(" -> ")
        key = right
        parsed = left.split()
        if len(parsed) == 1:
            try:
                signals[key] = int(parsed[0])
            except ValueError:
                computations[key] = operations["IDENT"], parsed[0]
        elif parsed[0] == "NOT":
            computations[key] = operations["NOT"], parsed[1]
        elif parsed[1] == "AND":
            computations[key] = operations["AND"], parsed[0], parsed[2]
        elif parsed[1] == "OR":
            computations[key] = operations["OR"], parsed[0], parsed[2]
        elif parsed[1] == "LSHIFT":
            computations[key] = operations["LSHIFT"], parsed[0], parsed[2]
        elif parsed[1] == "RSHIFT":
            computations[key] = operations["RSHIFT"], parsed[0], parsed[2]
        else:
            raise ValueError("unknown command in line " + line)
    for key, value in overrides.items():
        signals[key] = value
    while len(computations) > 0:
        key = next(iter(computations.keys()))
        trace = [key]
        while len(trace) > 0:
            key = trace[-1]
            if key in signals:
                trace.pop()
                continue
            operation, *args = computations[key]
            arg_values = []
            for arg in args:
                if arg.isnumeric():
                    arg_values.append(int(arg))
                elif arg in signals:
                    arg_values.append(signals[arg])
                else:
                    trace.append(arg)
            if len(args) == len(arg_values):
                signals[key] = operation(*arg_values)
                computations.pop(key)
                trace.pop()
    return signals


def part1(text_input):
    return compute_signals(text_input)["a"]


def test_compute_signals():
    text = """
x -> z
x AND yy -> d
x OR yy -> e
x LSHIFT 2 -> f
yy RSHIFT 2 -> g
NOT x -> hh
NOT yy -> ii
123 -> x
456 -> yy
1 OR d -> dd
    """.strip()
    expected = {
        "d": 72,
        "e": 507,
        "f": 492,
        "g": 114,
        "hh": 65412,
        "ii": 65079,
        "x": 123,
        "yy": 456,
        "z": 123,
        "dd": 73,
    }
    actual = compute_signals(text)
    for key, value in expected.items():
        assert value == actual[key]


def part2(text_input):
    a_value = compute_signals(text_input)["a"]
    answer = compute_signals(text_input, overrides={"b": a_value})["a"]
    return answer
