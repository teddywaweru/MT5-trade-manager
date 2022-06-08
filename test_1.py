def get_primes(n):
    multipliers = []
    multiplier = 2
    while n!=1:
        if n % multiplier != 0:
            multiplier += 1
            continue
        n //= multiplier
        multipliers.append(multiplier)

    return multipliers

print(get_primes(630))