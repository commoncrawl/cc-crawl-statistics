import sys

import pandas

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, MonthlyCrawl, MultiCount
from plot.table import TabularStats


class DomainStats(TabularStats):

    # defined via crawlstats command-line option --max-top-hosts-domains
    MAX_TOP_DOMAINS = 500

    def __init__(self, crawl):
        super().__init__()
        self.crawl = crawl
        self.N = 0

    def add(self, key, val):
        cst = CST[key[0]]
        if cst not in (CST.size, CST.domain):
            return
        typeval = key[1]
        crawl = key[2]
        if crawl != self.crawl:
            return
        if cst == CST.size:
            self.size[typeval] = val
            return
        self.type_stats['domain'][self.N] = typeval 
        self.type_stats['pages'][self.N] = MultiCount.get_count(0, val)
        self.type_stats['urls'][self.N] = MultiCount.get_count(1, val)
        self.type_stats['hosts'][self.N] = MultiCount.get_count(2, val)
        # self.type_stats['crawl'][self.N] = crawl
        self.N += 1

    def transform_data(self):
        data = pandas.DataFrame(self.type_stats)
        for cnt in ['pages', 'urls']:
            total = self.size[cnt[:-1]]
            data['%' + cnt] = 100.0 * data[cnt] / total
        data.sort_values(ascending=False, inplace=True, by='pages')
        print(data)
        self.type_stats = data

    def save_data(self, name, dir_name='data/'):
        self.type_stats.to_csv('{}/{}-top-{}.csv'.format(PLOTDIR, name, self.MAX_TOP_DOMAINS),
                               float_format='%.6f', index=None)

    def plot(self, name):
        data = self.type_stats
        css_classes = ['tablesorter', 'tablesearcher']
        data = data.set_index('domain')
        data.columns.name = 'domain'
        data.index.name = None
        print(data.to_html('{}/{}-top-{}.html'.format(
                            PLOTDIR, name, self.MAX_TOP_DOMAINS),
                           float_format='%.6f',
                           classes=css_classes, index='domain'))

if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    if len(plot_crawls) == 0:
        plot_crawls = MonthlyCrawl.get_latest(1)
        print(plot_crawls)
    latest_crawl = plot_crawls[-1]
    plot_name = 'domains'
    plot = DomainStats(latest_crawl)
    plot.read_from_stdin_or_file()
    plot.transform_data()
    plot.save_data(plot_name, dir_name=PLOTDIR)
    plot.plot(plot_name)
