import os
import re
import sys

import pandas


from crawlstats import CST, MultiCount
from crawl_size import CrawlSizePlot




class CrawlerMetrics(CrawlSizePlot):

    metrics_map = {
        'fetcher:aggr:redirect': ('fetcher:temp_moved', 'fetcher:moved',
                                  'fetcher:redirect_count_exceeded',
                                  'fetcher:redirect_deduplicated'),
        'fetcher:aggr:denied':   ('fetcher:access_denied',
                                  'fetcher:robots_denied',
                                  'fetcher:robots_denied_maxcrawldelay',
                                  'fetcher:filter_denied'),
        'fetcher:aggr:failed':   ('fetcher:gone', 'fetcher:notfound',
                                  'fetcher:exception'),
        'fetcher:aggr:skipped':  ('fetcher:hitByThrougputThreshold',
                                  'fetcher:hitByTimeLimit',
                                  'fetcher:AboveExceptionThresholdInQueue',
                                  'fetcher:filtered')
    }

    def __init__(self):
        super().__init__()
        self.sum_counts = True

    def add(self, key, val):
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
                self.add_by_type(crawl, metric, val)

    def save_data(self):
        self.size.sort_values(['crawl'], inplace=True)
        self.size.to_csv('data/crawlmetrics.csv')
        self.size_by_type.to_csv('data/crawlmetricsbytype.csv')

    def add_percent(self):
        for crawl in self.crawls:
            for item_type in self.type_index:
                if self.crawls[crawl] not in self.size[item_type]:
                    continue
                count = self.size[item_type][self.crawls[crawl]]
                _N = self.type_index[item_type][self.crawls[crawl]]
                if (item_type.startswith('fetcher:') and
                    item_type != 'fetcher:total' and
                    self.crawls[crawl] in self.size['fetcher:total']):
                    total = self.size['fetcher:total'][self.crawls[crawl]]
                    self.size_by_type['percentage'][_N] = 100.0*count/total
                elif item_type.startswith('scheme:'):
                    total = self.size['url'][self.crawls[crawl]]
                    self.size_by_type['percentage'][_N] = 100.0*count/total

    @staticmethod
    def row2title(row):
        row = re.sub('(?<=^fetch)er(?::aggr)?|^generator:', '', row)
        row = re.sub('[:_]', ' ', row)
        if row == 'page':
            row = 'pages released'
        return row

    def plot(self):
        # -- line plot
        row_types = [# 'generator:crawldb_size',
                     'generator:fetch_list',
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
        ratio = 0.1 + self.ncrawls * .05
        self.plot_fetch_status(self.size_by_type, row_types,
                               'crawler/fetch_status_percentage.png',
                               ratio=ratio)
        # -- status of pages in CrawlDb
        row_types = ['crawldb:status:db_fetched',
                     'crawldb:status:db_notmodified',
                     'crawldb:status:db_redir_perm',
                     'crawldb:status:db_redir_temp',
                     'crawldb:status:db_duplicate',
                     'crawldb:status:db_gone',
                     'crawldb:status:db_unfetched',
                     'crawldb:status:db_orphan']
        self.plot_crawldb_status(self.size_by_type, row_types,
                                 'crawler/crawldb_status.png',
                                 ratio=ratio)
        # successfully fetched http:// vs https:// URLs
        self.size_plot(self.size_by_type, ['scheme:http', 'scheme:https'], lambda x: x.split(':')[1],
                       'HTTP vs HTTPS URLs', 'Successfully fetched URLs',
                       'crawler/url_protocols.png')
        self.size_plot(self.size_by_type, ['scheme:http', 'scheme:https'], lambda x: x.split(':')[1],
                       'Percentage of HTTP vs HTTPS URLs', 'Percentage of successfully fetched URLs',
                       'crawler/url_protocols_percentage.png', y='percentage')

    def plot_fetch_status_with_rpy2_ggplot2(self, data, img_path, ratio):
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
    
    def plot_fetch_status_with_matplotliob(self, data, categories, img_path, ratio):
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.ticker import FuncFormatter

        fig_width_px = 2100
        fig_height_px = 6000
        # Calculate figsize in inches
        fig_width = fig_width_px / self.DEFAULT_DPI
        fig_height = fig_height_px / self.DEFAULT_DPI
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Get unique crawls and categories
        crawls = data['crawl'].unique()
        n_crawls = len(crawls)

        # Define colors from dark green (success) to dark red (denied)
        # Categories in stacking order: success, skipped, redirect, notmodified, failed, denied
        status_order = ['success', 'skipped', 'redirect', 'notmodified', 'failed', 'denied']
        status_colors = {
            'success': '#1A9850',      # Dark green
            'skipped': '#91CF60',      # Light green
            'redirect': '#D9EF8B',     # Yellow-green
            'notmodified': '#FEE08B',  # Yellow
            'failed': '#FC8D59',       # Orange
            'denied': '#D73027'        # Dark red
        }

        # Use status_order instead of categories to ensure proper stacking order
        categories_ordered = [cat for cat in status_order if cat in categories]

        # Prepare data for horizontal stacked bar chart
        bar_positions = np.arange(n_crawls)

        # Create stacked bars
        lefts = np.zeros(n_crawls)

        for category in categories_ordered:
            category_data = data[data['type'] == category]
            values = []

            for crawl in crawls:
                crawl_data = category_data[category_data['crawl'] == crawl]
                if len(crawl_data) > 0:
                    values.append(crawl_data['percentage'].iloc[0])
                else:
                    values.append(0)

            ax.barh(bar_positions, values, left=lefts, height=0.8,
                color=status_colors[category], label=category)
            lefts += values

        # Set labels and title
        ax.set_title('Percentage of Fetch Status', fontsize=16, fontweight='normal',
                    pad=10, loc='left')
        ax.set_xlabel('', fontsize=24)
        ax.set_ylabel('', fontsize=24)

        # Format y-axis (crawl names)
        ax.set_yticks(bar_positions)
        ax.set_yticklabels(crawls, fontsize=12)
        # Remove extra space above and below bars
        ax.set_ylim(-0.5, n_crawls - 0.5)

        # Format x-axis (percentage)
        # Set x-axis to match the maximum value in the data (should be ~100% for stacked bars)
        max_value = lefts.max()
        ax.set_xlim(0, max_value * 1.02)  # Add 2% padding

        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))

        # Apply ggplot2-like styling
        ax.grid(True, which='major', linewidth=0.8, color='#E6E6E6', zorder=0, axis='x')
        ax.set_axisbelow(True)

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Set tick colors and font size
        ax.tick_params(axis='y', which='both', colors='#E6E6E6', length=20, width=1.5, labelsize=12)
        ax.tick_params(axis='x', which='both', colors='#E6E6E6', length=4, width=1.5, labelsize=12)
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')

        # Position legend at bottom with reversed order to match ggplot2
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='upper center',
                bbox_to_anchor=(0.5, -0.05), ncol=min(3, len(categories)),
                frameon=False, fontsize=14, title='')

        # Adjust layout and save
        plt.tight_layout(pad=0.5)
        plt.savefig(img_path, dpi=self.DEFAULT_DPI, bbox_inches='tight', facecolor='white', pad_inches=0.1)
        plt.close()

        return fig

        
    def plot_fetch_status(self, data, row_filter, img_file, ratio=1.0):
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
        # print(data)
        
        img_path = os.path.join(self.PLOTDIR, img_file)

        if self.PLOTLIB == "rpy2.ggplot2":
            return self.plot_fetch_status_with_rpy2_ggplot2(data=data, img_path=img_path, ratio=ratio)
    
        elif self.PLOTLIB == "matplotlib":
            return self.plot_fetch_status_with_matplotliob(data=data, categories=categories, img_path=img_path, ratio=ratio)
        else:
            raise ValueError("Invalid PLOTLIB")

    def plot_crawldb_status_with_rpy2_ggplot2(self, data, img_path, ratio):
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
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.ticker import AutoMinorLocator, MaxNLocator
        from matplotlib.ticker import FuncFormatter
        
        fig_width_px = 2100
        fig_height_px = 6000  # TODO this should be based on "ratio"
        # Calculate figsize in inches
        fig_width = fig_width_px / self.DEFAULT_DPI
        fig_height = fig_height_px / self.DEFAULT_DPI
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Get unique crawls and categories
        crawls = data['crawl'].unique()
        n_crawls = len(crawls)

        # Pastel1 palette colors
        # Standard ColorBrewer Pastel1 colors
        pastel1_colors = ['#FDDAEC', '#E5D8BD',  '#FFFFCC','#FED9A6', '#DECBE4',  '#CCEBC5',  '#B3CDE3',
            '#FBB4AE', '#F2F2F2']

        # Use categories hard-coded order of categories
        categories_ordered = ['unfetched', 'redir_temp', 'redir_perm', 'orphan', 'notmodified', 'gone', 'fetched', 'duplicate']

        # Prepare data for horizontal stacked bar chart
        bar_positions = np.arange(n_crawls)

        # Create stacked bars
        lefts = np.zeros(n_crawls)

        for i, category in enumerate(categories_ordered):
            category_data = data[data['type'] == category]
            values = []

            for crawl in crawls:
                crawl_data = category_data[category_data['crawl'] == crawl]
                if len(crawl_data) > 0:
                    values.append(crawl_data['size'].iloc[0])
                else:
                    values.append(0)

            # Use Pastel1 colors cycling through the palette
            color = pastel1_colors[i % len(pastel1_colors)]
            ax.barh(bar_positions, values, left=lefts, height=0.8,
                color=color, label=category)
            lefts += values

        # Set labels and title
        ax.set_title('CrawlDb Size and Status Counts', fontsize=16, fontweight='normal',
                    pad=10, loc='left')
        ax.set_xlabel('', fontsize=24)
        ax.set_ylabel('', fontsize=24)


        ax.xaxis.set_major_locator(MaxNLocator(nbins=3, prune=None, integer=False))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))  # 4 minor ticks between majors = gridlines every year

        # Format y-axis (crawl names)
        ax.set_yticks(bar_positions)
        ax.set_yticklabels(crawls, fontsize=12)
        # Remove extra space above and below bars
        ax.set_ylim(-0.5, n_crawls - 0.5)

        # Format x-axis (size counts)
        # Set x-axis to match the maximum value in the data
        max_value = lefts.max()
        ax.set_xlim(0, max_value * 1.02)  # Add 2% padding

        # Format with scientific notation if large numbers
        if max_value > 1e4:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))
        else:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))

        # Apply ggplot2-like styling
        ax.grid(True, which='both', linewidth=0.8, color='#E6E6E6', zorder=0, axis='x')
        ax.set_axisbelow(True)

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Set tick colors and font size
        ax.tick_params(axis='both', which='both', colors='#E6E6E6', length=8, width=0.8, labelsize=12)

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')

        # Position legend at bottom (no reversal since reverse=False)
        handles, labels_legend = ax.get_legend_handles_labels()
        ax.legend(handles, labels_legend, loc='upper center',
                bbox_to_anchor=(0.5, -0.05), ncol=min(4, len(categories_ordered)),
                frameon=False, fontsize=12, title='')

        # Adjust layout and save
        plt.tight_layout(pad=0.5)
        plt.savefig(img_path, dpi=self.DEFAULT_DPI, bbox_inches='tight', facecolor='white', pad_inches=0.1)
        plt.close()

        return fig

    def plot_crawldb_status(self, data, row_filter, img_file, ratio=1.0):
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
        print(data)

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
    plot.plot()
