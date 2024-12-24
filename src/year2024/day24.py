# Problem statement: https://adventofcode.com/2024/day/24

day_title = "Crossed Wires"


def part1(text_input: str) -> int:
    initial, gates = text_input.split("\n\n")
    gates = gates.split("\n")
    values = {}
    for line in initial.split("\n"):
        key, value = line.split(": ")
        values[key] = int(value)
    while gates:
        unused_gates = []
        for gate in gates:
            a_name, op, b_name, _, res = gate.split()
            a = values.get(a_name, None)
            b = values.get(b_name, None)
            if a is None or b is None:
                unused_gates.append(gate)
                continue
            if op == "AND":
                values[res] = a & b
            elif op == "OR":
                values[res] = a | b
            elif op == "XOR":
                values[res] = a ^ b
            else:
                raise ValueError(f"Unknown operator {op}")
        gates = unused_gates
    zs = sorted((key for key in values.keys() if key.startswith("z")), reverse=True)
    number = "".join(str(values[z]) for z in zs)
    return int(number, 2)


class SwapException(Exception):
    def __init__(self, message, a, b):
        super().__init__(message)
        self.wires = (a, b)


def find_swaps(gates: str):
    XOR, AND, OR = "XOR AND OR".split()
    gates = gates.split("\n")
    calculations = {}
    for gate in gates:
        a, op, b, _, res = gate.split()
        a, b = sorted((a, b))
        calculations[(a, op, b)] = res

    def find_gate(a, op, b):
        a, b = sorted((a, b))
        key = (a, op, b)
        if key in calculations:
            return calculations[key]
        # else something's not wired right
        # for example, we want "a xor b"
        # but we have "a xor c"
        # this means b and c should be swapped
        calc = [
            calc
            for calc in calculations.keys()
            if op in calc and (a in calc or b in calc)
        ][0]
        swap = set(calc).symmetric_difference(key)
        raise SwapException("Found you!", *swap)

    try:
        # Basically construct a correct binary addition contraption from logic gates
        # And see where it differs from what we're given
        # I learned the structure from studying the calculations graph
        # rendered with Graphviz
        xor00 = find_gate("x00", XOR, "y00")
        if xor00 != "z00":
            return xor00, "z00"
        and00 = find_gate("x00", AND, "y00")
        xor01 = find_gate("x01", XOR, "y01")
        zxor_i = find_gate(and00, XOR, xor01)
        and01 = find_gate("x01", AND, "y01")
        if zxor_i != "z01":
            return zxor_i, "z01"
        carry_and = find_gate(and00, AND, xor01)
        carry_or = find_gate(and01, OR, carry_and)
        for i in range(2, 45):
            and_i = find_gate(f"x{i:02d}", AND, f"y{i:02d}")
            xor_i = find_gate(f"x{i:02d}", XOR, f"y{i:02d}")
            zxor_i = find_gate(xor_i, XOR, carry_or)
            if zxor_i != f"z{i:02d}":
                return zxor_i, f"z{i:02d}"
            carry_and = find_gate(carry_or, AND, xor_i)
            carry_or = find_gate(carry_and, OR, and_i)
    except SwapException as e:
        return e.wires


def part2(text_input: str) -> int:
    _, gates = text_input.split("\n\n")
    swaps = {}
    for _ in range(4):
        # Find one swap at a time, fix it in the input text and go again
        a, b = find_swaps(gates)
        gates = gates.replace(f"-> {a}", "-> ???")
        gates = gates.replace(f"-> {b}", f"-> {a}")
        gates = gates.replace("-> ???", f"-> {b}")
        swaps[a] = b
    return ",".join(sorted([*swaps.keys(), *swaps.values()]))


test_input = """
x00: 1
x01: 0
x02: 1
x03: 1
x04: 0
y00: 1
y01: 1
y02: 1
y03: 1
y04: 1

ntg XOR fgs -> mjb
y02 OR x01 -> tnw
kwq OR kpj -> z05
x00 OR x03 -> fst
tgd XOR rvg -> z01
vdt OR tnw -> bfw
bfw AND frj -> z10
ffh OR nrd -> bqk
y00 AND y03 -> djm
y03 OR y00 -> psh
bqk OR frj -> z08
tnw OR fst -> frj
gnj AND tgd -> z11
bfw XOR mjb -> z00
x03 OR x00 -> vdt
gnj AND wpb -> z02
x04 AND y00 -> kjc
djm OR pbm -> qhw
nrd AND vdt -> hwm
kjc AND fst -> rvg
y04 OR y02 -> fgs
y01 AND x02 -> pbm
ntg OR kjc -> kwq
psh XOR fgs -> tgd
qhw XOR tgd -> z09
pbm OR djm -> kpj
x03 XOR y03 -> ffh
x00 XOR y04 -> ntg
bfw OR bqk -> z06
nrd XOR fgs -> wpb
frj XOR qhw -> z04
bqk OR frj -> z07
y03 OR x01 -> nrd
hwm AND bqk -> z03
tgd XOR rvg -> z12
tnw OR pbm -> gnj
""".strip()


def test_part1():
    assert part1(test_input) == 2024
