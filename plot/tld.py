import sys

from collections import defaultdict

import pandas

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, MonthlyCrawl, MultiCount
from top_level_domain import TopLevelDomain
from stats.tld_alexa_top_1m import alexa_top_1m_tlds
from stats.tld_cisco_umbrella_top_1m import cisco_umbrella_top_1m_tlds
from stats.tld_majestic_top_1m import majestic_top_1m_tlds

# min. share of URLs for a TLD to be shown in metrics
min_urls_percentage = .05

field_percentage_formatter = '{0:,.2f}'.format


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
                self.tld_stats['suffix'][self.N] = tld_repr
                self.tld_stats['crawl'][self.N] = crawl
                date = pandas.Timestamp(MonthlyCrawl.date_of(crawl))
                self.tld_stats['date'][self.N] = date
                if tld_obj:
                    self.tld_stats['type'][self.N] \
                        = TopLevelDomain.short_type(tld_obj.tld_type)
                    self.tld_stats['subtype'][self.N] = tld_obj.sub_type
                    self.tld_stats['tld'][self.N] = tld_obj.first_level
                else:
                    self.tld_stats['type'][self.N] = ''
                    self.tld_stats['subtype'][self.N] = ''
                    self.tld_stats['tld'][self.N] = ''
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

    def percent_agg(self, data, columns, index, values, aggregate):
        data = data[[columns, index, values]]
        data = data.groupby([columns, index]).agg(aggregate)
        data = data.groupby(level=0).apply(lambda x: 100.0*x/float(x.sum()))
        # print("\n-----\n")
        # print(data.to_string(formatters={'urls': field_percentage_formatter}))
        return data

    def pivot_percentage(self, data, columns, index, values, aggregate):
        data = self.percent_agg(data, columns, index, values, aggregate)
        return data.reset_index().pivot(index=index,
                                        columns=columns, values=values)

    def plot_groups(self):
        title = 'Groups of Top-Level Domains'
        ylabel = 'URLs %'
        clabel = ''
        img_file = 'tld/groups.png'
        data = self.pivot_percentage(self.tld_stats, 'crawl', 'type',
                                     'urls', {'urls': 'sum'})
        data = data.transpose()
        print("\n-----\n")
        types = set(self.tld_stats['type'].tolist())
        formatters = {c: field_percentage_formatter for c in types}
        print(data.to_string(formatters=formatters))
        data.to_html('{}/tld/groups-percentage.html'.format(PLOTDIR),
                     formatters=formatters,
                     classes=['tablesorter', 'tablepercentage'])
        data = self.percent_agg(self.tld_stats, 'date', 'type',
                                'urls', {'urls': 'sum'}).reset_index()
        return self.line_plot(data, title, ylabel, img_file,
                              x='date', y='urls', c='type', clabel=clabel)

    def plot(self, crawls, latest_crawl):
        field_formatters = {c: '{:,.0f}'.format
                            for c in ['pages', 'urls', 'hosts', 'domains']}
        for c in ['%urls', '%hosts', '%domains']:
            field_formatters[c] = field_percentage_formatter
        data = self.tld_stats
        data = data[data['crawl'].isin(crawls)]
        crawl_data = data
        top_tlds = []
        # stats per crawl
        for crawl in crawls:
            print("\n-----\n{}\n".format(crawl))
            for aggr_type in ('type', 'tld'):
                data = crawl_data
                data = data[data['crawl'].isin([crawl])]
                data = data.set_index([aggr_type], drop=False)
                data = data.sum(level=aggr_type).sort_values(
                    by=['urls'], ascending=False)
                for count in ('urls', 'hosts', 'domains'):
                    data['%'+count] = 100.0 * data[count] / data[count].sum()
                if aggr_type == 'tld':
                    # skip less frequent TLDs
                    data = data[data['%urls'] >= min_urls_percentage]
                    for tld in data.index.values:
                        top_tlds.append(tld)
                print(data.to_string(formatters=field_formatters))
                print()
                if crawl == latest_crawl:
                    # latest crawl by convention
                    type_name = aggr_type
                    if aggr_type == 'type':
                        type_name = 'group'
                    path = '{}/tld/latest-crawl-{}s.html'.format(
                        PLOTDIR, type_name)
                    data.to_html(path,
                                 formatters=field_formatters,
                                 classes=['tablesorter'])
        # stats comparison for selected crawls
        for aggr_type in ('type', 'tld'):
            data = crawl_data
            if aggr_type == 'tld':
                data = data[data['tld'].isin(top_tlds)]
            data = self.pivot_percentage(data, 'crawl', aggr_type,
                                         'urls', {'urls': 'sum'})
            print("\n----- {}\n".format(aggr_type))
            print(data.to_string(formatters={c: field_percentage_formatter
                                             for c in crawls}))
            if aggr_type == 'tld':
                # save as HTML table
                path = '{}/tld/selected-crawls-percentage.html'.format(
                                    PLOTDIR, len(crawls))
                data.to_html(path,
                             formatters={c: '{0:,.4f}'.format
                                         for c in crawls},
                             classes=['tablesorter', 'tablepercentage'])

    def plot_comparison(self, crawl, name, topNlimit=None, method='spearman'):
        print()
        print('Comparison for', crawl, '-', name, '-', method)
        data = self.tld_stats
        data = data[data['crawl'].isin([crawl])]
        data = data[data['urls'] >= topNlimit]
        data = data.set_index(['tld'], drop=False)
        data = data.sum(level='tld')
        print(data)
        data['alexa'] = pandas.Series(alexa_top_1m_tlds)
        data['cisco'] = pandas.Series(cisco_umbrella_top_1m_tlds)
        data['majestic'] = pandas.Series(majestic_top_1m_tlds)
        fields = ('pages', 'urls', 'hosts', 'domains',
                  'alexa', 'cisco', 'majestic')
        formatters = {c: '{0:,.3f}'.format for c in fields}
        # relative frequency (percent)
        for count in fields:
            data[count] = 100.0 * data[count] / data[count].sum()
        # Spearman's rank correlation for all TLDs
        corr = data.corr(method=method, min_periods=1)
        print(corr.to_string(formatters=formatters))
        corr.to_html('{}/tld/{}-comparison-{}-all-tlds.html'
                     .format(PLOTDIR, name, method),
                     formatters=formatters,
                     classes=['matrix'])
        if topNlimit is None:
            return
        # Spearman's rank correlation for TLDs covering
        # at least topNlimit % of urls
        data = data[data['urls'] >= topNlimit]
        print()
        print('Top', len(data), 'TLDs (>= ', topNlimit, '%)')
        print(data)
        data.to_html('{}/tld/{}-comparison.html'.format(PLOTDIR, name),
                     formatters=formatters,
                     classes=['tablesorter', 'tablepercentage'])
        print()
        corr = data.corr(method=method, min_periods=1)
        print(corr.to_string(formatters=formatters))
        corr.to_html('{}/tld/{}-comparison-{}-frequent-tlds.html'
                     .format(PLOTDIR, name, method),
                     formatters=formatters,
                     classes=['matrix'])
        print()

    def plot_comparison_groups(self):
        # Alexa and Cisco types/groups:
        for (name, data) in [('Alexa', alexa_top_1m_tlds),
                             ('Cisco', cisco_umbrella_top_1m_tlds),
                             ('Majestic', majestic_top_1m_tlds)]:
            compare_types = defaultdict(int)
            for tld in data:
                compare_types[TopLevelDomain(tld).tld_type] += data[tld]
            print(name, 'TLD groups:')
            for tld in compare_types:
                c = compare_types[tld]
                print(' {:6d}\t{:4.1f}\t{}'.format(c, (100.0*c/1000000), tld))
            print()


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    latest_crawl = plot_crawls[-1]
    if len(plot_crawls) == 0:
        print(sys.argv[0], 'crawl-id...')
        print()
        print('Distribution of top-level domains for (selected) monthly crawls')
        print()
        print('Example:')
        print('', sys.argv[0], '[options]', 'CC-MAIN-2014-52', 'CC-MAIN-2016-50')
        print()
        print('Last argument is considered to be the latest crawl')
        print()
        print('Options:')
        print()
        sys.exit(1)
    plot = TldStats()
    plot.read_data(sys.stdin)
    plot.transform_data()
    plot.save_data()
    plot.plot_groups()
    plot.plot(plot_crawls, latest_crawl)
    if latest_crawl == 'CC-MAIN-2018-22':
        # plot comparison only for crawl of similar date as benchmark data
        plot.plot_comparison(latest_crawl, 'selected-crawl',
                             min_urls_percentage)
#         plot.plot_comparison(latest_crawl, 'selected-crawl',
#                              min_urls_percentage, 'pearson')
    plot.plot_comparison_groups()
