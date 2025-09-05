from math import floor, pi

from matplotlib import pyplot
import h5py
import numpy as np


DEF_CMAP = 'gnuplot_r'

IMSHOW_KWARGS = {
    'origin': 'lower',
    'aspect': 'equal',
    'interpolation': 'nearest'
}

COLORBAR_KWARGS = {
    'orientation': 'horizontal',
    'fraction': 0.06
}

LETTERS = ('X', 'Y', 'Z')
LABELS = (
    'Downstream distance [m]',
    'Lateral distance [m]',
    'Height above ground [m]'
)


def _get_wind_direction_deg(file, timestep_index):
    dataset = file['/wind_directions']
    if len(dataset.shape) == 4:  # old versions of flow plane store this dataset as 4D
        return dataset[0, 0, 0, timestep_index] * 180 / pi
    elif len(dataset.shape) == 1:
        return dataset[timestep_index] * 180 / pi
    raise ValueError("Incorrect number of dimensions for 'wind_directions' dataset")


def _get_grid(file, timestep_index):
    def _get(name):
        dataset = file[name]
        if len(dataset.shape) == 4:  # old versions of flow plane store this dataset as 4D
            return dataset[0, :, 0, timestep_index]
        elif len(dataset.shape) == 2:
            return dataset[:, timestep_index]
    grid_start = _get('/grid_starts')
    grid_step = _get('/grid_steps')
    if grid_step[0] == 0.0:
        grid_step[0] = grid_step[1]  # assume x step is equal to y step
    return grid_start, grid_step


def _get_loc(grid_start, grid_step, loc, dim, zero_origin=False):
    if zero_origin:
        index = loc / grid_step[dim]
    else:
        index = (loc - grid_start[dim]) / grid_step[dim]
    lower = floor(index)
    frac = index - lower
    return lower, index, frac


def _get_vlims(data):
    return np.min(data), np.max(data)


def _read_file(file, timestep_index, field):
    wind_direction = _get_wind_direction_deg(file, timestep_index)
    grid_start, grid_step = _get_grid(file, timestep_index)
    data = file[field]
    return data, wind_direction, grid_start, grid_step


def _get_data_2d(data, grid_start, grid_step, axis_indices, timestep_index, slice_value, zero_origin=False):
    z_lower, z_index, f = _get_loc(grid_start, grid_step, slice_value, axis_indices[2], zero_origin)
    data = np.transpose(data[:, :, :, timestep_index], axes=axis_indices)
    if z_lower < 0 or z_lower + 1 >= data.shape[2]:
        raise IndexError(LABELS[axis_indices[2]] + " ({}) out of range".format(slice_value))
    return (1 - f) * data[:, :, z_lower] + f * data[:, :, z_lower + 1]


def _plot_graph(fig, axes, axes_indices, data, cmap, extent, vlims, field, slice_value, wind_direction):
    im = axes.imshow(data, cmap=cmap, extent=extent, vmin=vlims[0], vmax=vlims[1], **IMSHOW_KWARGS)
    axes.set_xlabel(LABELS[axes_indices[0]])
    axes.set_ylabel(LABELS[axes_indices[1]])
    axes.set_title('{}-{} {} slice at {:.1f}m, wind direction = {:.1f}deg'.format(LETTERS[axes_indices[0]],
                                                                                  LETTERS[axes_indices[1]],
                                                                                  field, slice_value, wind_direction))
    fig.colorbar(im, ax=axes, **COLORBAR_KWARGS)


def plot_flow_plane_xy(filepath, height,
                       field='velocities', fig=None, axes=None, timestep_index=0, cmap=DEF_CMAP, vlims=None):
    """
    Plots a the flow plane in the x-y plane i.e. birds-eye view

    :param filepath: File path to the flow plane *.h5 file
    :type filepath: str or path
    :param height: z-value in metres of the slice at which to plot e.g. hub height
    :type height: float
    :param field: name of the dataset to plot - defaults to 'velocities'
    :param fig: matplotlib figure object. If 'None', a figure will be created using pyplot.subplots()
    :type fig: maatplotlib.Figure
    :param axes: matplotlib axes object. If figure is 'None', axes will be created using pyplot.subplots()
    :type axes: matplotlib.Axes
    :param timestep_index: Index of timestep (flow-case) in flow plane file. Defaults to zero
    :type timestep_index: int
    :param cmap: matplotlib colormap to use for the colour scale
    :type cmap: str or matplotlib.Colormap
    """
    if fig is None:
        fig, axes = pyplot.subplots()

    with h5py.File(filepath, 'r') as file:
        dataset, wind_direction, grid_start, grid_step = _read_file(file, timestep_index, field)
        vlims = _get_vlims(dataset) if vlims is None else vlims
        if dataset.shape[2] == 1:
            data = dataset[:, :, 0].squeeze()
            height = grid_start[2]  # single height case
        else:
            data = _get_data_2d(dataset, grid_start, grid_step, (0, 1, 2), timestep_index, height)

    extent = (0.0, data.shape[0] * grid_step[0],
              0.0, data.shape[1] * grid_step[1])
    _plot_graph(fig, axes, (0, 1), np.transpose(data), cmap, extent, vlims, field, height, wind_direction)


def plot_flow_plane_xz(filepath, lateral_distance,
                       field='velocities', fig=None, axes=None, timestep_index=0, cmap=DEF_CMAP, vlims=None):
    """
    Plots a the flow plane in the x-z plane i.e. side-on view

    :param filepath: File path to the flow plane *.h5 file
    :type filepath: str or path
    :param lateral_distance: y-value in metres from edge of flow plane of the slice to plot. Based on right-handed system where 'x' is downstream and 'z' is vertically upwards
    :type lateral_distance: float
    :param field: name of the dataset to plot - defaults to 'velocities'
    :param fig: matplotlib figure object. If 'None', a figure will be created using pyplot.subplots()
    :type fig: maatplotlib.Figure
    :param axes: matplotlib axes object. If figure is 'None', axes will be created using pyplot.subplots()
    :type axes: matplotlib.Axes
    :param timestep_index: Index of timestep (flow-case) in flow plane file. Defaults to zero
    :type timestep_index: int
    :param cmap: matplotlib colormap to use for the colour scale
    :type cmap: str or matplotlib.Colormap
    """
    if fig is None:
        fig, axes = pyplot.subplots()

    with h5py.File(filepath, 'r') as file:
        dataset, wind_direction, grid_start, grid_step = _read_file(file, timestep_index, field)
        vlims = _get_vlims(dataset) if vlims is None else vlims
        data = _get_data_2d(dataset, grid_start, grid_step, (0, 2, 1), timestep_index, lateral_distance, True)

    extent = (0.0, data.shape[0] * grid_step[0],
              grid_start[2], grid_start[2] + data.shape[1] * grid_step[2])
    _plot_graph(fig, axes, (0, 2), np.transpose(data), cmap, extent, vlims, field, lateral_distance, wind_direction)


def plot_flow_plane_yz(filepath, downstream_distance,
                       field='velocities', fig=None, axes=None, timestep_index=0, cmap=DEF_CMAP, vlims=None):
    """
    Plots a the flow plane in the y-z plane i.e. front-on view

    :param filepath: File path to the flow plane *.h5 file
    :type filepath: str or path
    :param downstream_distance: x-value of the slice at which to plot downstream from the start of the flow plane
    :type downstream_distance: float
    :param field: name of the dataset to plot - defaults to 'velocities'
    :param fig: matplotlib figure object. If 'None', a figure will be created using pyplot.subplots()
    :type fig: maatplotlib.Figure
    :param axes: matplotlib axes object. If figure is 'None', axes will be created using pyplot.subplots()
    :type axes: matplotlib.Axes
    :param timestep_index: Index of timestep (flow-case) in flow plane file. Defaults to zero
    :type timestep_index: int
    :param cmap: matplotlib colormap to use for the colour scale
    :type cmap: str or matplotlib.Colormap
    """
    if fig is None:
        fig, axes = pyplot.subplots()

    with h5py.File(filepath, 'r') as file:
        dataset, wind_direction, grid_start, grid_step = _read_file(file, timestep_index, field)
        vlims = _get_vlims(dataset) if vlims is None else vlims
        data = _get_data_2d(dataset, grid_start, grid_step, (1, 2, 0), timestep_index, downstream_distance, True)

    extent = (0.0, data.shape[0] * grid_step[1],
              grid_start[2], grid_start[2] + data.shape[1] * grid_step[2])
    _plot_graph(fig, axes, (1, 2), np.fliplr(np.transpose(data)), cmap, extent, vlims, field, downstream_distance, wind_direction)