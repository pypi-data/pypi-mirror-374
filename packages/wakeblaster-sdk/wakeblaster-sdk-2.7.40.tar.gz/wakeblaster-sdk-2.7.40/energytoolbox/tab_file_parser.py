import numpy as np
from .wind_frequency_matrix import WindFrequencyMatrix


class TabFileParser:
    """
    Parses .tab (observed wind climate) files as documented by WAsP. Currently none of the 'variants' are supported,
    only the version without a flag
    
    :param filepath: Path to .tab file
    """
    def __init__(self, filepath):
        with open(filepath, 'r') as fp:
            self._lines = fp.readlines()

    def get_frequency_matrix(self, hours_in_a_year=8766, max_wind_speed=None, stop_when_zero=True):
        """
        :param hours_in_a_year: Total number of hours in an average calendar year. 8766 is Julian calendar average (leap year every 4 years). True astronomical average is 8765.81
        :param max_wind_speed: Maximum wind speed to read up to. If None, read until end of matrix
        :param stop_when_zero: If True, stop parsing when it reaches the first row that sums to zero
        :returns: WindFrequencyMatrix object
        """
        line3_parts = self._lines[2].split()
        if len(line3_parts) > 3:
            raise IOError('Cannot read TAB file type with flag {}'.format(line3_parts[3]))
        n_sectors = int(line3_parts[0])
        speed_factor = float(line3_parts[1])
        sector0_midpoint = float(line3_parts[2])
        sectorwise_frequencies = self._parse_sectorwise_frequencies(n_sectors)
        wind_speeds, frequency_rows = self._parse_rows(n_sectors, max_wind_speed, stop_when_zero)
        frequencies = self._convert_frequencies(sectorwise_frequencies, frequency_rows)
        return WindFrequencyMatrix(self._bin_centres(speed_factor*wind_speeds),
                                   n_sectors,
                                   hours_in_a_year*frequencies,
                                   sector0_midpoint)

    def _parse_sectorwise_frequencies(self, n):
        parts = self._lines[3].split()
        if len(parts) != n:
            raise IOError('Incorrect number of sectors. Expected {}, found {}'.format(n, len(parts)))
        return [float(p) for p in parts]

    def _parse_rows(self, n_sectors, max_wind_speed, stop_when_zero):
        wind_speeds = []
        frequency_rows = []
        for i in range(4, len(self._lines)):
            parts = self._lines[i].split()
            if len(parts) == 0:
                continue
            if len(parts) != (n_sectors + 1):
                raise IOError('Incorrect number of sectors. Expected {}, found {}'.format(n_sectors, len(parts) - 1))
            ws = float(parts[0])
            freqs = np.array(parts[1:], dtype=float)
            if (max_wind_speed is not None and ws > max_wind_speed) or (stop_when_zero and np.sum(freqs) <= 0.0):
                break
            wind_speeds.append(ws)
            frequency_rows.append(freqs)
        return np.array(wind_speeds), frequency_rows

    @staticmethod
    def _convert_frequencies(sectorwise_frequencies, frequency_rows):
        frequencies = np.zeros((len(frequency_rows), len(sectorwise_frequencies)), dtype=float)
        for i in range(len(frequency_rows)):
            frequencies[i, :] = frequency_rows[i]

        for j in range(frequencies.shape[1]):
            colsum = frequencies[:, j].sum()
            if colsum < 999.9 or colsum > 1000.1:
                raise IOError('Column {} does not add up to 1000'.format(j))
            frequencies[:, j] = (sectorwise_frequencies[j] / 100.) * frequencies[:, j] / 1000.

        return frequencies

    @staticmethod
    def _bin_centres(wind_speeds):
        speed_bin_centres = np.empty(wind_speeds.shape, dtype=float)
        speed_bin_centres[0] = wind_speeds[0]/2
        speed_bin_centres[1:] = (wind_speeds[1:] + wind_speeds[:-1]) / 2
        return speed_bin_centres
