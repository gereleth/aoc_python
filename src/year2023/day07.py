# Problem statement: https://adventofcode.com/2023/day/7

from collections import Counter

day_title = "Camel Cards"

example_input = """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
""".strip()

FIVE_OF_A_KIND = 0
FOUR_OF_A_KIND = 1
FULL_HOUSE = 2
THREE_OF_A_KIND = 3
TWO_PAIR = 4
ONE_PAIR = 5
HIGH_CARD = 6

cards = "AKQJT98765432"
card_rank = {c: i for i, c in enumerate(cards)}


def hand_strength(hand):
    s = Counter(hand)
    if len(s) == 1:
        return FIVE_OF_A_KIND
    if len(s) == 2:
        c = max(s.values())
        if c == 4:
            return FOUR_OF_A_KIND
        else:
            return FULL_HOUSE
    if len(s) == 3:
        c = max(s.values())
        if c == 3:
            return THREE_OF_A_KIND
        else:
            return TWO_PAIR
    if len(s) == 4:
        return ONE_PAIR
    return HIGH_CARD


def test_hand_strength():
    assert hand_strength("AAAAA") == FIVE_OF_A_KIND
    assert hand_strength("22222") == FIVE_OF_A_KIND
    assert hand_strength("AAAAK") == FOUR_OF_A_KIND
    assert hand_strength("KKKQK") == FOUR_OF_A_KIND
    assert hand_strength("A2AAA") == FOUR_OF_A_KIND
    assert hand_strength("AAAKK") == FULL_HOUSE
    assert hand_strength("KAAKK") == FULL_HOUSE
    assert hand_strength("AAAK2") == THREE_OF_A_KIND
    assert hand_strength("2AAKA") == THREE_OF_A_KIND
    assert hand_strength("23QQQ") == THREE_OF_A_KIND
    assert hand_strength("AAKK2") == TWO_PAIR
    assert hand_strength("2Q2Q3") == TWO_PAIR
    assert hand_strength("AAKK2") == TWO_PAIR
    assert hand_strength("A789A") == ONE_PAIR
    assert hand_strength("AAT23") == ONE_PAIR
    assert hand_strength("456KK") == ONE_PAIR
    assert hand_strength("23456") == HIGH_CARD
    assert hand_strength("AKQJ5") == HIGH_CARD
    assert hand_strength("KT789") == HIGH_CARD


def part1(text_input):
    total = 0
    ls = []
    for line in text_input.split("\n"):
        hand, bid = line.split()
        strength = hand_strength(hand)
        bid = int(bid)
        ls.append((strength, *(card_rank[h] for h in hand), hand, bid))
    ls.sort()
    N = len(ls)
    for i, (*_, bid) in enumerate(ls):
        total += bid * (N - i)
    return total


def test_part_1():
    assert part1(example_input) == 6440


def improve_hand_joker(hand):
    if "J" not in hand:
        return hand
    card_counts = Counter(hand)
    card_counts.pop("J")
    if len(card_counts) == 0:
        return "AAAAA"
    card, _ = card_counts.most_common(1)[0]
    return "".join(c if c != "J" else card for c in hand)


def test_improve_hand_joker():
    assert improve_hand_joker("23456") == "23456"
    assert improve_hand_joker("JJJJJ") == "AAAAA"
    assert improve_hand_joker("KKK2J") == "KKK2K"
    assert improve_hand_joker("KJJJJ") == "KKKKK"
    assert improve_hand_joker("KK2JJ") == "KK2KK"
    hand = improve_hand_joker("2345J")
    assert hand_strength(hand) == ONE_PAIR
    hand = improve_hand_joker("234JJ")
    assert hand_strength(hand) == THREE_OF_A_KIND
    hand = improve_hand_joker("23JJJ")
    assert hand_strength(hand) == FOUR_OF_A_KIND
    hand = improve_hand_joker("2233J")
    assert hand_strength(hand) == FULL_HOUSE


def part2(text_input):
    total = 0
    card_rank_joker = {**card_rank}
    card_rank_joker["J"] = 99  # make it the weakest card
    ls = []
    for line in text_input.split("\n"):
        hand, bid = line.split()
        improved_hand = improve_hand_joker(hand)
        strength = hand_strength(improved_hand)
        bid = int(bid)
        ls.append((strength, *(card_rank_joker[h] for h in hand), hand, bid))
    ls.sort()
    N = len(ls)
    for i, (*_, bid) in enumerate(ls):
        total += bid * (N - i)
    return total


def test_part_2():
    assert part2(example_input) == 5905
