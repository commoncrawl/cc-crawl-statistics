"""
Plot crawler performance metrics.

This module generates visualizations of crawler metrics including:
- Fetch status breakdown (success, redirect, denied, failed, skipped)
- CrawlDb status counts
- HTTP vs HTTPS URL distribution

These metrics help monitor crawler health and performance over time.
"""

import logging
import os
import re

from collections import defaultdict

import pandas

from crawlstats import CST, MultiCount
from crawl_size import CrawlSizePlot


LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=LOGGING_LEVEL)

def human_format(v, _pos=None):
    """Format large tick values as billions or millions."""
    if v >= 1e9:
        return '%g B' % (v / 1e9)
    if v >= 1e6:
        return '%g M' % (v / 1e6)
    return '%g' % v


class CrawlerMetrics(CrawlSizePlot):
    """Generate plots showing crawler performance metrics.

    Tracks fetch statuses, CrawlDb sizes, and URL protocol distribution
    across crawls.
    """

    metrics_map = {
        'fetcher:aggr:redirect': ('fetcher:temp_moved', 'fetcher:moved',
                                  'fetcher:redirect_count_exceeded',
                                  'fetcher:redirect_deduplicated',
                                  # new counter names (NUTCH-3132)
                                  # unchanged: 'fetcher:temp_moved', 'fetcher:moved',
                                  'fetcher:redirect_count_exceeded_total',
                                  'fetcher:redirect_deduplicated_total',
                                  'fetcher:redirect_not_created_total'),
        'fetcher:aggr:denied':   ('fetcher:access_denied',
                                  'fetcher:robots_denied',
                                  'fetcher:robots_denied_maxcrawldelay',
                                  'fetcher:robots_defer_visits_dropped',
                                  'fetcher:filter_denied',
                                  # new counter names (NUTCH-3132)
                                  # unchanged: 'fetcher:access_denied',
                                  'fetcher:robots_denied_total',
                                  'fetcher:robots_denied_maxcrawldelay_total',
                                  'fetcher:robots_defer_visits_dropped_total'),
        'fetcher:aggr:failed':   ('fetcher:gone', 'fetcher:notfound',
                                  'fetcher:exception',
                                  # (no) new counter names (NUTCH-3132)
                                  ),
        'fetcher:aggr:skipped':  ('fetcher:hitByThrougputThreshold',
                                  'fetcher:hitByTimeLimit',
                                  'fetcher:AboveExceptionThresholdInQueue',
                                  'fetcher:filtered',
                                  # new counter names (NUTCH-3132)
                                  'fetcher:hit_by_throughput_threshold_total',
                                  'fetcher:hit_by_timelimit_total',
                                  'fetcher:above_exception_threshold_total',
                                  'fetcher:hit_by_timeout_total',
                                  'fetcher:filtered_total')
    }

    def __init__(self):
        super().__init__()
        self.sum_counts = True
        self.type_values = defaultdict(set)

    def add(self, key, val):
        """Process crawl status, size, and scheme records."""
        cst = CST[key[0]]
        item_type = key[1]
        crawl = key[2]
        if not (cst == CST.crawl_status or
                (cst == CST.size and item_type in ('page', 'url'))
                or cst == CST.scheme):
            return
        if cst == CST.scheme:
            item_type = 'scheme:' + item_type
            val = MultiCount.get_count(1, val)
        self.add_by_type(crawl, item_type, val)
        for metric in self.metrics_map:
            if item_type in self.metrics_map[metric]:
                logging.debug('Adding metric %s for <%s, %s> = %s', metric, crawl, item_type, val)
                self.add_by_type(crawl, metric, val)

    def save_data(self):
        """Save crawler metrics data to CSV files."""
        self.size.sort_values(['crawl'], inplace=True)
        self.size.to_csv('data/crawlmetrics.csv')
        self.size_by_type.to_csv('data/crawlmetricsbytype.csv')

    def add_percent(self):
        """Calculate percentage values for fetch statuses and schemes."""
        for crawl in self.crawls:
            if self.crawls[crawl] not in self.size['fetcher:total']:
                logging.debug('Crawl %s not found in fetch status data', crawl)
                continue
            total = self.size['fetcher:total'][self.crawls[crawl]]
            total_urls = self.size['url'][self.crawls[crawl]]
            for item_type in self.type_index:
                if self.crawls[crawl] not in self.size[item_type]:
                    continue
                count = self.size[item_type][self.crawls[crawl]]
                _N = self.type_index[item_type][self.crawls[crawl]]
                if (item_type.startswith('fetcher:') and
                    item_type != 'fetcher:total'):
                    self.size_by_type['percentage'][_N] = 100.0*count/total
                elif item_type.startswith('scheme:'):
                    self.size_by_type['percentage'][_N] = 100.0*count/total_urls
        for crawl in self.crawls:
            total = 0
            total_https = 0
            for item_type in self.type_index:
                if self.crawls[crawl] not in self.size[item_type]:
                    continue
                if item_type.startswith('http_protocol_version:'):
                    total += self.size[item_type][self.crawls[crawl]]
                elif item_type.startswith('tls_protocol_version:'):
                    total_https += self.size[item_type][self.crawls[crawl]]
            if total == 0:
                continue
            self.add_by_type(crawl, 'tls_protocol_version:(no SSL/TLS)', (total - total_https))
            for item_type in self.type_index:
                if self.crawls[crawl] not in self.size[item_type]:
                    continue
                count = self.size[item_type][self.crawls[crawl]]
                _N = self.type_index[item_type][self.crawls[crawl]]
                if item_type.startswith('http_protocol_version:'):
                    self.size_by_type['percentage'][_N] = 100.0*count/total
                    self.type_values['http_protocol_version'].add(item_type)
                elif item_type.startswith('tls_protocol_version:'):
                    self.size_by_type['percentage'][_N] = 100.0*count/total_https
                    self.type_values['tls_protocol_version'].add(item_type)
                elif item_type.startswith('ip_address_version:'):
                    self.size_by_type['percentage'][_N] = 100.0*count/total
                    self.type_values['ip_address_version'].add(item_type)

    @staticmethod
    def row2title(row):
        """Convert metric row name to human-readable title."""
        row = re.sub('(?<=^fetch)er(?::aggr)?|^generator:', '', row)
        row = re.sub('[:_]', ' ', row)
        if row == 'page':
            row = 'pages released'
        return row

    def plot(self):
        """Generate all crawler metrics plots."""
        row_types = ['generator:fetch_list',
                     'fetcher:success', 'fetcher:total',
                     'fetcher:aggr:redirect', 'fetcher:notmodified',
                     'fetcher:aggr:failed', 'fetcher:aggr:denied',
                     'fetcher:aggr:skipped', 'page']
        self.size_plot(self.size_by_type, row_types, CrawlerMetrics.row2title,
                       'Crawler Metrics', 'Pages',
                       'crawler/metrics.png')
        # -- stacked bar plot
        row_types = ['fetcher:success', 'fetcher:notmodified',
                     'fetcher:aggr:redirect', 'fetcher:aggr:failed',
                     'fetcher:aggr:denied', 'fetcher:aggr:skipped']
        self.plot_fetch_status_time(self.size_by_type, row_types,
                                    'crawler/fetch_status_percentage.png')
        # -- status of pages in CrawlDb
        row_types = ['crawldb:status:db_fetched',
                     'crawldb:status:db_notmodified',
                     'crawldb:status:db_redir_perm',
                     'crawldb:status:db_redir_temp',
                     'crawldb:status:db_duplicate',
                     'crawldb:status:db_gone',
                     'crawldb:status:db_unfetched',
                     'crawldb:status:db_orphan']
        self.plot_crawldb_status_time(self.size_by_type, row_types,
                                      'crawler/crawldb_status.png')
        # successfully fetched http:// vs https:// URLs
        self.size_plot(self.size_by_type, ['scheme:http', 'scheme:https'], lambda x: x.split(':')[1],
                       'HTTP vs HTTPS URLs', 'Successfully fetched URLs',
                       'crawler/url_protocols.png')
        self.size_plot(self.size_by_type,
                       ['scheme:http', 'scheme:https'],
                       lambda x: x.split(':')[1],
                       'Percentage of HTTP vs HTTPS URLs',
                       'Percentage of successfully fetched URLs',
                       'crawler/url_protocols_percentage.png',
                       y='percentage')
        self.size_plot(self.size_by_type,
                       list(self.type_values['http_protocol_version']),
                       lambda x: x.split(':')[1],
                       'HTTP Protocol Version',
                       'Percentage of HTTP Requests',
                       'crawler/http_protocol_version_percentage.png',
                       'percentage',
                       'crawler/http_protocol_version.csv',
                       y='percentage')
        self.size_plot(self.size_by_type,
                       list(self.type_values['tls_protocol_version']),
                       lambda x: x.split(':')[1],
                       'TLS Version',
                       'Percentage of HTTP Requests',
                       'crawler/tls_protocol_version_percentage.png',
                       'percentage',
                       'crawler/tls_protocol_version.csv',
                       y='percentage')
        self.size_plot(self.size_by_type,
                       list(self.type_values['ip_address_version']),
                       lambda x: x.split(':')[1],
                       'IPv4 vs. IPv6',
                       'Percentage of HTTP Requests',
                       'crawler/ip_address_version_percentage.png',
                       'percentage',
                       'crawler/ip_address_version.csv',
                       y='percentage')

    def plot_fetch_status_with_rpy2_ggplot2(self, data, img_path, ratio):
        """Generate fetch status stacked bar chart using rpy2/ggplot2."""
        from rpy2.robjects.lib import ggplot2

        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl', y='percentage', fill='type') \
            + ggplot2.geom_bar(stat='identity', position='stack', width=.9) \
            + ggplot2.coord_flip() \
            + ggplot2.scale_fill_brewer(palette='RdYlGn', type='sequential',
                                        guide=ggplot2.guide_legend(reverse=True)) \
            + self.GGPLOT2_THEME \
            + ggplot2.theme(**{'legend.position': 'bottom',
                            'aspect.ratio': ratio,
                            **self.GGPLOT2_THEME_KWARGS}) \
            + ggplot2.labs(title='Percentage of Fetch Status',
                        x='', y='', fill='')

        p.save(img_path, height = int(7 * ratio), width = 7)

        return p

    def plot_fetch_status_with_matplotlib(self, data, categories, img_path, ratio):
        """Generate fetch status stacked bar chart using matplotlib."""
        import numpy as np
        from matplotlib.ticker import MaxNLocator

        crawls = data['crawl'].unique()
        n_crawls = len(crawls)

        # Define colors from dark green (success) to dark red (denied)
        status_order = ['success', 'skipped', 'redirect', 'notmodified', 'failed', 'denied']
        status_colors = {
            'success': '#1A9850', 'skipped': '#91CF60', 'redirect': '#D9EF8B',
            'notmodified': '#FEE08B', 'failed': '#FC8D59', 'denied': '#D73027'
        }
        categories_ordered = [cat for cat in status_order if cat in categories]

        fig, ax = self.create_figure(ratio=ratio)

        # Prepare data for horizontal stacked bar chart
        bar_positions = np.arange(n_crawls)
        lefts = np.zeros(n_crawls)

        for category in categories_ordered:
            category_data = data[data['type'] == category]
            values = [
                category_data[category_data['crawl'] == crawl]['percentage'].iloc[0]
                if len(category_data[category_data['crawl'] == crawl]) > 0 else 0
                for crawl in crawls
            ]
            ax.barh(bar_positions, values, left=lefts, height=self.bar_width,
                    color=status_colors[category], label=category)
            lefts += values

        self.set_title(ax, 'Percentage of Fetch Status')
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Format y-axis (crawl names)
        ax.set_yticks(bar_positions)
        ax.set_yticklabels(crawls, fontsize=self.ticks_fontsize)
        ax.set_ylim(-0.5, n_crawls - 0.5)

        # Format x-axis (percentage)
        max_value = lefts.max()
        ax.set_xlim(0, max_value * 1.02)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))

        # Apply ggplot2-like styling
        self.apply_ggplot2_style(ax, grid_axis='x')

        # Set tick colors
        ax.tick_params(axis='y', which='both', colors='#E6E6E6', length=20,
                       width=1.5, labelsize=self.ticks_fontsize)
        ax.tick_params(axis='x', which='both', colors='#E6E6E6', length=4,
                       width=1.5, labelsize=self.ticks_fontsize)
        self.set_tick_labels_black(ax)

        # Position legend at bottom
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  ncol=min(3, len(categories)), frameon=False,
                  fontsize=self.legend_fontsize, title='')

        return self.save_figure(fig, img_path)

    def plot_fetch_status(self, data, row_filter, img_file, ratio=1.0):
        """Generate fetch status percentage stacked bar chart."""
        if row_filter:
            data = data[data['type'].isin(row_filter)]
        data = data[['crawl', 'percentage', 'type']]
        categories = []
        for value in row_filter:
            if re.search('^fetcher:(?:aggr:)?', value):
                replacement = re.sub('^fetcher:(?:aggr:)?', '', value)
                categories.append(replacement)
                data.replace(to_replace=value, value=replacement, inplace=True)
        data['type'] = pandas.Categorical(data['type'], ordered=True,
                                          categories=categories.reverse())
        ratio = 0.1 + len(data['crawl'].unique()) * .03
        img_path = os.path.join(self.PLOTDIR, img_file)

        if self.PLOTLIB == "rpy2.ggplot2":
            return self.plot_fetch_status_with_rpy2_ggplot2(data=data, img_path=img_path, ratio=ratio)
        elif self.PLOTLIB == "matplotlib":
            return self.plot_fetch_status_with_matplotlib(data=data, categories=categories, img_path=img_path, ratio=ratio)
        else:
            raise ValueError("Invalid PLOTLIB")

    # Fixed axes rectangle (fractions of the figure) shared by all
    # time-axis figures, so the x-axis has identical pixel geometry
    # (same range, same width, same step size) in every plot
    TIME_AXES_RECT = (0.11, 0.20, 0.86, 0.66)

    # Width in days of one bar in the time-axis figures: the shortest
    # interval between two crawls (3 weeks, also about the fetch phase
    # duration of a monthly crawl), so bars never overlap, touch where
    # crawls ran back-to-back, and longer gaps between crawls remain
    # visible
    TIME_BAR_WIDTH = 21.0

    @staticmethod
    def time_axis(index):
        """Convert a DatetimeIndex to numeric x-positions for bars of
        fixed width TIME_BAR_WIDTH, left-aligned on the crawl date.

        Returns (x, xlim) where xlim is aligned to full years so that
        all time-axis figures share the same x-axis range.
        """
        from matplotlib.dates import date2num, num2date

        x = date2num(index)
        xmin = date2num(pandas.Timestamp(year=index[0].year,
                                         month=1, day=1))
        last = num2date(x[-1] + CrawlerMetrics.TIME_BAR_WIDTH)
        xmax = date2num(pandas.Timestamp(year=last.year + 1,
                                         month=1, day=1))
        return x, (xmin, xmax)

    def style_time_axes(self, fig, ax, title, ylabel, xlim, handles, labels,
                        legend_ncol, img_file):
        """Apply the shared layout of the time-axis figures and save.

        The axes are pinned to TIME_AXES_RECT and the figure is saved
        without tight_layout, so the plot geometry is identical across
        all time-axis figures.
        """
        import matplotlib.pyplot as plt
        from matplotlib.ticker import AutoMinorLocator
        from matplotlib.dates import YearLocator, DateFormatter

        ax.set_position(self.TIME_AXES_RECT)
        self.set_title(ax, title)
        ax.set_xlabel('')
        ax.set_ylabel(ylabel, fontsize=self.ylabel_fontsize)
        ax.set_xlim(*xlim)

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(DateFormatter('%Y'))
        ax.xaxis.set_major_locator(YearLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        self.apply_ggplot2_style(ax, grid_axis='y')
        # no vertical grid lines: the year ticks are enough and the
        # lines would interfere with the tightly spaced bars
        ax.grid(False, axis='x')
        ax.tick_params(axis='both', labelsize=self.ticks_fontsize)
        self.hide_tick_marks(ax)
        self.set_tick_labels_black(ax)

        ax.legend(handles, labels, loc='upper center',
                  bbox_to_anchor=(0.5, -0.1), ncol=legend_ncol,
                  frameon=False, fontsize=self.legend_fontsize)

        img_path = os.path.join(self.PLOTDIR, img_file)
        fig.savefig(img_path, dpi=self.DEFAULT_DPI,
                    facecolor=self.savefig_facecolor)
        plt.close(fig)
        return fig

    def plot_stacked_status_time(self, data, row_filter, prefix_re,
                                 status_order, status_colors, title, ylabel,
                                 img_file, value='size', yformatter=None):
        """Generate status counts as vertical stacked bars over time.

        The x-axis is the crawl date (datetime derived from the crawl
        label) and every crawl gets a bar of fixed width, so single
        crawls remain distinguishable, the irregular intervals between
        crawls are visible as gaps and the figure keeps a fixed
        landscape size regardless of the number of crawls.
        """
        import numpy as np
        from matplotlib.ticker import FuncFormatter

        data = data[data['type'].isin(row_filter)].copy()
        data['type'] = data['type'].str.replace(prefix_re, '', regex=True)
        data[value] = data[value].astype(float)
        wide = data.pivot_table(index='date', columns='type', values=value,
                                aggfunc='sum').fillna(0.0).sort_index()
        categories = [c for c in status_order if c in wide.columns]

        x, xlim = self.time_axis(wide.index)

        fig, ax = self.create_figure(ratio=0.6)

        bottom = np.zeros(len(wide))
        for category in categories:
            values = wide[category].to_numpy()
            ax.bar(x, values, bottom=bottom, width=self.TIME_BAR_WIDTH,
                   align='edge', color=status_colors[category],
                   label=category)
            bottom += values

        ax.set_ylim(0, bottom.max() * 1.05)
        if yformatter is not None:
            ax.yaxis.set_major_formatter(FuncFormatter(yformatter))

        # legend reversed so it matches the visual top-to-bottom
        # stack order
        handles, labels = ax.get_legend_handles_labels()
        return self.style_time_axes(fig, ax, title, ylabel, xlim,
                                    handles[::-1], labels[::-1], 4, img_file)

    def plot_crawldb_status_time(self, data, row_filter, img_file):
        """Generate CrawlDb status as vertical stacked bars over time."""
        # Stack order (bottom to top), grouped by lifecycle: successfully
        # fetched, redirects, dead or duplicate, still to be fetched
        status_order = ['fetched', 'notmodified',
                        'redir_perm', 'redir_temp',
                        'gone', 'duplicate', 'orphan',
                        'unfetched']
        status_colors = {
            'fetched': '#6BAED6', 'notmodified': '#9E9AC8',
            'redir_perm': '#FFD92F', 'redir_temp': '#C49C64',
            'gone': '#74C476', 'duplicate': '#FB6A4A', 'orphan': '#FDAE6B',
            'unfetched': '#F4A3C8',
        }

        return self.plot_stacked_status_time(
            data, row_filter, '^crawldb:status:db_',
            status_order, status_colors,
            'CrawlDb Size and Status Counts', 'URLs in CrawlDb',
            img_file, yformatter=human_format)

    def plot_fetch_status_time(self, data, row_filter, img_file):
        """Generate fetch status percentage as vertical stacked bars over
        time."""
        # Stack order (bottom to top), from dark green (success) to
        # dark red (denied)
        status_order = ['success', 'skipped', 'redirect',
                        'notmodified', 'failed', 'denied']
        status_colors = {
            'success': '#1A9850', 'skipped': '#91CF60',
            'redirect': '#D9EF8B', 'notmodified': '#FEE08B',
            'failed': '#FC8D59', 'denied': '#D73027',
        }
        return self.plot_stacked_status_time(
            data, row_filter, '^fetcher:(?:aggr:)?',
            status_order, status_colors,
            'Percentage of Fetch Status', 'Percentage of fetched pages',
            img_file, value='percentage')

    def plot_crawldb_status_with_rpy2_ggplot2(self, data, img_path, ratio):
        """Generate CrawlDb status stacked bar chart using rpy2/ggplot2."""
        from rpy2.robjects.lib import ggplot2

        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl', y='size', fill='type') \
            + ggplot2.geom_bar(stat='identity', position='stack', width=.9) \
            + ggplot2.coord_flip() \
            + ggplot2.scale_fill_brewer(palette='Pastel1', type='sequential',
                                        guide=ggplot2.guide_legend(reverse=False)) \
            + self.GGPLOT2_THEME \
            + ggplot2.theme(**{'legend.position': 'bottom',
                            'aspect.ratio': ratio,
                            **self.GGPLOT2_THEME_KWARGS}) \
            + ggplot2.labs(title='CrawlDb Size and Status Counts',
                        x='', y='', fill='')

        p.save(img_path, height = int(7 * ratio), width = 7)
        return p

    def plot_crawldb_status_with_matplotlib(self, data, img_path, ratio):
        """Generate CrawlDb status stacked bar chart using matplotlib."""
        import numpy as np

        crawls = data['crawl'].unique()
        n_crawls = len(crawls)

        # Pastel1 palette colors
        pastel1_colors = ['#FDDAEC', '#E5D8BD', '#FFFFCC', '#FED9A6',
                          '#DECBE4', '#CCEBC5', '#B3CDE3', '#FBB4AE', '#F2F2F2']
        categories_ordered = ['unfetched', 'redir_temp', 'redir_perm', 'orphan',
                              'notmodified', 'gone', 'fetched', 'duplicate']

        fig, ax = self.create_figure(ratio=ratio)

        bar_positions = np.arange(n_crawls)
        lefts = np.zeros(n_crawls)

        for i, category in enumerate(categories_ordered):
            category_data = data[data['type'] == category]
            values = [
                category_data[category_data['crawl'] == crawl]['size'].iloc[0]
                if len(category_data[category_data['crawl'] == crawl]) > 0 else 0
                for crawl in crawls
            ]
            color = pastel1_colors[i % len(pastel1_colors)]
            ax.barh(bar_positions, values, left=lefts, height=self.bar_width,
                    color=color, label=category)
            lefts += values

        self.set_title(ax, 'CrawlDb Size and Status Counts')
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Format y-axis (crawl names)
        ax.set_yticks(bar_positions)
        ax.set_yticklabels(crawls, fontsize=self.ticks_fontsize)
        ax.set_ylim(-0.5, n_crawls - 0.5)

        # Format x-axis (size counts)
        max_value = lefts.max()
        ax.set_xlim(0, max_value * 1.02)

        # Axes ratio
        ax.set_aspect(1 / ax.get_data_ratio() * ratio)

        # Apply nice x-axis ticks
        self.apply_nice_ticks(ax, axis='x')

        # Apply ggplot2-like styling with x-axis grid
        ax.grid(True, which='both', linewidth=self.grid_major_linewidth,
                color=self.grid_major_color, zorder=0, axis='x')
        ax.set_axisbelow(True)
        self.apply_ggplot2_style(ax, show_grid=False)

        # Set tick colors
        ax.tick_params(axis='both', which='both', colors=self.ticks_color,
                       length=self.ticks_length, width=0.8,
                       labelsize=self.ticks_fontsize)
        self.set_tick_labels_black(ax)

        # Position legend at bottom with reversed order
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc='upper center',
                  bbox_to_anchor=(0.5, -0.05), ncol=min(4, len(categories_ordered)),
                  frameon=False, fontsize=self.legend_fontsize, title='')

        return self.save_figure(fig, img_path)

    def plot_crawldb_status(self, data, row_filter, img_file, ratio=1.0):
        """Generate CrawlDb status stacked bar chart."""
        if row_filter:
            data = data[data['type'].isin(row_filter)]
        categories = []
        for value in row_filter:
            if re.search('^crawldb:status:db_', value):
                replacement = re.sub('^crawldb:status:db_', '', value)
                categories.append(replacement)
                data.replace(to_replace=value, value=replacement, inplace=True)
        data['type'] = pandas.Categorical(data['type'], ordered=True,
                                          categories=categories.reverse())
        data['size'] = data['size'].astype(float)
        ratio = 0.1 + len(data['crawl'].unique()) * .03
        img_path = os.path.join(self.PLOTDIR, img_file)

        if self.PLOTLIB == "rpy2.ggplot2":
            return self.plot_crawldb_status_with_rpy2_ggplot2(
                data=data, img_path=img_path, ratio=ratio
            )

        elif self.PLOTLIB == "matplotlib":
            return self.plot_crawldb_status_with_matplotlib(
                data=data, img_path=img_path, ratio=ratio
            )

        else:
            raise ValueError("Invalid PLOTLIB")


if __name__ == '__main__':
    plot = CrawlerMetrics()
    plot.read_from_stdin_or_file()
    plot.add_percent()
    plot.transform_data()
    plot.save_data()
    print(plot.type_values)
    plot.plot()
