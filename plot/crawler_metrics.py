import os
import re
import sys

from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri

from crawlplot import PLOTDIR, GGPLOT2_THEME

from crawlstats import CST
from crawl_size import CrawlSizePlot

pandas2ri.activate()


class CrawlerMetrics(CrawlSizePlot):

    metrics_map = {
        'fetcher:redirect': ('fetcher:temp_moved', 'fetcher:moved'),
        'fetcher:denied':   ('fetcher:access_denied', 'fetcher:robots_denied',
                             'fetcher:robots_denied_maxcrawldelay',
                             'fetcher:filter_denied'),
        'fetcher:failed':   ('fetcher:gone', 'fetcher:notfound',
                             'fetcher:exception'),
        'fetcher:skipped':  ('fetcher:hitByThrougputThreshold',
                             'fetcher:hitByTimeLimit',
                             'fetcher:AboveExceptionThresholdInQueue')
    }

    def add(self, key, val):
        cst = CST[key[0]]
        item_type = key[1]
        if not (cst == CST.crawl_status or
                (cst == CST.size and item_type in ('page', 'url'))):
            return
        crawl = key[2]
        self.add_by_type(crawl, item_type, val)
        for metric in self.metrics_map:
            if item_type in self.metrics_map[metric]:
                self.add_by_type(crawl, metric, val)

    def save_data(self):
        self.size.to_csv('data/crawlmetrics.csv')
        self.size_by_type.to_csv('data/crawlmetricsbytype.csv')

    def add_percent(self):
        for crawl in self.crawls:
            total = self.size['fetcher:total'][self.crawls[crawl]]
            for item_type in self.type_index:
                if item_type.startswith('fetcher:') and \
                        item_type != 'fetcher:total':
                    count = self.size[item_type][self.crawls[crawl]]
                    _N = self.type_index[item_type][self.crawls[crawl]]
                    self.size_by_type['percentage'][_N] = 100.0*count/total

    @staticmethod
    def row2title(row):
        row = re.sub('(?<=^fetch)er|^generator:', '', row)
        row = re.sub('[:_]', ' ', row)
        if row == 'page':
            row = 'pages released'
        return row

    def plot(self):
        # -- line plot
        row_types = ['generator:crawldb_size', 'generator:fetch_list',
                     'fetcher:success', 'fetcher:total', 'fetcher:redirect',
                     'fetcher:failed', 'fetcher:denied', 'fetcher:skipped',
                     'page']
        self.size_plot(self.size_by_type, row_types, CrawlerMetrics.row2title,
                       'Crawler Metrics', 'Pages',
                       'crawler/metrics.png')
        # -- stacked bar plot
        row_types = ['fetcher:success', 'fetcher:redirect',
                     'fetcher:failed', 'fetcher:denied', 'fetcher:skipped']
        ratio = 0.1 + self.ncrawls * .05
        self.plot_stacked_bar(self.size_by_type, row_types,
                              'crawler/fetch_status_percentage.png', ratio=ratio)

    def plot_stacked_bar(self, data, row_filter, img_file, ratio=1.0):
        if len(row_filter) > 0:
            data = data[data['type'].isin(row_filter)]
        for value in row_filter:
            if re.search('^fetcher:', value):
                replacement = re.sub('^fetcher:', '', value)
                data.replace(to_replace=value, value=replacement, inplace=True)
        # print(data)
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl', y='percentage', fill='type') \
            + ggplot2.geom_bar(stat='identity', position='stack', width=.9) \
            + ggplot2.coord_flip() \
            + ggplot2.scale_fill_brewer(palette='RdYlGn', type='sequential',
                                        guide=ggplot2.guide_legend(reverse=True)) \
            + GGPLOT2_THEME \
            + ggplot2.theme(**{'legend.position': 'bottom',
                               'aspect.ratio': ratio}) \
            + ggplot2.labs(title='Percentage of Fetch Status', x='', y='', fill='')
        img_path = os.path.join(PLOTDIR, img_file)
        p.save(img_path)
        return p


if __name__ == '__main__':
    plot = CrawlerMetrics()
    plot.read_data(sys.stdin)
    plot.add_percent()
    plot.transform_data()
    plot.save_data()
    plot.plot()
