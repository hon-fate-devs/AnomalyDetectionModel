import numpy as np
from typing import *


class System:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.b_invert = np.linalg.inv(b)
        self.n = len(a)

    def next_u(self, x, next_x) -> np.ndarray:
        # вычисляет вектор управлений для того, чтобы получить следующее состояние next_x из состояния x
        return self.b_invert @ (next_x - self.a @ x)

    def make_path(self, points: list[np.ndarray], num_steps: Union[list[int], int], noise: float) -> tuple[np.ndarray, np.ndarray]:
        # производит эволюцию системы через состояния points, добавляя к ним гауссов шум с sigma=noise
        # возвращает последовательность состояний системы и последовательность управлений 
        # (последнее состояние не выводится, но управление для перехода в него вычисляется)

        if type(num_steps) == int:
            num_steps = [num_steps] * (len(points) - 1)

        assert len(points) == len(num_steps) + 1

        tres, tus = [], []

        points = [point + np.random.normal(scale=noise, size=self.n) for point in points]

        for i in range(len(num_steps)):
            new_res, new_us = self.__line(points[i], points[i + 1], num_steps[i])
            tres += new_res
            tus += new_us

        return tres, tus

    def __line(self, x, next_x, num_steps=1) -> tuple[np.ndarray, np.ndarray]:
        # выполняет эволюцию системы от x до next_x (разбивая на num_steps шагов)

        step = (next_x - x) / num_steps
        res = [x + step * i for i in range(num_steps)]
        us = []

        for i in range(num_steps - 1):
            us.append(self.next_u(res[i], res[i + 1]))

        us.append(self.next_u(res[-1], next_x))

        return res, us
    
