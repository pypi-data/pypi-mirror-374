import pandas as pd
import numpy as np
from collections import deque

from .wind_frequency_matrix import WindFrequencyMatrix
from .util import SignalNames as signals


class FlowCaseMaker:
    """Base class: Responsible for producing flow cases with weighting in order to calculate yield from the frequency matrix"""
    def make(self, frequency_matrix):
        return NotImplementedError()


class GaussianQuadratureFlowCaseMaker(FlowCaseMaker):
    """
    Creates flow cases in each direction sector in order to perform Gaussian quadrature integration.
    This is an alternative but more efficient method than using evenly spaced direction flow cases

    :param points_per_sector: Number of points in each direction sector of the frequency matrix. n points per sector is capable of perfect integration of an order 2n-1 power vs direction profile within the sector
    """
    def __init__(self, points_per_sector):
        self._points_per_sector = points_per_sector

    def make(self, frequency_matrix):
        df = pd.DataFrame(columns=[signals.wind_speed, signals.wind_direction, 'weighting'])
        x, weights = np.polynomial.legendre.leggauss(self._points_per_sector)
        for ws, row in zip(frequency_matrix.wind_speeds, frequency_matrix.frequency_matrix):
            for midpoint, freq in zip(frequency_matrix.sector_midpoints, row):
                df_append = pd.DataFrame({signals.wind_speed: np.full((self._points_per_sector,), ws),
                                          signals.wind_direction: 0.5 * frequency_matrix.sector_width_degrees * x + midpoint,
                                          'weighting': weights * freq})
                df = df.append(df_append, ignore_index=True)
        return df


class LinspacePerSectorFlowCaseMaker(FlowCaseMaker):
    """
    Creates flow cases at fixed direction intervals within each WindFrequencyMatrixSector
    Within each sector, weighting is constant for all points. Points are always within the sector not at the sector boundaries

    :param n_directions_per_sector: Number of directions in each sector
    """
    def __init__(self, n_directions_per_sector):
        self._n_per_sector = n_directions_per_sector

    def make(self, frequency_matrix):
        if not isinstance(frequency_matrix, WindFrequencyMatrix):
            raise TypeError('frequency_matrix is not WindFrequencyMatrix')

        spacing = frequency_matrix.sector_width_degrees / self._n_per_sector
        lim = (self._n_per_sector / 2 - 0.5) * spacing
        offsets = np.linspace(-lim, lim, self._n_per_sector, True)
        data = {signals.wind_speed: [], signals.wind_direction: [], 'weighting': []}

        midpoints = frequency_matrix.sector_midpoints
        for ws, row in zip(frequency_matrix.wind_speeds, frequency_matrix.frequency_matrix):
            dirs = deque()
            weights = deque()
            for j in range(len(row)):
                dirs += deque(midpoints[j] + offsets)
                weights += self._n_per_sector * [row[j] / self._n_per_sector]

            self._standardise_directions(dirs, weights)
            data[signals.wind_speed] += len(dirs) * [ws]
            data[signals.wind_direction] += dirs
            data['weighting'] += weights

        return pd.DataFrame(data=data)

    @staticmethod
    def _standardise_directions(dirs, weights):
        # put in range [0, 360.0) and sort
        for jj in range(len(dirs)):
            if dirs[jj] < 0.0:
                dirs[jj] += 360.0
            else:
                dirs.rotate(-jj)
                weights.rotate(-jj)
                break


class SectorWeightFunction:
    def __init__(self, sector_width, bin_width):
        self._a = 0.5 * (sector_width - bin_width)
        self._b = 0.5 * (sector_width + bin_width)

    def weight(self, x):
        if abs(x) <= self._a:
            return 1.0
        elif abs(x) >= self._b:
            return 0.0
        else:
            return (self._b - abs(x)) / (self._b - self._a)


def _angle_diff(a, b):
    angle = a - b
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle


class LinspaceFlowCaseMaker(FlowCaseMaker):
    def __init__(self, n_directions, first_bin_midpoint=0.0):
        self._directions = np.linspace(0.0, 360.0, num=n_directions, endpoint=False) + first_bin_midpoint
        self._bin_width = 360.0 / n_directions

    def make(self, frequency_matrix):
        if not isinstance(frequency_matrix, WindFrequencyMatrix):
            raise TypeError('frequency_matrix is not WindFrequencyMatrix')

        data = {signals.wind_speed: [], signals.wind_direction: [], 'weighting': []}
        for ws, row in zip(frequency_matrix.wind_speeds, frequency_matrix.frequency_matrix):
            data[signals.wind_speed] += [ws] * len(self._directions)
            data[signals.wind_direction] += list(self._directions)
            weight_function = np.vectorize(SectorWeightFunction(frequency_matrix.sector_width_degrees, self._bin_width).weight)
            for d in self._directions:
                angle_diffs = np.vectorize(_angle_diff)(d, frequency_matrix.sector_midpoints)
                weights = weight_function(angle_diffs) * row \
                          * min(self._bin_width / frequency_matrix.sector_width_degrees, 1.0)
                data['weighting'].append(np.sum(weights))

        return pd.DataFrame(data=data)
