# haltonseq/core.py

def halton_sequence(b: int):
    """Generator function for Halton sequence with given base b."""
    n, d = 0, 1
    while True:
        x = d - n
        if x == 1:
            n = 1
            d *= b
        else:
            y = d // b
            while x <= y:
                y //= b
            n = (b + 1) * y - x
        yield n / d


def generate_halton_numbers(count: int, base: int = 2):
    """Generate a list of 'count' Halton numbers for the given base."""
    gen = halton_sequence(base)
    return [next(gen) for _ in range(count)]
