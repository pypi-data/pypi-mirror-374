import math


class MyMath:
    def __init__(self, value: int) -> None:
        self.value = value

    def factorial(self) -> int:
        return math.factorial(self.value)
