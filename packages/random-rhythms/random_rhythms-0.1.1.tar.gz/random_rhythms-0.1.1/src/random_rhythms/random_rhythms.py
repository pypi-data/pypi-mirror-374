"""
Name: random_rhythms

Abstract: Partition a musical duration into rhythmic phrases.

Description: This library converts a musical duration into a
partitioned rhythmic phrase.

128th to 128: .03125 .0625 .125 .25 .5 1 2 4 8 16 32 64 128
# durations = [ 2**x for x in range(-5, 8) ]
16th to 16th: .25 .5 1 2 4 8 16
# durations = [ 2**x for x in range(-2, 5) ]
Triplets: .167 .333 .667 1.333 2.667
# durations = [ 2**x/3 for x in range(-1, 4) ]
Dotted: .375 .75 1.5 3 6
# durations = [ 2**x+2**x/2 for x in range(-2, 3) ]
Double dotted: .4375 .875 1.75 3.5 7
# durations = [ 2**x+2**x/2+2**x/4 for x in range(-2, 3) ]

"""

from music21 import *
import random

class Rhythm:
    def __init__(self):
        self.time_signature = '4/4'
        self.measure_size = 4
        self.durations = [ 1/4, 1/2, 1/3, 1, 3/2, 2 ]
        self.weights = [ 1, 1, 1, 1, 1, 1 ]
        self.groups = { 1/3: 3 }
        self.smallest = 1/128

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