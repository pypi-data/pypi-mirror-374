class ArithmeticProgression:
    def __init__(self, first: float, difference: float):
        self.first = first
        self.difference = difference

    def __getitem__(self, n: int):
        if n <= 0:
            raise IndexError('n must be positive')
        if n == 1:
            return self.first
        return self.first + (self.difference * (n - 1))


class GeometricProgression:
    def __init__(self, first: float, denominator: float):
        if first == 0:
            raise ValueError("First cannot be zero")
        if denominator == 0:
            raise ValueError("Denominator cannot be zero")
        self.first = first
        self.denominator = denominator

    def __getitem__(self, n: int):
        if n <= 0:
            raise IndexError('n must be positive')
        if n == 1:
            return self.first
        return self.first * (self.denominator ** (n - 1))

