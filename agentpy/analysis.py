"""
Agentpy Analysis Module
Content: Sensitivity and interactive analysis, animation, visualization
"""

import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from SALib.analyze import sobol

from .tools import make_list, param_tuples_to_salib




def animate(model, fig, axs, plot, steps=None, seed=None,
            skip=0, fargs=(), **kwargs):
    """ Returns an animation of the model simulation,
    using :func:`matplotlib.animation.FuncAnimation`.

    Arguments:
        model (Model): The model instance.
        fig (matplotlib.figure.Figure): Figure for the animation.
        axs (matplotlib.axes.Axes or list): Axis or list of axis of the figure.
        plot (function): Function that takes `(model, ax, *fargs)`
            and creates the desired plots on each axis at each time-step.
        steps(int, optional):
            Maximum number of steps for the simulation to run.
            If none is given, the parameter 'Model.p.steps' will be used.
            If there is no such parameter, 'steps' will be set to 1000.
        seed (int, optional):
            Seed to set for :obj:`Model.random` at the beginning of the simulation.
            If none is given, the parameter 'Model.p.seed' will be used.
            If there is no such parameter, as random seed will be set.
        skip (int, optional): Number of rounds to skip before the
            animation starts (default 0).
        fargs (tuple, optional): Forwarded fo the `plot` function.
        **kwargs: Forwarded to :func:`matplotlib.animation.FuncAnimation`.

    Examples:
        An animation can be generated as follows::

            def my_plot(model, ax):
                pass  # Call pyplot functions here
            
            fig, ax = plt.subplots() 
            my_model = MyModel(parameters)
            animation = ap.animate(my_model, fig, ax, my_plot)

        One way to display the resulting animation object in Jupyter::

            from IPython.display import HTML
            HTML(animation.to_jshtml())
    """

    model.run_setup(steps, seed)
    model.create_output()
    pre_steps = 0

    for _ in range(skip):
        model.run_step()

    def frames():
        nonlocal model, pre_steps
        if model.running is True:
            while model.running:
                if pre_steps < 2:  # Frames iterates twice before starting plot
                    pre_steps += 1
                else:
                    model.run_step()
                    model.create_output()
                yield model.t
        else:  # Yield current if model stops before the animation starts
            yield model.t

    def update(t, m, axs, *fargs):  # noqa
        nonlocal pre_steps
        for ax in make_list(axs):
            # Clear axes before each plot
            ax.clear()
        plot(m, axs, *fargs)  # Perform plot

    ani = matplotlib.animation.FuncAnimation(
        fig, update,
        frames=frames,
        fargs=(model, axs, *fargs),
        save_count=model._steps,
        **kwargs)  # noqa

    plt.close()  # Don't display static plot
    return ani


def _apply_colors(grid, color_dict, convert):
    if isinstance(grid[0], (list, np.ndarray)):
        return [_apply_colors(subgrid, color_dict, convert)
                for subgrid in grid]
    else:
        if color_dict is not None:
            grid = [i if i is np.nan else color_dict[i] for i in grid]
        if convert is True:
            grid = [(0., 0., 0., 0.) if i is np.nan else
                    matplotlib.colors.to_rgba(i) for i in grid]
        return grid


def gridplot(grid, color_dict=None, convert=False, ax=None, **kwargs):
    """ Visualizes values on a two-dimensional grid with
    :func:`matplotlib.pyplot.imshow`.

    Arguments:
        grid(list of list): Two-dimensional grid with values.
            numpy.nan values will be plotted as empty patches.
        color_dict(dict, optional): Dictionary that translates
            each value in `grid` to a color specification.
        convert(bool, optional): Convert values to rgba vectors,
             using :func:`matplotlib.colors.to_rgba` (default False).
        ax(matplotlib.pyplot.axis, optional): Axis to be used for plot.
        **kwargs: Forwarded to :func:`matplotlib.pyplot.imshow`.
     """

    # TODO Make feature for legend
    if color_dict is not None or convert:
        grid = _apply_colors(grid, color_dict, convert)
    if ax:
        ax.imshow(grid, **kwargs)
    else:
        plt.imshow(grid, **kwargs)
