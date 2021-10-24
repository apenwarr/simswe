#!/usr/bin/env python3
import csv
import random
import sys

MARKET_SIZE = 10000
GROWTH_RATE = 0.20
N_FEATURES = 10
N_NEEDS = 20


class Person(object):
    __slots__ = ['wants', 'needs', 'aware']

    def __init__(self, wants, needs):
        self.wants = wants
        self.needs = needs
        self.aware = False
    
    def interested(self, features):
        return (self.wants & features) != 0
    
    def blocked(self, unblocked):
        return (self.needs & ~unblocked) != 0
    
    def satisfied(self, features, unblocked):
        return self.interested(features) and not self.blocked(unblocked)


def blockless():
    for i in range(N_NEEDS):
        # yield((1<<i, 0xffffffff))
        yield((1, 1<<i))


def strategy(impl):
    features = 0
    unblocked = 0
    for features_added, unblocked_added in impl:
        features |= features_added
        unblocked |= unblocked_added
        for _ in range(20):
            yield features, unblocked

    # continue for a while to show pattern
    for i in range(100):
        yield features, unblocked


def randbits(n, total):
    o = 0
    for _ in range(n):
        o |= 1 << random.randint(0, total-1)
    return o


def main():
    # for repeatability
    random.seed(1)
    
    w = csv.writer(sys.stdout)
    w.writerow([
        't', 'features', 'unblocked',
        'interested', 'satisfiable', 'users',
    ])

    market = []
    for _ in range(MARKET_SIZE):
        need = randbits(10, N_NEEDS)
        want = randbits(3, N_FEATURES)
        market.append(Person(want, need))
    
    inactive = set(market)
    active = set()
    for t, (features, unblocked) in enumerate(strategy(blockless())):
        nf = bin(features).count('1')
        nu = bin(unblocked).count('1')
        interested = [p for p in inactive if p.interested(features)]
        satisfiable = [p for p in interested if not p.blocked(unblocked)]
        
        # awareness grows faster if there are more active users.
        # But awareness can only grow among the set of interested users.
        # This is basically a "logistic function".
        newly_aware = len(active) * GROWTH_RATE
        if newly_aware < 10:
            newly_aware = 10  # founder sales :)
        newly_aware_prob = newly_aware / (len(active) + len(interested))
        # The GROWTH_RATE is spread among all interested users, including
        # ones that were already aware or active. This makes awareness
        # growth slow down as the population gets more saturated, as we
        # expect with logistic growth.
        for p in interested:
            if random.random() < newly_aware_prob:
                p.aware = True
        
        # Select a fixed fraction of satisfiable users who are already
        # aware of our product. This simulates the way customers don't
        # all adopt a product right away even once they know about it
        # and it's applicable to them.
        new_active = set()
        for p in satisfiable:
            if p.aware and random.random() < 0.2:
                new_active.add(p)

        w.writerow([
            t, nf, nu,
            len(active) + len(interested),
            len(active) + len(satisfiable),
            len(active) + len(new_active),
        ])

        active.update(new_active)
        inactive -= new_active
        if not inactive:
            break

if __name__ == '__main__':
    main()
