import sys

from collections import defaultdict

import pandas

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, MonthlyCrawl, MultiCount
from top_level_domain import TopLevelDomain


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
        crawl_has_host_domain_counts = {}
        for tld in self.tlds:
            tld_repr = tld
            tld_obj = None
            if tld in ('', '(ip address)'):
                continue
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
                else:
                    self.tld_stats['type'][self.N] = ''
                    self.tld_stats['subtype'][self.N] = ''
                    self.tld_stats['toptld'][self.N] = ''
                value = self.tlds[tld][crawl]
                n_pages = MultiCount.get_count(0, value)
                self.tld_stats['pages'][self.N] = n_pages
                n_urls = MultiCount.get_count(1, value)
                self.tld_stats['urls'][self.N] = n_urls
                n_hosts = MultiCount.get_count(2, value)
                self.tld_stats['hosts'][self.N] = n_hosts
                n_domains = MultiCount.get_count(3, value)
                self.tld_stats['domains'][self.N] = n_domains
                if n_urls != n_hosts:
                    # multi counts including host counts are not (yet)
                    # available for all crawls
                    crawl_has_host_domain_counts[crawl] = True
                elif crawl not in crawl_has_host_domain_counts:
                    crawl_has_host_domain_counts[crawl] = False
                self.N += 1
        for crawl in crawl_has_host_domain_counts:
            if not crawl_has_host_domain_counts[crawl]:
                print('No host and domain counts for', crawl)
                for n in self.tld_stats['crawl']:
                    if self.tld_stats['crawl'][n] == crawl:
                        del(self.tld_stats['hosts'][n])
                        del(self.tld_stats['domains'][n])
        self.tld_stats = pandas.DataFrame(self.tld_stats)

    def save_data(self):
        self.tld_stats.to_csv('data/tlds.csv')

    def plot(self, crawls):
        field_percentage_formatter = '{0:,.2f}'.format
        field_formatters = {'%urls': field_percentage_formatter,
                            '%hosts': field_percentage_formatter,
                            '%domains': field_percentage_formatter}
        data = self.tld_stats
        data = data[data['crawl'].isin(crawls)]
        crawl_data = data
        top_tlds = []
        # stats per crawl
        for crawl in crawls:
            print("\n-----\n{}\n".format(crawl))
            for aggr_type in ('type', 'toptld'):
                data = crawl_data
                data = data[data['crawl'].isin([crawl])]
                data = data.set_index([aggr_type], drop=False)
                data = data.sum(level=aggr_type).sort_values(
                    by=['urls'], ascending=False)
                for count in ('urls', 'hosts', 'domains'):
                    data['%'+count] = 100.0 * data[count] / data[count].sum()
                if aggr_type == 'toptld':
                    # skip less frequent TLDs
                    data = data[data['%urls'] >= .1]
                    for tld in data.index.values:
                        top_tlds.append(tld)
                print(data.to_string(formatters=field_formatters))
                print()
        # stats comparison for selected crawls
        for aggr_type in ('type', 'toptld'):
            data = crawl_data
            if aggr_type == 'toptld':
                data = data[data['toptld'].isin(top_tlds)]
            data = data[['crawl', aggr_type, 'urls']]
            data = data.groupby(['crawl', aggr_type]).agg({'urls': 'sum'})
            data = data.groupby(level=0).apply(lambda x: 100.0*x/float(x.sum()))
            # print("\n-----\n")
            # print(data.to_string(formatters={'urls': field_percentage_formatter}))
            data = data.reset_index().pivot(index=aggr_type,
                                            columns='crawl', values='urls')
            print("\n-----\n")
            print(data.to_string(formatters={c: field_percentage_formatter
                                             for c in crawls}))

        # save as HTML table
        data = crawl_data
        data = data[['crawl', aggr_type, 'urls']]
        data = data.groupby(['crawl', aggr_type]).agg({'urls': 'sum'})
        data = data.groupby(level=0).apply(lambda x: 100.0*x/float(x.sum()))
        data = data.reset_index().pivot(index=aggr_type,
                                        columns='crawl', values='urls')
        print(data.to_html('{}/tld-last-n-crawls.html'.format(
                            PLOTDIR, len(crawls)),
                           formatters={c: '{0:,.4f}'.format
                                       for c in crawls},
                           classes=['tablesorter']))


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    if len(plot_crawls) == 0:
        print(sys.argv[0], 'crawl-id...')
        print()
        print('Distribution of top-level domains for monthly crawls')
        print()
        print('Example:')
        print('', sys.argv[0], 'CC-MAIN-2014-52', 'CC-MAIN-2016-50')
        sys.exit(1)
    plot = TldStats()
    plot.read_data(sys.stdin)
    plot.transform_data()
    plot.save_data()
    plot.plot(plot_crawls)
