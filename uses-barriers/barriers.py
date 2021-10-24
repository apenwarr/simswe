#!/usr/bin/env python3
import csv
import random
import sys

MARKET_SIZE = 10000
GROWTH_RATE = 0.2
ADOPTION_DELAY = 0.2

PICK_FEATURES = 3
N_FEATURES = 10

PICK_NEEDS = 10
N_NEEDS = 25
EXTRA_NEEDS = N_NEEDS - PICK_NEEDS

SIM_STEPS = 500

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


def randbits(n, total):
    o = 0
    for _ in range(n):
        o |= 1 << random.randint(0, total-1)
    return o


def simulate(w, name, strategy):
    # for repeatability
    random.seed(1)

    market = []
    for _ in range(MARKET_SIZE):
        need = randbits(PICK_NEEDS, N_NEEDS)
        want = randbits(PICK_FEATURES, N_FEATURES)
        market.append(Person(want, need))
    
    inactive = set(market)
    active = set()
    cumu = 0
    for t, (features, unblocked) in enumerate(stratgen(strategy)):
        nf = bin(features).count('1')
        nu = bin(unblocked).count('1')
        interested = [p for p in inactive if p.interested(features)]
        satisfiable = [p for p in interested if not p.blocked(unblocked)]
        
        # awareness grows faster if there are more active users.
        # But awareness can only grow among the set of interested users.
        # This is basically a "logistic function".
        newly_aware = len(active) * GROWTH_RATE
        if newly_aware < 10:
            newly_aware = 10  # marketing :)
        newly_aware_prob = newly_aware / (len(active) + len(interested) + 1)
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
            if p.aware and random.random() < ADOPTION_DELAY:
                new_active.add(p)

        val = len(active) + len(new_active)
        cumu += val
        w.writerow([
            name, t, nf, nu,
            len(active) + len(interested),
            len(active) + len(satisfiable),
            val,
            cumu,
        ])
        sys.stdout.flush()

        active.update(new_active)
        inactive -= new_active
        
        if t == SIM_STEPS:
            break


def base_needs():
    o = 0
    for i in range(EXTRA_NEEDS, N_NEEDS):
        o |= 1 << i
    return o


def stratgen(impl):
    features = 0
    unblocked = base_needs()
    for features_added, unblocked_added in impl:
        assert not (features_added & ~((1<<N_FEATURES)-1))
        assert not (unblocked_added & ~((1<<N_NEEDS)-1))
    
        features |= features_added
        unblocked |= unblocked_added
        for _ in range(20):
            yield features, unblocked

    while 1:
        yield features, unblocked


def nonblocked():
    all_blocks = (1<<N_NEEDS) - 1
    for i in range(N_FEATURES):
        yield((1<<i, all_blocks))


def one_feature():
    for i in range(EXTRA_NEEDS):
        yield(1, 1<<i)


def alternating():
    needs_per_feat = EXTRA_NEEDS / N_FEATURES
    f = 0
    n = 0
    acc = 0
    while f < N_FEATURES and n < EXTRA_NEEDS:
        yield(1<<f, 0)
        f += 1
        acc += needs_per_feat

        while acc >= 1:
            yield(0, 1<<n)
            n += 1
            acc -= 1


def perfectionism():
    for i in range(EXTRA_NEEDS):
        yield(0, 1<<i)
    for i in range(N_FEATURES):
        yield(1<<i, 0)


def blockers_first():
    yield(1, 0)
    for i in range(EXTRA_NEEDS):
        yield(0, 1<<i)
    for i in range(1, N_FEATURES):
        yield(1<<i, 0)


def features_first():
    bn = base_needs()
    yield(0, bn)
    for i in range(N_FEATURES):
        yield(1<<i, 0)
    for i in range(EXTRA_NEEDS):
        yield(0, 1<<i)


def main():
    w = csv.writer(sys.stdout)
    w.writerow([
        'strategy', 't',
        'features', 'unblocked',
        'interested', 'satisfiable',
        'users', 'cumu',
    ])
    
    #simulate(w, 'base (non-blocked)', nonblocked())
    #simulate(w, 'base (one feature)', one_feature())
    simulate(w, 'alternating', alternating())
    simulate(w, 'blockers first', blockers_first())
    simulate(w, 'features first', features_first())
    simulate(w, 'perfectionism', perfectionism())



if __name__ == '__main__':
    main()
