"""
Base plotting module for Common Crawl statistics visualization.

This module provides the CrawlPlot base class which handles:
- Plot library selection (matplotlib, rpy2/ggplot2, or legacy ggplot)
- Common plot styling to match ggplot2 aesthetics
- Data input from stdin or files
- Output directory management

The plot library is controlled by the PLOTLIB environment variable:
- 'matplotlib' (recommended)
- 'rpy2.ggplot2' (requires R and rpy2)
- 'ggplot' (deprecated)

The output directory is controlled by PLOTDIR (defaults to 'plots/').
"""

import json
import logging
import os
import os.path
import sys
from typing import Literal

import fsspec
import numpy as np


# Supported plot library backends
PlotLibType = Literal["rpy2.ggplot2", "ggplot", "matplotlib"]


class CrawlPlot:
    """
    Base class for Common Crawl statistics plots.

    Provides common functionality for all plot types including:
    - Plot library initialization and configuration
    - Data reading from stdin or gzipped files
    - Line plot generation with consistent styling
    - Output directory management

    Subclasses should implement:
    - add(key, val): Process a single data record
    - plot(): Generate the specific visualization

    Attributes:
        PLOTLIB: The plotting library to use ('matplotlib', 'rpy2.ggplot2', or 'ggplot')
        PLOTDIR: Directory for saving plot output files
        DEFAULT_FIGSIZE: Default figure size in inches (7 = 2100px at 300 DPI)
        DEFAULT_DPI: Default resolution for saved figures
    """

    GGPLOT2_THEME = None
    GGPLOT2_THEME_KWARGS = None

    # figure with square aspect ratio : 7 inches * 300 DPI = 2100 pixels
    DEFAULT_FIGSIZE = 7
    DEFAULT_DPI = 300

    title_fontsize = 15
    title_pad = 20
    title_fontweight = "normal"
    title_loc = "left"
    xlabel_fontsize = 12
    ylabel_fontsize = 12
    ticks_fontsize = 10
    ticks_color = "#E6E6E6"
    ticks_length = 8
    ticks_width = 1.0
    bar_width = 0.8
    legend_fontsize = 10
    legend_title_fontsize = 11
    line_width = 0.75
    marker_size = 4
    grid_major_linewidth = 1.0
    grid_minor_linewidth = 0.5
    grid_major_color = "#E6E6E6"
    grid_minor_color = "#E6E6E6"
    tight_layout_pad = 0.5
    savefig_facecolor = "white"
    savefig_bbox_inches = None

    # -------------------------------------------------------------------------
    # Matplotlib helper methods for reducing code duplication
    # -------------------------------------------------------------------------

    def create_figure(self, ratio=1.0):
        """Create a matplotlib figure with consistent sizing.

        Args:
            ratio: Height ratio relative to width (default: 1.0 for square)

        Returns:
            Tuple of (fig, ax)
        """
        import matplotlib.pyplot as plt
        return plt.subplots(figsize=(self.DEFAULT_FIGSIZE, self.DEFAULT_FIGSIZE * ratio))

    def set_title(self, ax, title):
        """Apply consistent title styling to an axes.

        Args:
            ax: matplotlib Axes object
            title: Title text
        """
        ax.set_title(
            title,
            fontsize=self.title_fontsize,
            fontweight=self.title_fontweight,
            pad=self.title_pad,
            loc=self.title_loc,
        )

    def apply_ggplot2_style(self, ax, show_grid=True, grid_axis='both'):
        """Apply ggplot2-like minimal styling to an axes.

        Removes spines, adds grid lines, and sets axes below plot elements.

        Args:
            ax: matplotlib Axes object
            show_grid: Whether to show grid lines (default: True)
            grid_axis: Which axis to show grid on ('both', 'x', or 'y')
        """
        # Remove all spines
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)

        # Add grid
        if show_grid:
            ax.grid(True, which='major', linewidth=self.grid_major_linewidth,
                    color=self.grid_major_color, zorder=0, axis=grid_axis)

        ax.set_axisbelow(True)

    def set_tick_labels_black(self, ax):
        """Set all tick labels to black color.

        Args:
            ax: matplotlib Axes object
        """
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')

    def apply_nice_ticks(self, ax, axis='y', use_scientific=True):
        """Apply nice tick spacing using the nice_tick_step calculation.

        Sets minor and major ticks at 'nice' intervals (multiples of 1, 2, or 5).
        Optionally applies scientific notation for large values.

        Args:
            ax: matplotlib Axes object
            axis: Which axis to apply to ('x' or 'y')
            use_scientific: Whether to use scientific notation for large values
        """
        from matplotlib.ticker import MultipleLocator, FormatStrFormatter

        if axis == 'y':
            vmin, vmax = ax.get_ylim()
            axis_obj = ax.yaxis
        else:
            vmin, vmax = ax.get_xlim()
            axis_obj = ax.xaxis

        minor = self.nice_tick_step(vmin, vmax, n=8)
        major = 2 * minor

        axis_obj.set_minor_locator(MultipleLocator(minor))
        axis_obj.set_major_locator(MultipleLocator(major))

        if use_scientific and vmax > 1e4:
            axis_obj.set_major_formatter(FormatStrFormatter('%.0e'))

    def save_figure(self, fig, img_path):
        """Save figure with consistent settings and close it.

        Args:
            fig: matplotlib Figure object
            img_path: Output file path

        Returns:
            The figure object (for chaining)
        """
        import matplotlib.pyplot as plt
        plt.tight_layout(pad=self.tight_layout_pad)
        plt.savefig(img_path, dpi=self.DEFAULT_DPI,
                    bbox_inches=self.savefig_bbox_inches,
                    facecolor=self.savefig_facecolor)
        plt.close()
        return fig

    def hide_tick_marks(self, ax, tick_color='#FFFFFF'):
        """Hide tick marks by setting them to a background color.

        The tick labels remain visible but the tick marks themselves are hidden.

        Args:
            ax: matplotlib Axes object
            tick_color: Color to set ticks to (default: white)
        """
        ax.tick_params(axis='both', which='both', colors=tick_color,
                       length=self.ticks_length, width=self.ticks_width)

    def __init__(self):
        """Initialize the plot with library selection and output directory setup."""
        # Settings defined via environment variables
        self.PLOTLIB: PlotLibType = os.environ.get('PLOTLIB', 'rpy2.ggplot2')
        self.PLOTDIR = os.environ.get('PLOTDIR', 'plots')

        if self.PLOTLIB == 'ggplot':
            # nothing to do here
            pass
        elif self.PLOTLIB == 'rpy2.ggplot2':
            from rpy2.robjects.lib import ggplot2
            from rpy2.robjects import pandas2ri
            pandas2ri.activate()
            # use minimal theme with white background set in plot constructor
            # https://ggplot2.tidyverse.org/reference/ggtheme.html
            self.GGPLOT2_THEME = ggplot2.theme_minimal(base_size=12, base_family="Helvetica")

            self.GGPLOT2_THEME_KWARGS = {
                'panel.background': ggplot2.element_rect(fill='white', color='white'),
                'plot.background': ggplot2.element_rect(fill='white', color='white')
            }

        elif self.PLOTLIB == "matplotlib":
            import matplotlib.pyplot as plt

            # ggplot2-inspired color palette
            ggplot_colors = [
                "#F8766D", "#00BE67", "#00A9FF", "#CD9600", "#7CAE00",
                "#00BFC4", "#C77CFF", "#FF61CC",
            ]

            # Set up ggplot2-like minimal theme with larger fonts
            plt.style.use('default')
            plt.rcParams.update({
                'font.family': 'sans-serif',
                'font.sans-serif': ['Liberation Sans', 'Arial', 'DejaVu Sans'],
                'font.size': 20,  # Much larger base font size
                'axes.linewidth': 1.5,
                'axes.spines.left': True,
                'axes.spines.bottom': True,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'axes.axisbelow': True,
                'axes.grid': True,
                'axes.grid.axis': 'both',
                'grid.linewidth': 1.0,
                'grid.color': '#E6E6E6',  # Gray grid lines
                'axes.facecolor': 'white',  # White background
                'figure.facecolor': 'white',
                'xtick.bottom': True,
                'xtick.top': False,
                'ytick.left': True,
                'ytick.right': False,
                'xtick.direction': 'out',
                'ytick.direction': 'out',
                'axes.prop_cycle':  plt.cycler(color=ggplot_colors),
            })

        else:
            raise ValueError("Invalid PLOTLIB defined")

        # Make sure output directories exists
        os.makedirs(os.path.join(self.PLOTDIR, "crawler"), exist_ok=True)
        os.makedirs(os.path.join(self.PLOTDIR, "crawloverlap"), exist_ok=True)
        os.makedirs(os.path.join(self.PLOTDIR, "crawlsize"), exist_ok=True)
        os.makedirs(os.path.join(self.PLOTDIR, "tld"), exist_ok=True)


    def read_from_stdin_or_file(self):
        """Read statistics data from a file argument or stdin.

        If a file path is provided as the first command line argument,
        reads from that file (supports gzip compression). Otherwise,
        reads from stdin.
        """
        if len(sys.argv) > 1:
            # File provided as argument
            fp = sys.argv[1]
            compression = ("gzip" if fp.endswith(".gz") else None)

            with fsspec.open(fp, 'r', compression=compression) as f:
                self.read_data(f)
        else:
            # No argument, use stdin
            self.read_data(sys.stdin)

    def read_data(self, stream):
        """Parse tab-separated JSON key-value pairs from a stream.

        Args:
            stream: Input stream containing lines of tab-separated JSON data.
                   Each line should have format: JSON_KEY<tab>JSON_VALUE
        """
        for line in stream:
            keyval = line.split('\t')
            if len(keyval) == 2:
                key = json.loads(keyval[0])
                val = json.loads(keyval[1])
                self.add(key, val)
            else:
                logging.error("Not a key-value pair: {}".find(line))

    def line_plot_with_ggplot(
        self,
        data,
        title,
        ylabel,
        img_path,
        x="date",
        y="size",
        c="type",
        clabel="",
        ratio=1.0,
    ):
        """Generate a line plot using the legacy ggplot library (deprecated)."""
        from ggplot import ggplot, aes, ggtitle, ylab, xlab, scale_x_date, date_breaks, geom_line, geom_point

        date_label = "%Y\n%W"  # year + week number
        p = (
            ggplot(data, aes(x=x, y=y, color=c))
            + ggtitle(title)
            + ylab(ylabel)
            + xlab(" ")
            + scale_x_date(breaks=date_breaks("3 months"), labels=date_label)
            + geom_line()
            + geom_point()
        )
        p.save(img_path)
        return p

    def line_plot_with_rpy2_ggplot2(
        self,
        data,
        title,
        ylabel,
        img_path,
        x="date",
        y="size",
        c="type",
        clabel="",
        ratio=1.0,
    ):
        """Generate a line plot using R's ggplot2 via rpy2."""
        from rpy2.robjects.lib import ggplot2

        # Convert y axis to float because R uses 32-bit signed integers
        # and values >= 2 billion (2^31) will overflow
        data[y] = data[y].astype(float)
        if y != "size" and "size" in data.columns:
            data["size"] = data["size"].astype(float)
        p = (
            ggplot2.ggplot(data)
            + ggplot2.aes_string(x=x, y=y, color=c)
            + ggplot2.geom_line(linewidth=0.5)
            + ggplot2.geom_point()
            + self.GGPLOT2_THEME
            + ggplot2.theme(
                **{
                    "legend.position": "bottom",
                    "aspect.ratio": ratio,
                    **self.GGPLOT2_THEME_KWARGS,
                }
            )
            + ggplot2.labs(title=title, x="", y=ylabel, color=clabel)
        )

        p.save(img_path)

        return p

    @staticmethod
    def nice_tick_step(vmin, vmax, n=5):
        """Calculate a 'nice' tick step for axis labels.

        Returns a tick step value that is a multiple of 1, 2, or 5 times
        a power of 10, which produces clean, readable axis labels.

        Args:
            vmin: Minimum value of the axis range
            vmax: Maximum value of the axis range
            n: Approximate number of tick intervals desired (default: 5)

        Returns:
            A 'nice' tick step value (1/2/5 * 10^k)
        """
        span = abs(vmax - vmin)
        if span == 0:
            return 1.0
        raw = span / n
        exp = np.floor(np.log10(raw))
        frac = raw / (10**exp)
        nice_frac = 1 if frac <= 1 else 2 if frac <= 2 else 5 if frac <= 5 else 10
        return nice_frac * 10**exp
    
    @staticmethod
    def center_legend_title(fig, ax, leg_items, leg_title, x_axes=0.1):
        """Center the legend title vertically with respect to legend items."""
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        bb = leg_items.get_window_extent(r)
        y = fig.transFigure.inverted().transform((0, (bb.y0+bb.y1)/2))[1]
        x = fig.transFigure.inverted().transform(ax.transAxes.transform((x_axes, 0)))[0]
        leg_title.set_bbox_to_anchor((x, y), transform=fig.transFigure)

    def line_plot_with_matplotlib(
        self,
        data,
        title,
        ylabel,
        img_path,
        x="date",
        y="size",
        c="type",
        clabel="",
        ratio=1.0,
    ):
        """Generate a line plot using matplotlib with ggplot2-like styling.

        Creates a multi-series line plot with markers, styled to match
        ggplot2's minimal theme aesthetic.

        Args:
            data: pandas DataFrame containing the plot data
            title: Plot title
            ylabel: Y-axis label
            img_path: Output file path for the saved image
            x: Column name for x-axis values (default: 'date')
            y: Column name for y-axis values (default: 'size')
            c: Column name for grouping/color (default: 'type')
            clabel: Legend title (default: '')
            ratio: Aspect ratio for the plot (default: 1.0)

        Returns:
            matplotlib Figure object
        """
        from matplotlib.ticker import AutoMinorLocator
        from matplotlib.dates import YearLocator, DateFormatter

        # Convert y axis to float for consistency with large values
        data[y] = data[y].astype(float)
        if y != "size" and "size" in data.columns:
            data["size"] = data["size"].astype(float)

        fig, ax = self.create_figure()
        groups = data.groupby(c)

        # Use ggplot2 default colors for small group counts
        colors = ["#F8766D", "#00BA38", "#619CFF"] if len(groups) <= 3 else None

        for i, (group_key, group_df) in enumerate(groups):
            group_color = colors[i] if colors is not None else None
            ax.plot(
                group_df[x], group_df[y], "o-",
                color=group_color, label=group_key,
                linewidth=self.line_width, markersize=self.marker_size,
            )

        self.set_title(ax, title)
        ax.set_xlabel("")
        ax.set_ylabel(ylabel, fontsize=self.ylabel_fontsize)

        # Apply nice y-axis ticks
        self.apply_nice_ticks(ax, axis='y')

        # Axes ratio
        axes_aspect_ratio = 1 / ax.get_data_ratio() * ratio
        if axes_aspect_ratio < 1:
            ax.set_aspect(axes_aspect_ratio)

        # Date formatting for x-axis
        ax.xaxis.set_major_formatter(DateFormatter("%Y"))
        ax.xaxis.set_major_locator(YearLocator(base=5))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        ax.tick_params(axis="both", labelsize=self.ticks_fontsize)

        # Grid with both major and minor lines
        ax.grid(True, which="major", linewidth=self.grid_major_linewidth,
                color=self.grid_major_color, zorder=0)
        ax.grid(True, which="minor", linewidth=self.grid_minor_linewidth,
                color=self.grid_minor_color, zorder=0)
        ax.set_axisbelow(True)

        # Apply ggplot2 style (remove spines)
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)

        # Hide tick marks but keep labels black
        self.hide_tick_marks(ax)
        self.set_tick_labels_black(ax)

        # Legend setup
        num_legend_items = len(groups)
        ncol = 5 if num_legend_items == 5 else 4

        if clabel:
            leg_items = ax.legend(
                loc="upper center", ncol=ncol, bbox_to_anchor=(0.6, -0.1),
                frameon=False, fontsize=self.legend_fontsize,
            )
            ax.legend(
                [], [], title=clabel, loc="upper center",
                bbox_to_anchor=(0.2, -0.075), frameon=False,
                title_fontsize=self.legend_title_fontsize,
            )
            ax.add_artist(leg_items)
        else:
            ax.legend(
                loc="upper center", bbox_to_anchor=(0.5, -0.1),
                ncol=ncol, frameon=False, fontsize=self.legend_fontsize,
            )

        return self.save_figure(fig, img_path)

    def line_plot(
        self,
        data,
        title,
        ylabel,
        img_file,
        x="date",
        y="size",
        c="type",
        clabel="",
        ratio=1.0,
    ):
        """Generate a line plot using the configured plotting library.

        This is the main entry point for creating line plots. It delegates
        to the appropriate backend based on the PLOTLIB setting.

        Args:
            data: pandas DataFrame containing the plot data
            title: Plot title
            ylabel: Y-axis label
            img_file: Output filename relative to PLOTDIR
            x: Column name for x-axis values (default: 'date')
            y: Column name for y-axis values (default: 'size')
            c: Column name for grouping/color (default: 'type')
            clabel: Legend title (default: '')
            ratio: Aspect ratio for the plot (default: 1.0)

        Returns:
            Plot object (type depends on backend)
        """
        img_path = os.path.join(self.PLOTDIR, img_file)

        if self.PLOTLIB == "ggplot":
            return self.line_plot_with_ggplot(
                data=data,
                title=title,
                ylabel=ylabel,
                img_path=img_path,
                x=x,
                y=y,
                c=c,
                clabel=clabel,
                ratio=ratio,
            )

        elif self.PLOTLIB == "rpy2.ggplot2":
            return self.line_plot_with_rpy2_ggplot2(
                data=data,
                title=title,
                ylabel=ylabel,
                img_path=img_path,
                x=x,
                y=y,
                c=c,
                clabel=clabel,
                ratio=ratio,
            )

        elif self.PLOTLIB == "matplotlib":
            return self.line_plot_with_matplotlib(
                data=data,
                title=title,
                ylabel=ylabel,
                img_path=img_path,
                x=x,
                y=y,
                c=c,
                clabel=clabel,
                ratio=ratio,
            )
