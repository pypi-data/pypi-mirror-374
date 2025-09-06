import bisect
from dataclasses import dataclass, field
from typing import Self


@dataclass
class IntervalSet:
    segments: list[tuple[int, int]] = field(default_factory=list)

    def add(self, start: int, end: int) -> None:
        if start == end:
            return

        assert start < end

        segment = (start, end)
        bisect.insort_left(self.segments, segment, key=lambda x: x[0])

        # note(taras): you can check if the new segment overlaps with the previous ones to improve the best case to O(log(n))
        # however, the average case would still be O(n) because you need to copy the segments liniearly
        self._merge_intervals()

    def _merge_intervals(self) -> None:
        merged: list[tuple[int, int]] = [self.segments[0]]

        for cur in self.segments[1:]:
            if merged[-1][1] < cur[0]:
                merged.append(cur)
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], cur[1]))

        self.segments = merged

    def range_intersection(self: Self, start: int, end: int) -> "IntervalSet":
        res = IntervalSet()

        # position where all segments are before or at the range
        left = bisect.bisect_left(self.segments, start, key=lambda x: x[1])

        # position where all segments are after the range
        right = bisect.bisect_right(self.segments, end, key=lambda x: x[0])

        assert left <= right

        for i in range(left, right):
            l, r = self.segments[i]
            res.add(max(start, l), min(end, r))

        return res
