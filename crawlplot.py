import json
import logging
import os.path
import os
import fsspec
import sys

PLOTLIB = os.environ.get('PLOTLIB', 'rpy2.ggplot2')
PLOTDIR = os.environ.get('PLOTDIR', 'plots')

# MATPLOTLIB_PATH_SUFFIX = "__new.png"
MATPLOTLIB_PATH_SUFFIX = ""

if PLOTLIB == 'ggplot':
    from ggplot import *
elif PLOTLIB == 'rpy2.ggplot2':
    from rpy2.robjects.lib import ggplot2
    from rpy2.robjects import pandas2ri
    pandas2ri.activate()
    # use minimal theme with white background set in plot constructor
    # https://ggplot2.tidyverse.org/reference/ggtheme.html
    GGPLOT2_THEME = ggplot2.theme_minimal(base_size=12, base_family="Helvetica")

    GGPLOT2_THEME_KWARGS = {
        'panel.background': ggplot2.element_rect(fill='white', color='white'),
        'plot.background': ggplot2.element_rect(fill='white', color='white')
    }
    # GGPLOT2_THEME = ggplot2.theme_grey()

# elif PLOTLIB == "matplotlib":
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FixedLocator
from matplotlib.dates import YearLocator, DateFormatter
import numpy as np

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

# else:
#     raise ValueError("Invalid PLOTLIB defined")

class CrawlPlot:

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

    def line_plot(self, data, title, ylabel, img_file,
                  x='date', y='size', c='type', clabel='', ratio=1.0):
        img_path = os.path.join(PLOTDIR, img_file)
        
        if PLOTLIB == 'ggplot':
            # date_label = "%Y\n%b"
            date_label = "%Y\n%W"  # year + week number
            p = ggplot(data,
                       aes(x=x, y=y, color=c)) \
                + ggtitle(title) \
                + ylab(ylabel) \
                + xlab(' ') \
                + scale_x_date(breaks=date_breaks('3 months'),
                               labels=date_label) \
                + geom_line() + geom_point()
        elif PLOTLIB == 'rpy2.ggplot2':
            # convert y axis to float because R uses 32-bit signed integers,
            # values >= 2 bln. (2^31) will overflow
            data[y] = data[y].astype(float)
            if y != 'size' and 'size' in data.columns:
                data['size'] = data['size'].astype(float)
            p = ggplot2.ggplot(data) \
                + ggplot2.aes_string(x=x, y=y, color=c) \
                + ggplot2.geom_line(linewidth=.5) + ggplot2.geom_point() \
                + GGPLOT2_THEME \
                + ggplot2.theme(**{'legend.position': 'bottom',
                                   'aspect.ratio': ratio,
                                   **GGPLOT2_THEME_KWARGS}) \
                + ggplot2.labs(title=title, x='', y=ylabel, color=clabel)

        # elif PLOTLIB == "matplotlib":
        ##### matplotlib
        # Create the plot with exact dimensions to match original 2100x2100 resolution
        # Calculate figsize to get 2100x2100 pixels at 150 DPI: 2100/150 = 14 inches
        fig, ax = plt.subplots(figsize=(14, 14))

        # ggplot2 default colors (hue scale)
        # colors = ['#F8766D', '#00BA38', '#619CFF']  # Red, Green, Blue from ggplot2

        # Plot the three metrics with significantly larger line thickness and points
        line_width = 2.5  # Much thicker lines to match original        
        marker_size = 8   # Much larger points to match original

        for i, (group_key, group_df) in enumerate(data.groupby(c)):
            print(group_key, group_df)
            ax.plot(
                group_df[x], 
                group_df[y], 'o-', 
                #color=colors[i], 
                label=group_key, linewidth=line_width, markersize=marker_size)
            

        ax.set_title(title, fontsize=26, fontweight='normal', pad=30, loc='left')
        ax.set_xlabel('')
        ax.set_ylabel(ylabel, fontsize=24)

        # Format y-axis with scientific notation (e.g., 2e+09)
        from matplotlib.ticker import FuncFormatter

        # First, let MaxNLocator determine nice tick locations
        ax.yaxis.set_major_locator(MaxNLocator(nbins='auto', prune=None, integer=False))

        # Then format them in scientific notation if numbers are large
        if data[y].max() > 1e4:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        # Show y-axis labels only every second tick
        yticks = ax.yaxis.get_major_ticks()
        for i, tick in enumerate(yticks):
            if i % 2 == 0:  # Hide every second label (even indices)
                tick.label1.set_visible(False)

        # Set aspect ratio to match ggplot2 (ratio=0.9 from the original code)
        ax.set_aspect(1/ax.get_data_ratio() * 0.9)
        ax.xaxis.set_major_formatter(DateFormatter('%Y'))  # Format as just the year
        ax.xaxis.set_major_locator(YearLocator(base=5))  # Show years every 5 years (2010, 2015, 2020, 2025)

        from matplotlib.ticker import AutoMinorLocator
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))  # 4 minor ticks between majors = gridlines every year

        # ax.xaxis.set_minor_locator(YearLocator(base=2.5))
        # ax.xaxis.set_minor_formatter(DateFormatter('%Y'))
        # ax.xaxis.set_minor_locator(YearLocator(base=1))
        # Show x-axis labels only every second tick
        # xticks = ax.xaxis.get_major_ticks()
        # for i, tick in enumerate(xticks):
        #     if i % 2 == 0:  # Hide every second label (even indices)
        #         tick.label1.set_visible(False)

        # ggplot2-style grid: gray lines on white background
        # ax.grid(True, linewidth=0.8, color='#E6E6E6', zorder=0)
        ax.grid(True, which='major', linewidth=1.0, color='#E6E6E6', zorder=0)
        ax.grid(True, which='minor', linewidth=0.5, color='#E6E6E6', zorder=0)

        ax.set_axisbelow(True)

        # Remove top, right, and left spines, keep only bottom spine in gray
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)  # Hide y-axis line
        # ax.spines['bottom'].set_color('#E6E6E6')
        ax.spines['bottom'].set_visible(False)

        # Set tick colors to gray and increase tick length
        ax.tick_params(axis='both', which='both', colors='#FFF', length=8, width=1.5) # #E6E6E6
        # But keep the tick labels black
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')
            
        # Position legend at bottom like ggplot2 with larger font
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4,
                        frameon=False, fontsize=18)

        # Adjust layout
        plt.tight_layout()

        # Save the plot with exact dimensions to match original 2100x2100
        # Use bbox_inches=None to maintain exact figure size and set DPI to achieve 2100x2100
        plt.savefig(img_path + MATPLOTLIB_PATH_SUFFIX, dpi=150, bbox_inches=None, facecolor='white')
        plt.close()

        pass
        ######

        if PLOTLIB in {'ggplot', 'rpy2.ggplot2'}: 
            p.save(img_path)

        return p
