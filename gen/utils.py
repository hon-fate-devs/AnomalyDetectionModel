import numpy as np
import matplotlib.pyplot as plt
from typing import *
from dataclasses import dataclass
from System import System


def gen_points_ellipse(r1, r2, right_point: np.ndarray, num_points):
    phi = np.linspace(0, 2 * np.pi, num_points)
    xs = r1 * np.cos(phi)
    ys = r2 * np.sin(phi)
    points = np.stack((xs, ys), axis=1)
    
    delta = right_point - points[0]
    
    return points + delta

def gen_exp(start_point: np.ndarray, stop_point: np.ndarray, start_exp: float, stop_exp: float, num_points: int):
    if (start_point > stop_point).any():
        start_point, stop_point = stop_point, start_point
        reverse = True
        
    else:
        reverse = False
    
    basic_x = np.linspace(start_exp, stop_exp, num=num_points, endpoint=True)
    
    y = np.exp(basic_x)
    
    delta_y_raw = y[-1] - y[0]
    delta_y = stop_point[1] - start_point[1]
    y -= y.min()
    y *= delta_y / delta_y_raw
    
    x = np.linspace(start_point[0], stop_point[0], num=num_points, endpoint=True)
    
    res = np.stack((x, y), axis=1)
    return res if not reverse else res[::-1]

def gen_line(start_point: np.ndarray, stop_point: np.ndarray, num_points: int):
    return np.linspace(start_point, stop_point, num=num_points, endpoint=True)


@dataclass 
class CarnoParams:
    points: list
    num_points: int


@dataclass 
class EllipseParams:
    r1: float
    r2: float
    center: np.ndarray
    num_points: int


DEFAULT_CARNO = CarnoParams(
    [np.array([0, 0]), np.array([10, 10]), np.array([20, 10]), np.array([10, 0])],
    240
)

DEFAULT_ELLIPSE = EllipseParams(2, 4, np.array([0, 0]), 120)


def create_carno_m(params: CarnoParams = DEFAULT_CARNO) -> np.ndarray:
    if params.num_points % 6:
        print("Warning: num points mod 6 should be 0")

    num_points_exp = params.num_points // 3
    num_points_lin = num_points_exp // 2

    return create_carno(*params.points, npoint_exp=num_points_exp, npoint_lin=num_points_lin)


def create_ellipses_m(params: EllipseParams = DEFAULT_ELLIPSE) -> np.ndarray:
    return create_ell_2_cycles(params.r1, params.r2, params.center, params.num_points)


def create_ell_2_cycles(r1, r2, center, points_per_ellipse):
    points = gen_points_ellipse(r1, r2, center, points_per_ellipse)
    points2 = gen_points_ellipse(r2, r1, center, points_per_ellipse)
    return np.concatenate((points, points2))


def create_carno(s0, s1, s2, s3, npoint_exp=80, npoint_lin=40):
    points = gen_exp(s0, s1, 4, 7, npoint_exp)

    other = [
        gen_line(s1, s2, npoint_lin),
        gen_exp(s2, s3, 4, 7, npoint_exp),
        gen_line(s3, s0, npoint_lin)
    ]

    for o in other:
        points = np.concatenate((points, o))

    return points


def unite_axis(points1, points2):
    return np.concatenate((points1, points2), axis=1)


def _create_2d_ell_cycle(ellipse_params: EllipseParams):
    return create_ellipses_m(ellipse_params)  # точки 2х эллиптических циклов (каждый по два эллипса)


def _create_2d_carno_cycle(carno_params: CarnoParams):
    return create_carno_m(carno_params)  # точки цикла Карно


def _create_random_2d_component(carno_params: CarnoParams, ellipse_params: EllipseParams):
    if np.random.uniform() < 0.5:
        return _create_2d_carno_cycle(carno_params)
    else:
        return _create_2d_ell_cycle(ellipse_params)


def create_cycle(system: System, noise, num_carno: int = None,
                 carno_params: CarnoParams = DEFAULT_CARNO,
                 ellipse_params: EllipseParams = DEFAULT_ELLIPSE,
                 num_steps: int = 1) -> np.ndarray:

    assert len(system.a) % 2 == 0
    if num_carno is None:
        num_carno = len(system.a) // 4
        
    assert num_carno <= len(system.a) // 2

    state_dim = len(system.a)
    
    points = np.concatenate(
        [_create_2d_carno_cycle(carno_params) for _ in range(num_carno)] +
        [_create_2d_ell_cycle(ellipse_params) for _ in range(len(system.a) // 2 - num_carno)],
        axis=1
    )

    return np.concatenate(system.make_path(points, num_steps, noise), axis=1)  # векторы наблюдений


def create_series(
        system: System, noise: float, num_cycles: int, num_carno=None,
        carno_params: CarnoParams = DEFAULT_CARNO,
        ellipse_params: EllipseParams = DEFAULT_ELLIPSE,
        num_steps: int = 1
            ) -> np.ndarray:

    return np.concatenate([create_cycle(
        system, noise, num_carno, carno_params, ellipse_params, num_steps
            ) for _ in range(num_cycles)
         ]
    )
