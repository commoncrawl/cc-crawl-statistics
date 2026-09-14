import sys

import pandas

from crawlstats import MonthlyCrawl
from plot.table import TabularStats


class DomainStats(TabularStats):

    # top domains csv fetched by get_stats.sh
    MAX_TOP_DOMAINS = 1000
    TOP_DOMAINS_FILE = 'stats/top-domains/{}.domains-top-{}.csv'

    def __init__(self, crawl):
        super().__init__()
        self.crawl = crawl

    def read_data(self):
        """Read the downloaded top domains csv."""
        path = self.TOP_DOMAINS_FILE.format(self.crawl, self.MAX_TOP_DOMAINS)
        self.type_stats = pandas.read_csv(path)

    def plot(self, name):
        data = self.type_stats
        css_classes = ['tablesorter', 'tablesearcher']
        data = data.set_index('domain')
        data.columns.name = 'domain'
        data.index.name = None
        print(data.to_html('{}/{}-top-{}.html'.format(
                            self.PLOTDIR, name, self.MAX_TOP_DOMAINS),
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
    plot.read_data()
    plot.plot(plot_name)
