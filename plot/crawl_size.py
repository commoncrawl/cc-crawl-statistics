import os
import pandas
import re
import sys
import types

from collections import defaultdict
from hyperloglog import HyperLogLog

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, CrawlStatsJSONDecoder, HYPERLOGLOG_ERROR,\
    MonthlyCrawl


class CrawlSizePlot(CrawlPlot):

    def __init__(self):
        self.size = defaultdict(dict)
        self.size_by_type = defaultdict(dict)
        self.type_index = defaultdict(dict)
        self.crawls = {}
        self.ncrawls = 0
        self.hll = defaultdict(dict)
        self.N = 0
        self.sum_counts = False

    def add(self, key, val):
        cst = CST[key[0]]
        if cst not in (CST.size, CST.size_estimate):
            return
        item_type = key[1]
        crawl = key[2]
        count = 0
        if cst == CST.size_estimate:
            item_type = ' '.join([item_type, 'estim.'])
            hll = CrawlStatsJSONDecoder.json_decode_hyperloglog(val)
            count = len(hll)
            self.hll[item_type][crawl] = hll
        elif cst == CST.size:
            count = val
        self.add_by_type(crawl, item_type, count)

    def add_by_type(self, crawl, item_type, count):
        if crawl not in self.crawls:
            self.crawls[crawl] = self.ncrawls
            self.size['crawl'][self.ncrawls] = crawl
            date = pandas.Timestamp(MonthlyCrawl.date_of(crawl))
            self.size['date'][self.ncrawls] = date
            self.ncrawls += 1
        else:
            date = self.size['date'][self.crawls[crawl]]
        if item_type in self.size and \
                self.crawls[crawl] in self.size[item_type]:
            # add count to existing record?
            if self.sum_counts:
                count += self.size[item_type][self.crawls[crawl]]
                self.size[item_type][self.crawls[crawl]] = count
                _N = self.type_index[item_type][self.crawls[crawl]]
                self.size_by_type['size'][_N] = count
            return
        self.size[item_type][self.crawls[crawl]] = count
        self.size_by_type['crawl'][self.N] = crawl
        self.size_by_type['date'][self.N] = date
        self.size_by_type['type'][self.N] = item_type
        self.size_by_type['size'][self.N] = count
        self.type_index[item_type][self.crawls[crawl]] = self.N
        self.N += 1

    def cumulative_size(self):
        latest_n_crawls_cumul = [2, 3, 4, 6, 9, 12]
        total_pages = 0
        sorted_crawls = sorted(self.crawls)
        for crawl in sorted_crawls:
            total_pages += self.size['page'][self.crawls[crawl]]
            self.add_by_type(crawl, 'page cumul.', total_pages)
        urls_cumul = defaultdict(dict)
        for item_type in self.hll.keys():
            item_type_cumul = ' '.join([item_type, 'cumul.'])
            item_type_new = ' '.join([item_type, 'new'])
            cumul_hll = HyperLogLog(HYPERLOGLOG_ERROR)
            n = 0
            hlls = []
            for crawl in sorted(self.hll[item_type]):
                n += 1
                hll = self.hll[item_type][crawl]
                last_cumul_hll_len = len(cumul_hll)
                cumul_hll.update(hll)
                # cumulative size
                self.add_by_type(crawl, item_type_cumul, len(cumul_hll))
                # new unseen items this crawl (since the first analyzed crawl)
                unseen = (len(cumul_hll) - last_cumul_hll_len)
                if unseen > len(hll):
                    # 1% error rate for cumulative HLLs is large in comparison
                    # to crawl size, adjust to size of items in this crawl
                    # (there can be no more new items than the size of the crawl)
                    unseen = len(hll)
                self.add_by_type(crawl, item_type_new, unseen)
                hlls.append(hll)
                # cumulative size for last N crawls
                for n_crawls in latest_n_crawls_cumul:
                    item_type_n_crawls = '{} cumul. last {} crawls'.format(
                        item_type, n_crawls)
                    if n_crawls <= len(hlls):
                        cum_hll = HyperLogLog(HYPERLOGLOG_ERROR)
                        for i in range(1, (n_crawls+1)):
                            if i > len(hlls):
                                break
                            cum_hll.update(hlls[-i])
                        size_last_n = len(cum_hll)
                        if item_type == 'url estim.':
                            urls_cumul[crawl][str(n_crawls)] = size_last_n
                    else:
                        size_last_n = 'nan'
                    self.add_by_type(crawl, item_type_n_crawls, size_last_n)
        for n, crawl in enumerate(sorted_crawls):
            for n_crawls in latest_n_crawls_cumul:
                if n_crawls > (n+1):
                    self.add_by_type(crawl,
                                     'page cumul. last {} crawls'.format(n_crawls),
                                     'nan')
                    continue
                cumul_pages = 0
                for c in sorted_crawls[(1+n-n_crawls):(n+1)]:
                    cumul_pages += self.size['page'][self.crawls[c]]
                self.add_by_type(crawl,
                                 'page cumul. last {} crawls'.format(n_crawls),
                                 cumul_pages)
                urls_cumul[crawl][str(n_crawls)] = urls_cumul[crawl][str(n_crawls)]/cumul_pages
        for crawl in urls_cumul:
            for n_crawls in urls_cumul[crawl]:
                self.add_by_type(crawl,
                                 'URLs/pages last {} crawls'.format(n_crawls),
                                 urls_cumul[crawl][n_crawls])

    def transform_data(self):
        self.size = pandas.DataFrame(self.size)
        self.size_by_type = pandas.DataFrame(self.size_by_type)

    def save_data(self):
        self.size.to_csv('data/crawlsize.csv')
        self.size_by_type.to_csv('data/crawlsizebytype.csv')

    def duplicate_ratio(self):
        # -- duplicate ratio
        data = self.size[['crawl', 'page', 'url', 'digest estim.']]
        data['1-(urls/pages)'] = 100 * (1.0 - (data['url'] / data['page']))
        data['1-(digests/pages)'] = \
            100 * (1.0 - (data['digest estim.'] / data['page']))
        floatf = '{0:.1f}%'.format
        print(data.to_string(formatters={'1-(urls/pages)': floatf,
                                         '1-(digests/pages)': floatf}),
              file=open('data/crawlduplicates.txt', 'w'))

    def plot(self):
        # -- size per crawl (pages, URL and content digest)
        row_types = ['page', 'url',  # 'url estim.',
                     'digest estim.']
        self.size_plot(self.size_by_type, row_types, '',
                       'Crawl Size', 'Pages / Unique Items',
                       'crawlsize/monthly.png',
                       data_export_csv='crawlsize/monthly.csv')
        # -- cumulative size
        row_types = ['page cumul.', 'url estim. cumul.',
                     'digest estim. cumul.']
        self.size_plot(self.size_by_type, row_types, ' cumul\.$',
                       'Crawl Size Cumulative',
                       'Pages / Unique Items Cumulative',
                       'crawlsize/cumulative.png')
        # -- new items per crawl
        row_types = ['page', 'url estim. new',
                     'digest estim. new']
        self.size_plot(self.size_by_type, row_types, ' new$',
                       'New Items per Crawl (not observed in prior crawls)',
                       'Pages / New Items', 'crawlsize/monthly_new.png',
                       data_export_csv='crawlsize/monthly_new.csv')
        # -- cumulative URLs over last N crawls (this and preceding N-1 crawls)
        row_types = ['url', '1 crawl',  # 'url' replaced by '1 crawl'
                     'url estim. cumul. last 2 crawls',
                     'url estim. cumul. last 3 crawls',
                     'url estim. cumul. last 4 crawls',
                     'url estim. cumul. last 6 crawls',
                     'url estim. cumul. last 9 crawls',
                     'url estim. cumul. last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='url', value='1 crawl', inplace=True)
        self.size_plot(data, row_types, '^url estim\. cumul\. last | crawls?$',
                       'URLs Cumulative Over Last N Crawls',
                       'Unique URLs cumulative',
                       'crawlsize/url_last_n_crawls.png',
                       clabel='n crawls',
                       data_export_csv='crawlsize/url_last_n_crawls.csv')
        # -- ratio unique URLs by total page captures over last N crawls (this and preceding N-1 crawls)
        row_types = ['URLs/pages last 2 crawls',
                     'URLs/pages last 3 crawls',
                     'URLs/pages last 4 crawls',
                     'URLs/pages last 6 crawls',
                     'URLs/pages last 9 crawls',
                     'URLs/pages last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='url', value='1 crawl', inplace=True)
        self.size_plot(data, row_types, '^URLs/pages last | crawls?$',
                       'Ratio Unique URLs / Total Pages Captured Over Last N Crawls',
                       'URLs/Pages',
                       'crawlsize/url_page_ratio_last_n_crawls.png',
                       clabel='n crawls',
                       data_export_csv='crawlsize/url_page_ratio_last_n_crawls.csv')
        # -- cumul. digests over last N crawls (this and preceding N-1 crawls)
        row_types = ['digest estim.', '1 crawl',  # 'url' replaced by '1 crawl'
                     'digest estim. cumul. last 2 crawls',
                     'digest estim. cumul. last 3 crawls',
                     'digest estim. cumul. last 6 crawls',
                     'digest estim. cumul. last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='digest estim.', value='1 crawl', inplace=True)
        self.size_plot(data, row_types,
                       '^digest estim\. cumul\. last | crawls?$',
                       'Content Digest Cumulative Over Last N Crawls',
                       'Unique content digests cumulative',
                       'crawlsize/digest_last_n_crawls.png',
                       clabel='n crawls')
        # -- URLs, hosts, domains, tlds (normalized)
        data = self.size_by_type
        row_types = ['url', 'tld', 'domain', 'host']
        data = data[data['type'].isin(row_types)]
        self.export_csv(data, 'crawlsize/domain.csv')
        size_norm = data['size'] / 1000.0
        data['size'] = size_norm.where(data['type'] == 'tld',
                                       other=data['size'])
        data.replace(to_replace='tld', value='tld e+04', inplace=True)
        size_norm = size_norm / 10000.0
        data['size'] = size_norm.where(data['type'] == 'host',
                                       other=data['size'])
        data.replace(to_replace='host', value='host e+07', inplace=True)
        data['size'] = size_norm.where(data['type'] == 'domain',
                                       other=data['size'])
        data.replace(to_replace='domain', value='domain e+07', inplace=True)
        size_norm = size_norm / 100.0
        data['size'] = size_norm.where(data.type == 'url',
                                       other=data['size'])
        data.replace(to_replace='url', value='url e+09', inplace=True)
        self.size_plot(data, '', '',
                       'URLs / Hosts / Domains / TLDs per Crawl',
                       'Unique Items', 'crawlsize/domain.png')

    def export_csv(self, data, csv):
        if csv is not None:
            data.reset_index().pivot(index='crawl',
                                     columns='type', values='size').to_csv(
                                         os.path.join(PLOTDIR, csv))

    def norm_data(self, data, row_filter, type_name_norm):
        if len(row_filter) > 0:
            data = data[data['type'].isin(row_filter)]
        if type_name_norm != '':
            for value in row_filter:
                replacement = value
                if isinstance(type_name_norm, str):
                    if re.search(type_name_norm, value):
                        while re.search(type_name_norm, replacement):
                            replacement = re.sub(type_name_norm,
                                                 '', replacement)
                elif isinstance(type_name_norm, types.FunctionType):
                    replacement = type_name_norm(value)
                if replacement != value:
                    data.replace(to_replace=value, value=replacement,
                                 inplace=True)
        return data

    def size_plot(self, data, row_filter, type_name_norm,
                  title, ylabel, img_file, clabel='', data_export_csv=None,
                  x='date', y='size', c='type'):
        data = self.norm_data(data, row_filter, type_name_norm)
        print(data)
        self.export_csv(data, data_export_csv)
        return self.line_plot(data, title, ylabel, img_file,
                              x=x, y=y, c=c, clabel=clabel)


if __name__ == '__main__':
    plot = CrawlSizePlot()
    plot.read_data(sys.stdin)
    plot.cumulative_size()
    plot.transform_data()
    plot.save_data()
    plot.duplicate_ratio()
    plot.plot()
