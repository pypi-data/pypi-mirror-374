import random as rn

import pyray as pr


class CountdownTimer:
    def __init__(self, base: float, factor: float) -> None:
        self._base: float = base
        self._factor: float = factor
        self._value: float = 0.0
        self.reset()

    @property
    def value(self) -> float:
        return self._value

    def update(self) -> None:
        self._value -= pr.get_frame_time()

    def is_complete(self) -> bool:
        is_complete_: bool = self._value <= 0.0
        return is_complete_

    def reset(self) -> None:
        self._value = (rn.random() * self._factor) + self._base
