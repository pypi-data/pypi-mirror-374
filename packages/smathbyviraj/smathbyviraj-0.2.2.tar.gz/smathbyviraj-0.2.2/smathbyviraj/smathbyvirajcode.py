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
    return fbnci(n - 1) + fbnci(n - 2)

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