import sys

import pandas

from crawlstats import CST, MonthlyCrawl
from plot.table import TabularStats


class DomainStats(TabularStats):

    # extended top domains csv fetched by get_stats.sh
    MAX_TOP_DOMAINS = 1000
    TOP_DOMAINS_FILE = 'stats/top-domains/{}.domains-top-{}-extended.csv.gz'

    def __init__(self, crawl):
        super().__init__()
        self.crawl = crawl

    def add(self, key, val):
        """Collect the crawl size records read from stdin."""
        cst = CST[key[0]]
        if cst != CST.size:
            return
        if key[2] != self.crawl:
            return
        self.size[key[1]] = val

    def read_top_domains(self):
        """Read the downloaded top domains csv, handles gzipped or plain versions."""
        path = self.TOP_DOMAINS_FILE.format(self.crawl, self.MAX_TOP_DOMAINS)
        with open(path, 'rb') as instream:
            gzipped = instream.read(2) == b'\x1f\x8b'
        self.type_stats = pandas.read_csv(path, compression='gzip' if gzipped else None)

    def transform_data(self):
        """Add the percentage columns, counts are crawl totals."""
        data = self.type_stats
        for cnt in ['pages', 'urls']:
            total = self.size[cnt[:-1]]
            data['%' + cnt] = 100.0 * data[cnt] / total
        self.type_stats = data

    def save_data(self, name):
        """Write the top domains csv next to the html table."""
        self.type_stats.to_csv('{}/{}-top-{}.csv'.format(
                                self.PLOTDIR, name, self.MAX_TOP_DOMAINS),
                               float_format='%.6f', index=None)

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
    plot.read_from_stdin_or_file()
    plot.read_top_domains()
    plot.transform_data()
    plot.save_data(plot_name)
    plot.plot(plot_name)
