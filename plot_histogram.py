import os.path
import pandas
import sys

from collections import defaultdict

from crawlstats import CST

from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri

from crawlplot import CrawlPlot, PLOTDIR

pandas2ri.activate()


class CrawlHistogram(CrawlPlot):

    PSEUDO_LOG_BINS = [0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000,
                       10000, 20000, 50000, 100000, 200000, 500000, 1000000,
                       2*10**6, 5*10**6, 10**7, 2*10**7, 5*10**7, 10**8]
    # PSEUDO_LOG_BINS = numpy.logspace(0.0, 6.0, 19)

    def __init__(self):
        self.histogr = defaultdict(dict)
        self.N = 0

    def add(self, key, frequency):
        cst = CST[key[0]]
        if cst != CST.histogram:
            return
        item_type = key[1]
        if item_type == 'surt_domain':
            return
        crawl = key[2]
        type_counted = key[3]
        count = key[4]
        self.histogr['crawl'][self.N] = crawl
        self.histogr['type'][self.N] = item_type
        self.histogr['type_counted'][self.N] = type_counted
        self.histogr['count'][self.N] = count
        self.histogr['frequency'][self.N] = frequency
        self.N += 1

    def transform_data(self):
        self.histogr = pandas.DataFrame(self.histogr)

    def save_data(self):
        self.histogr.to_csv('data/crawlhistogr.csv')

    def plot_dupl_url(self):
        # -- pages per URL (URL-level duplicates)
        row_filter = ['url']
        data = self.histogr
        data = data[data['type'].isin(row_filter)]
        title = 'Pages per URL (URL-level duplicates)'
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='count', y='frequency') \
            + ggplot2.geom_jitter() \
            + ggplot2.facet_wrap('crawl', ncol=5) \
            + ggplot2.labs(title=title, x='(duplicate) pages per URL',
                           y='log(frequency)') \
            + ggplot2.scale_y_log10()
        # + ggplot2.scale_x_log10()  # could use log-log scale
        img_path = os.path.join(PLOTDIR, 'histogr_url_dupl.png')
        p.save(img_path)
        # data.to_csv(img_path + '.csv')
        return p

    def plot_host_domain_tld(self):
        # -- pages/URLs per host / domain / tld
        data = self.histogr
        data = data[data['type'].isin(['host', 'domain', 'tld'])]
        data = data[data['type_counted'].isin(['url'])]
        img_path = os.path.join(PLOTDIR,
                                'histogr_host_domain_tld.png')
        # data.to_csv(img_path + '.csv')
        title = 'URLs per Host / Domain / TLD'
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='count', weight='frequency', color='type') \
            + ggplot2.geom_freqpoly(bins=20) \
            + ggplot2.facet_wrap('crawl', ncol=4) \
            + ggplot2.labs(title='', x=title,
                           y='Frequency') \
            + ggplot2.scale_y_log10() \
            + ggplot2.scale_x_log10()
        p.save(img_path)
        return p


if __name__ == '__main__':
    plot = CrawlHistogram()
    plot.read_data(sys.stdin)
    plot.transform_data()
    plot.save_data()
    plot.plot_dupl_url()
    plot.plot_host_domain_tld()
