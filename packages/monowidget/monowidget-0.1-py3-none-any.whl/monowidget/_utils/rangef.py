# -*- coding: utf-8 -*-
from monowidget._utils.core import *
import math
from typing import Iterator, Union

Number = Union[int, float]

class rangef:
    """
    浮点数版 range
    支持切片、索引、len、迭代，行为尽量与内置 range 保持一致。
    """

    def __init__(self, start: Number, stop: Number = None, step: Number = 1.0) -> None:
        if stop is None:           # 类似 range(n) 的用法
            start, stop = 0.0, start
        self.start = float(start)
        self.stop = float(stop)
        self.step = float(step)

        if self.step == 0:
            raise ValueError("rangef() step must not be zero")

        # 计算元素个数
        self._len = max(0, int(math.ceil((self.stop - self.start) / self.step)))

    def __iter__(self) -> Iterator[float]:
        n = 0
        while n < self._len:
            yield self.start + n * self.step
            n += 1

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, idx: int) -> float:
        if not -self._len <= idx < self._len:
            raise IndexError("rangef object index out of range")
        if idx < 0:
            idx += self._len
        return self.start + idx * self.step

    def __reversed__(self) -> Iterator[float]:
        n = self._len - 1
        while n >= 0:
            yield self.start + n * self.step
            n -= 1

    def __repr__(self) -> str:
        if self.start == 0 and self.step == 1.0:
            return f"rangef({self.stop})"
        if self.step == 1.0:
            return f"rangef({self.start}, {self.stop})"
        return f"rangef({self.start}, {self.stop}, {self.step})"


if __name__ == '__main__':
    # 基本功能测试
    pass
