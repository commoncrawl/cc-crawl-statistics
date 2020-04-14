import os
import re
import sys

import pandas

from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri

from crawlplot import PLOTDIR, GGPLOT2_THEME

from crawlstats import CST
from crawl_size import CrawlSizePlot

pandas2ri.activate()


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
                    if self.crawls[crawl] in self.size[item_type]:
                        count = self.size[item_type][self.crawls[crawl]]
                        _N = self.type_index[item_type][self.crawls[crawl]]
                        self.size_by_type['percentage'][_N] = 100.0*count/total
                    else:
                        pass

    @staticmethod
    def row2title(row):
        row = re.sub('(?<=^fetch)er(?::aggr)?|^generator:', '', row)
        row = re.sub('[:_]', ' ', row)
        if row == 'page':
            row = 'pages released'
        return row

    def plot(self):
        # -- line plot
        row_types = ['generator:crawldb_size', 'generator:fetch_list',
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
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl', y='percentage', fill='type') \
            + ggplot2.geom_bar(stat='identity', position='stack', width=.9) \
            + ggplot2.coord_flip() \
            + ggplot2.scale_fill_brewer(palette='RdYlGn', type='sequential',
                                        guide=ggplot2.guide_legend(reverse=True)) \
            + GGPLOT2_THEME \
            + ggplot2.theme(**{'legend.position': 'bottom',
                               'aspect.ratio': ratio}) \
            + ggplot2.labs(title='Percentage of Fetch Status',
                           x='', y='', fill='')
        img_path = os.path.join(PLOTDIR, img_file)
        p.save(img_path, height = int(7 * ratio), width = 7)
        return p

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
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl', y='size', fill='type') \
            + ggplot2.geom_bar(stat='identity', position='stack', width=.9) \
            + ggplot2.coord_flip() \
            + ggplot2.scale_fill_brewer(palette='Pastel1', type='sequential',
                                        guide=ggplot2.guide_legend(reverse=False)) \
            + GGPLOT2_THEME \
            + ggplot2.theme(**{'legend.position': 'bottom',
                               'aspect.ratio': ratio}) \
            + ggplot2.labs(title='CrawlDb Size and Status Counts\n(before crawling)',
                           x='', y='', fill='')
        img_path = os.path.join(PLOTDIR, img_file)
        p.save(img_path, height = int(7 * ratio), width = 7)
        return p


if __name__ == '__main__':
    plot = CrawlerMetrics()
    plot.read_data(sys.stdin)
    plot.add_percent()
    plot.transform_data()
    plot.save_data()
    plot.plot()
