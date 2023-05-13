import numpy as np
from typing import *
from .System import *
from .utils import *


def gen_time_series(dim: int, num_cycles: int, noise: float, 
                    carno_params: CarnoParams = DEFAULT_CARNO,
                    ellipse_params: EllipseParams = DEFAULT_ELLIPSE,
                    sys: System = None) \
            -> np.ndarray:
    # возвращает сгенерировнный временной ряд из наблюдений 
    # массив [N, k], N -- число измерений, k -- число датчиков (k=dim*2)
    # sys -- созданная ранее модель системы 

    if sys is None:
        na = np.random.uniform(-5, 12, size=(dim, dim))
        nb = np.random.uniform(-5, 5, size=na.shape) + 5 * np.ones(na.shape)

        sys = System(na, nb)

    observations = create_series(sys, noise, num_cycles, carno_params=carno_params, 
                                 ellipse_params=ellipse_params)
    return observations


if __name__ == '__main__':
    ts = gen_time_series(160, 50, 0.3)

    np.savetxt("test.csv", ts, delimiter=",")

