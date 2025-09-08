def sqrt(n):
    if n < 0:
        raise ValueError('Square root not defined for negative numbers')
    return n ** 0.5

def fbnci(n):
    if n < 0:
        raise ValueError('Fibonacci not defined for negative numbers')
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    return n + fbnci(n-1)

def fctrl(n):
    if n < 0:
        raise ValueError('Factorial not defined for negative numbers')
    elif n == 0 or n == 1:
        return 1
    return n * fctrl(n - 1)

def divby(x, y):
    return f'''{x} by {y}:
    Quotient = {x//y}
    Remainder = {x%y}
    Exact Quotient = {x/y}

{y} by {x}:
    Quotient = {y//x}
    Remainder = {y%x}
    Exact Quotient = {y/x}'''

def baseconv(x, y, z, precision=12):
    """
    Converts number x from base y to base z.
    Supports fractional parts and bases 2–36.
    Uses capital letters for digits > 9.
    precision: number of digits after decimal in output
    """
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if not (2 <= y <= 36 and 2 <= z <= 36):
        raise ValueError("Bases must be between 2 and 36")

    # Step 1: Convert x (str) from base y to base 10 float
    x = str(x).strip().upper()
    is_negative = x.startswith('-')
    if is_negative:
        x = x[1:]

    if '.' in x:
        int_part, frac_part = x.split('.')
    else:
        int_part, frac_part = x, ''

    # Convert integer part
    base10_int = 0
    for char in int_part:
        if char not in digits[:y]:
            raise ValueError(f"Invalid character '{char}' for base {y}")
        base10_int = base10_int * y + digits.index(char)

    # Convert fractional part
    base10_frac = 0
    for i, char in enumerate(frac_part, 1):
        if char not in digits[:y]:
            raise ValueError(f"Invalid character '{char}' for base {y}")
        base10_frac += digits.index(char) / (y ** i)

    base10 = base10_int + base10_frac
    if is_negative:
        base10 = -base10

    # Step 2: Convert base10 float to base z string
    abs_val = abs(base10)
    int_part = int(abs_val)
    frac_part = abs_val - int_part

    # Convert integer part
    result_int = []
    if int_part == 0:
        result_int.append('0')
    else:
        while int_part > 0:
            result_int.append(digits[int_part % z])
            int_part //= z

    # Convert fractional part
    result_frac = []
    count = 0
    while frac_part > 0 and count < precision:
        frac_part *= z
        digit = int(frac_part)
        result_frac.append(digits[digit])
        frac_part -= digit
        count += 1

    result = ''.join(reversed(result_int))
    if result_frac:
        result += '.' + ''.join(result_frac)
    if base10 < 0:
        result = '-' + result
    return result

def euler_totient(n):
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result