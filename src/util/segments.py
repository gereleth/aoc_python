from typing import List


class Segment1D:
    """Represents an inclusive range of integers from a to b"""

    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def intersects(self, other: "Segment1D") -> bool:
        return max(self.a, other.a) <= min(self.b, other.b)

    def contains(self, other: "Segment1D") -> bool:
        return other.a >= self.a and other.b <= self.b

    def __str__(self) -> str:
        return f"[{self.a}, {self.b}]"

    def union(self, other: "Segment1D") -> "Segment1D":
        if not self.intersects(other):
            raise ValueError(f"Segments {self} and {other} do not intersect")
        return Segment1D(min(self.a, other.a), max(self.b, other.b))

    def intersection(self, other: "Segment1D") -> "Segment1D":
        if not self.intersects(other):
            raise ValueError(f"Segments {self} and {other} do not intersect")
        return Segment1D(max(self.a, other.a), min(self.b, other.b))

    def difference(self, other: "Segment1D") -> List["Segment1D"]:
        if not self.intersects(other):
            return [self]
        result = []
        if self.a < other.a:
            result.append(Segment1D(self.a, other.a - 1))
        if self.b > other.b:
            result.append(Segment1D(other.b + 1, self.b))
        return result

    def __len__(self):
        return self.b - self.a + 1

    def __lt__(self, other: "Segment1D"):
        if self.a == other.a:
            return self.b < other.b
        return self.a < other.a

    def __gt__(self, other: "Segment1D"):
        if self.a == other.a:
            return self.b > other.b
        return self.a > other.a

    def __eq__(self, other: "Segment1D"):
        return self.a == other.a and self.b == other.b

    def __contains__(self, x: int):
        return self.a <= x <= self.b

    def __repr__(self):
        return f"Segment1D({self.a}, {self.b})"

    def __hash__(self):
        return hash((self.a, self.b))


class Segment1DCollection:
    """A collection of segments. Keeps segments sorted and defragmented."""

    def __init__(self, segments: List[Segment1D] = []):
        self.segments: List[Segment1D] = []
        for segment in segments:
            self += segment

    def __add__(self, segment: Segment1D):
        insert_index = 0
        for i, s in enumerate(self.segments):
            if s.intersects(segment):
                combined = s.union(segment)
                self.segments[i] = combined
                insert_index = None
                while i + 1 < len(self.segments) and self.segments[i + 1].intersects(
                    combined
                ):
                    self.segments[i] = combined.union(self.segments[i + 1])
                    self.segments.pop(i + 1)
                break
            elif s < segment:
                insert_index = i
            elif s > segment:
                break
        if insert_index is not None:
            self.segments.insert(insert_index + 1, segment)
        return self

    def __subtract__(self, segment: Segment1D):
        for i, s in enumerate(self.segments):
            if s.intersects(segment):
                diff = s.difference(segment)
                self.segments[i] = diff[0]
                if len(diff) > 1:
                    self.segments.insert(i + 1, diff[1])
                    break
            elif s > segment:
                break
        return self

    def __str__(self):
        return "(" + ", ".join(map(str, self.segments)) + ")"

    def __contains__(self, i: int):
        return any(i in s for s in self.segments)

    def __len__(self):
        return sum(len(s) for s in self.segments)
