# Problem statement: https://adventofcode.com/2023/day/20

from collections import defaultdict, deque
from dataclasses import dataclass
from math import lcm

day_title = "Pulse Propagation"

example_input_1 = r"""
broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a
""".strip()


example_input_2 = r"""
broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output
""".strip()


@dataclass
class Signal:
    source: str
    destination: str
    value: bool

    def __repr__(self):
        return f"Signal({self.source}, {self.destination}, {self.value})"

    def __str__(self):
        return f"{self.source}-{int(self.value)}->{self.destination}"


class Button:
    def __init__(self):
        self.destinations = ["broadcaster"]

    def send(self):
        return [Signal("button", "broadcaster", False)]

    @property
    def name(self):
        return "button"


class Broadcaster:
    def __init__(self, destinations):
        self.destinations = destinations

    def receive(self, signal: Signal):
        return [Signal("broadcaster", d, signal.value) for d in self.destinations]

    @property
    def name(self):
        return "broadcaster"


class FlipFlop:
    def __init__(self, name, destinations):
        self.name = name[1:]
        self.destinations = destinations
        self.on = False

    def receive(self, signal: Signal):
        if signal.value:
            return []
        self.on = not self.on
        return [Signal(self.name, d, self.on) for d in self.destinations]


class Conjunction:
    def __init__(self, name, destinations):
        self.name = name[1:]
        self.destinations = destinations
        self.memory = {}

    def add_input(self, name):
        self.memory[name] = False

    def receive(self, signal: Signal):
        self.memory[signal.source] = signal.value
        send = False if all(m for m in self.memory.values()) else True
        return [Signal(self.name, d, send) for d in self.destinations]


def parse_input(text: str):
    lines = text.split("\n")
    res = [Button()]
    inputs = defaultdict(list)
    for line in lines:
        module_str, destinations = line.split(" -> ")
        destinations = destinations.split(", ")
        if module_str == "broadcaster":
            module = Broadcaster(destinations)
        elif module_str.startswith("%"):
            module = FlipFlop(module_str, destinations)
        elif module_str.startswith("&"):
            module = Conjunction(module_str, destinations)
        else:
            raise ValueError(f"Unknown module {module_str}")
        res.append(module)
        for destination in destinations:
            inputs[destination].append(module.name)
    for module in res:
        if isinstance(module, Conjunction):
            for source in inputs[module.name]:
                module.add_input(source)
    return {module.name: module for module in res}


def part1(text_input: str):
    modules = parse_input(text_input)
    total_high = 0
    total_low = 0
    for _ in range(1000):
        queue = deque([modules["button"].send()])
        while len(queue) > 0:
            signals = queue.popleft()
            high = sum(signal.value for signal in signals)
            low = len(signals) - high
            total_high += high
            total_low += low
            for signal in signals:
                # print("process signal", signal)
                if signal.destination not in modules:
                    continue
                new_signals = modules[signal.destination].receive(signal)
                if len(new_signals) > 0:
                    queue.append(new_signals)
                    # print("send new signals", [str(s) for s in new_signals])
    # print(total_low, total_high)
    total = total_high * total_low
    return total


# non generalizable, quirky lcm all like day 8 again
def part2(text_input: str):
    modules = parse_input(text_input)
    button_presses = 0
    ultimate_destination_name = "rx"
    sources = [
        name
        for name, module in modules.items()
        if ultimate_destination_name in module.destinations
    ]
    if len(sources) != 1:
        raise ValueError("No single source for ultimate destination. Sources:", sources)
    ultimate_source = modules[sources[0]]
    if not isinstance(ultimate_source, Conjunction):
        raise ValueError("Ultimate source is not a conjunction module")
    memory = {}
    while True:
        button_presses += 1
        if button_presses % 10000 == 0:
            print(button_presses)
        queue = deque([modules["button"].send()])
        while len(queue) > 0:
            signals = queue.popleft()
            for signal in signals:
                if signal.destination not in modules:
                    continue
                if signal.destination == "rx" and signal.value is False:
                    return button_presses
                new_signals = modules[signal.destination].receive(signal)
                if signal.destination == ultimate_source.name:
                    for key, value in ultimate_source.memory.items():
                        if value and key not in memory:
                            memory[key] = button_presses
                    if len(memory) == len(ultimate_source.memory):
                        return lcm(*memory.values())
                if len(new_signals) > 0:
                    queue.append(new_signals)


def test_part1():
    assert part1(example_input_1) == 32000000
    assert part1(example_input_2) == 11687500
