import numpy as np


class WindFrequencyMatrix:
    """Information about the wind rose and speed distribution

    :param wind_speeds: wind speed bin centres as an array
    :param number_of_sectors: number of wind directions sectors
    :param frequency_matrix: 2D matrix of size len(wind_speeds) x number_of_sectors containing the expected time in each speed and direction bin
    :param first_sector_midpoint: the centre of the first sector in degrees, clockwise from North
    """
    def __init__(self, wind_speeds, number_of_sectors, frequency_matrix, first_sector_midpoint=0.):
        if frequency_matrix.shape != (len(wind_speeds), number_of_sectors):
            raise RuntimeError('Invalid hours per year matrix shape')
        self._wind_speeds = wind_speeds
        self._number_of_sectors = number_of_sectors
        self._sector_width_degrees = 360. / number_of_sectors
        self._sector_midpoints = first_sector_midpoint + np.arange(number_of_sectors, dtype=int) * self.sector_width_degrees
        self._frequency_matrix = frequency_matrix

    @property
    def shape(self):
        return self.frequency_matrix.shape

    @property
    def wind_speeds(self):
        return self._wind_speeds

    @property
    def sector_width_degrees(self):
        return self._sector_width_degrees

    @property
    def sector_midpoints(self):
        return self._sector_midpoints

    @property
    def frequency_matrix(self):
        return self._frequency_matrix