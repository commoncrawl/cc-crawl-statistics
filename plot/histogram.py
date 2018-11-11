import os.path
import pandas
import sys

from collections import defaultdict

from crawlstats import CST

from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri

from crawlplot import CrawlPlot, PLOTDIR, GGPLOT2_THEME

pandas2ri.activate()


class CrawlHistogram(CrawlPlot):

    PSEUDO_LOG_BINS = [0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000,
                       10000, 20000, 50000, 100000, 200000, 500000, 1000000,
                       2*10**6, 5*10**6, 10**7, 2*10**7, 5*10**7, 10**8,
                       2*10**8, 5*10**8, 10**9]
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
        img_path = os.path.join(PLOTDIR, 'crawler/histogr_url_dupl.png')
        p.save(img_path)
        # data.to_csv(img_path + '.csv')
        return p

    def plot_host_domain_tld(self):
        # -- pages/URLs per host / domain / tld
        data = self.histogr
        data = data[data['type'].isin(['host', 'domain', 'tld'])]
        data = data[data['type_counted'].isin(['url'])]
        img_path = os.path.join(PLOTDIR,
                                'crawler/histogr_host_domain_tld.png')
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

    def plot_domain_cumul(self, crawl):
        # -- coverage (cumulative pages) per domain
        data = self.histogr
        data = data[data['type'].isin(['domain'])]
        data = data[data['crawl'] == crawl]
        data = data[data['type_counted'].isin(['url'])]
        data['urls'] = data['count']*data['frequency']
        print(data)
        data = data[['urls', 'count', 'frequency']]
        data = data.sort_values(['count'], ascending=0)
        data['cum_domains'] = data['frequency'].cumsum()
        data['cum_urls'] = data['urls'].cumsum()
        data_perc = data.apply(lambda x: round(100.0*x/float(x.sum()), 1))
        data['%domains'] = data_perc['frequency']
        data['%urls'] = data_perc['urls']
        data['%cum_domains'] = data['cum_domains'].apply(
            lambda x: round(100.0*x/float(data['frequency'].sum()), 1))
        data['%cum_urls'] = data['cum_urls'].apply(
            lambda x: round(100.0*x/float(data['urls'].sum()), 1))
        with pandas.option_context('display.max_rows', None,
                                   'display.max_columns', None,
                                   'display.width', 200):
            print(data)
        img_path = os.path.join(PLOTDIR,
                                'crawler/histogr_domain_cumul.png')
        # data.to_csv(img_path + '.csv')
        title = 'Cumulative URLs for Top Domains'
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='cum_domains', y='cum_urls') \
            + ggplot2.geom_line() + ggplot2.geom_point() \
            + GGPLOT2_THEME \
            + ggplot2.labs(title=title, x='domains cumulative',
                           y='URLs cumulative') \
            + ggplot2.scale_y_log10() \
            + ggplot2.scale_x_log10()
        p.save(img_path)
        return p


if __name__ == '__main__':
    latest_crawl = sys.argv[-1]
    plot = CrawlHistogram()
    plot.read_data(sys.stdin)
    plot.transform_data()
    plot.save_data()
    plot.plot_dupl_url()
    plot.plot_host_domain_tld()
    plot.plot_domain_cumul(latest_crawl)
