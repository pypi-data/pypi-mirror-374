"""
Name: random_rhythms

Abstract: Partition a musical duration into rhythmic phrases.

Description: This library converts a musical duration into a
partitioned rhythmic phrase.
"""

from music21 import *
import random

class Rhythm:
    def __init__(
            self,
            measure_size=4,
            durations=[],
            weights=[],
            groups={},
            smallest=1/128
        ):
        self.measure_size = measure_size
        if not durations:
            self.durations = [1/4, 1/2, 1/3, 1, 3/2, 2]
        else:
            self.durations = durations
        if not weights:
            self.weights = [ 1 for x in self.durations ]
        else:
            self.weights = weights
        if not groups:
            self.groups = { 1/3: 3 }
        else:
            self.groups = groups
        self.smallest = smallest

    def motif(self):
        smallest = sorted(self.durations)[0]

        sum = 0
        motif = []
        group_num = 0
        group_item = 0

        while sum < self.measure_size:
            dura = random.choices(self.durations, weights=self.weights, k=1)[0]
            if group_num:
                group_num -= 1
                dura = group_item
            else:
                if dura in self.groups:
                    group_num = self.groups[dura] - 1
                    group_item = dura
                else:
                    group_num = 0
                    group_item = 0
            diff = self.measure_size - sum
            if diff < smallest:
                if diff >= self.smallest:
                    motif.append(diff)
                break
            if dura > diff:
                continue
            sum += dura
            if sum <= self.measure_size:
                motif.append(dura)

        return motif