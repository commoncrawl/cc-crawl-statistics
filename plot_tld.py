import sys

from collections import defaultdict

import pandas

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, MonthlyCrawl, MultiCount
from tld import TopLevelDomain


class TldStats(CrawlPlot):

    def __init__(self):
        self.tlds = defaultdict(dict)
        self.tld_stats = defaultdict(dict)
        self.N = 0

    def add(self, key, val):
        cst = CST[key[0]]
        if cst != CST.tld:
            return
        tld = key[1]
        crawl = key[2]
        self.tlds[tld][crawl] = val

    def transform_data(self):
        for tld in self.tlds:
            tld_repr = tld
            tld_obj = None
            if tld in ('', '(ip address)'):
                pass
            else:
                try:
                    tld_obj = TopLevelDomain(tld)
                    tld_repr = tld_obj.tld
                except:
                    print('error', tld)
                    continue
            for crawl in self.tlds[tld]:
                self.tld_stats['tld'][self.N] = tld_repr
                self.tld_stats['crawl'][self.N] = crawl
                if tld_obj:
                    self.tld_stats['type'][self.N] = tld_obj.tld_type
                    self.tld_stats['subtype'][self.N] = tld_obj.sub_type
                    self.tld_stats['toptld'][self.N] = tld_obj.first_level
                value = self.tlds[tld][crawl]
                self.tld_stats['pages'][self.N] = MultiCount.get_count(0, value)
                self.tld_stats['urls'][self.N] = MultiCount.get_count(1, value)
                # TODO: counts for domains and hosts
                self.N += 1
        self.tld_stats = pandas.DataFrame(self.tld_stats)

    def save_data(self):
        self.tld_stats.to_csv('data/tlds.csv')

    def plot(self):
        for crawl in ['CC-MAIN-2014-52', 'CC-MAIN-2016-40']:
            data = self.tld_stats
            data = data[data['crawl'].isin([crawl])]
            data['%_of_urls'] = 100.0 * data['urls'] / data['urls'].sum()
            data = data.set_index(['type', 'subtype', 'toptld'], drop=False)
            data = data.sum(level='type')
            print("\n-----\n", crawl)
            print(data)


if __name__ == '__main__':
    plot = TldStats()
    plot.read_data(sys.stdin)
    plot.transform_data()
    plot.save_data()
    plot.plot()
