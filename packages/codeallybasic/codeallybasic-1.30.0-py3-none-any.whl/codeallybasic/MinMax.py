
from typing import List

from dataclasses import dataclass


@dataclass
class MinMax:
    minValue: int = 0
    maxValue: int = 0

    @classmethod
    def deSerialize(cls, value: str) -> 'MinMax':

        minMax: MinMax = MinMax()

        values: List[str] = value.split(sep=',')

        assert len(values) == 2, 'Incorrectly formatted min/max values'

        try:
            minMax.minValue = int(values[0])
            minMax.maxValue = int(values[1])
        except ValueError as ve:
            print(f'MinMax - {ve}.')
            minMax.minValue = 0
            minMax.maxValue = 0

        return minMax

    def __str__(self):
        return f'{self.minValue},{self.maxValue}'

    def __repr__(self):
        return self.__str__()
