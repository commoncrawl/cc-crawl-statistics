import json
import logging
import os.path
import os
from typing import Literal
import fsspec
import sys

# Supported plot libraries
PlotLibType = Literal["rpy2.ggplot2", "ggplot", "matplotlib"]


class CrawlPlot:
    """Base class for crawl plots implementing utility functions."""
    GGPLOT2_THEME = None
    GGPLOT2_THEME_KWARGS = None

    # figure with square aspect ratio : 7 inches * 300 DPI = 2100 pixels
    DEFAULT_FIGSIZE = 7
    DEFAULT_DPI = 300

    def __init__(self):
                
        # Settings defined via environment variables
        self.PLOTLIB: PlotLibType = os.environ.get('PLOTLIB', 'rpy2.ggplot2')
        self.PLOTDIR = os.environ.get('PLOTDIR', 'plots')

        print("PLOTLIB = ", self.PLOTLIB)
        print("PLOTDIR = ", self.PLOTDIR)

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
            # GGPLOT2_THEME = ggplot2.theme_grey()

        elif self.PLOTLIB == "matplotlib":
            import matplotlib.pyplot as plt

            ggplot_colors = [
                "#F8766D", "#00BE67", "#00A9FF", "#CD9600", "#7CAE00", 
                "#00BFC4",  "#C77CFF", "#FF61CC",
            ]  # "#00A9FF", "#F8766D", "#00BE67"

            # Set up ggplot2-like minimal theme with larger fonts
            plt.style.use('default')
            plt.rcParams.update({
                # 'font.family': 'Helvetica',  # True Helvetica is proprietary and requires a license.
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
        from rpy2.robjects.lib import ggplot2

        # convert y axis to float because R uses 32-bit signed integers,
        # values >= 2 bln. (2^31) will overflow
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
        from matplotlib.ticker import FuncFormatter
        from matplotlib.ticker import AutoMinorLocator
        from matplotlib.ticker import MaxNLocator, FixedLocator
        from matplotlib.dates import YearLocator, DateFormatter
        import matplotlib.pyplot as plt

        title_fontsize = 14
        title_pad = 20
        ylabel_fontsize = 12
        ticks_fontsize = 9
        legend_fontsize = 10
        legend_title_fontsize = 11

        # convert y axis to float because R uses 32-bit signed integers,
        # values >= 2 bln. (2^31) will overflow
        data[y] = data[y].astype(float)
        if y != "size" and "size" in data.columns:
            data["size"] = data["size"].astype(float)

        # Plot the three metrics with significantly larger line thickness and points
        line_width = 0.75  # Much thicker lines to match original
        marker_size = 4  # Much larger points to match original

        fig, ax = plt.subplots(figsize=(self.DEFAULT_FIGSIZE, self.DEFAULT_FIGSIZE * ratio))

        groups = data.groupby(c)

        # specific colors depending on number of groups
        if len(groups) <= 3:
            # ggplot2 default colors (hue scale)
            colors = [
                "#F8766D",
                "#00BA38",
                "#619CFF",
            ]
        else:
            # default color schema
            colors = None

        for i, (group_key, group_df) in enumerate(groups):
            print(group_key, group_df)

            group_color = colors[i] if colors is not None else None
            ax.plot(
                group_df[x],
                group_df[y],
                "o-",
                color=group_color,
                label=group_key,
                linewidth=line_width,
                markersize=marker_size,
            )

        ax.set_title(
            title,
            fontsize=title_fontsize,
            fontweight="normal",
            pad=title_pad,
            loc="left",
        )
        ax.set_xlabel("")
        ax.set_ylabel(ylabel, fontsize=ylabel_fontsize)

        # First, let MaxNLocator determine nice tick locations
        ax.yaxis.set_major_locator(MaxNLocator(nbins="auto", prune=None, integer=False))

        # Then format them in scientific notation if numbers are large
        if data[y].max() > 1e4:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0e}"))

        # Show y-axis labels only every second tick
        yticks = ax.yaxis.get_major_ticks()
        for i, tick in enumerate(yticks):
            if i % 2 == 0:  # Hide every second label (even indices)
                tick.label1.set_visible(False)

        # Set aspect ratio to match ggplot2 (ratio=0.9 from the original code)
        ax.set_aspect(1 / ax.get_data_ratio() * ratio)
        ax.xaxis.set_major_formatter(DateFormatter("%Y"))  # Format as just the year
        ax.xaxis.set_major_locator(
            YearLocator(base=5)
        )  # Show years every 5 years (2010, 2015, 2020, 2025)
        ax.xaxis.set_minor_locator(
            AutoMinorLocator(2)
        )  # 4 minor ticks between majors = gridlines every year

        ax.tick_params(axis="both", labelsize=ticks_fontsize)

        # ggplot2-style grid: gray lines on white background
        # ax.grid(True, linewidth=0.8, color='#E6E6E6', zorder=0)
        ax.grid(True, which="major", linewidth=1.0, color="#E6E6E6", zorder=0)
        ax.grid(True, which="minor", linewidth=0.5, color="#E6E6E6", zorder=0)

        ax.set_axisbelow(True)

        # Remove top, right, and left spines, keep only bottom spine in gray
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)  # Hide y-axis line
        # ax.spines['bottom'].set_color('#E6E6E6')
        ax.spines["bottom"].set_visible(False)

        # Set tick colors to gray and increase tick length
        ax.tick_params(
            axis="both", which="both", colors="#FFF", length=8, width=1.5
        )  # #E6E6E6
        # But keep the tick labels black
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color("black")

        # Position legend at bottom like ggplot2 with larger font
        legend = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.05),
            ncol=4,
            frameon=False,
            fontsize=legend_fontsize,
        )

        plt.tight_layout()
        plt.savefig(img_path, dpi=self.DEFAULT_DPI, bbox_inches=None, facecolor="white")
        plt.close()

        return fig

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
