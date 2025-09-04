# Random Rhythms in Python!
Partition a musical duration into rhythmic phrases.

Usage:

1. Determine the pool of durations to use the ryhthmic phrase:

```
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
```

2. Import the class:

```python
from random_rhythms.random_rhythms import Rhythm
```

3. Instantiate a random-rhythm object:

```python
params = { # these are the defaults:
    time_signature: '4/4',
    measure_size: 4,
    durations: [ 1/4, 1/2, 1/3, 1, 3/2, 2 ],
    weights: [ 1, 1, 1, 1, 1, 1 ],
    groups: { 1/3: 3 },
    smallest: 1/128
}
rr = Rhythm(**params)
```

4. Get a motif:

```python
motif = rr.motif()
print(motif)
```