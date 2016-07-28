import json
import logging
import os.path
import pandas
import re
import sys

from collections import defaultdict
from hyperloglog import HyperLogLog

from crawlstats import CST, CrawlStatsJSONDecoder, HYPERLOGLOG_ERROR,\
    MonthlyCrawl

PLOTLIB = 'rpy2.ggplot2'
PLOTDIR = 'plots'

if PLOTLIB == 'ggplot':
    from ggplot import *
elif PLOTLIB == 'rpy2.ggplot2':
    from rpy2.robjects.lib import ggplot2
    from rpy2.robjects import pandas2ri
    pandas2ri.activate()


class CrawlSizePlot:

    def __init__(self):
        self.size = defaultdict(dict)
        self.size_by_type = defaultdict(dict)
        self.crawls = {}
        self.ncrawls = 0
        self.hll = defaultdict(dict)
        self.N = 0

    def add(self, key, val):
        cst = CST[key[0]]
        if cst not in (CST.size, CST.size_estimate):
            return
        item_type = key[1]
        crawl = key[2]
        count = 0
        if crawl not in self.crawls:
            self.crawls[crawl] = self.ncrawls
            self.size['crawl'][self.ncrawls] = crawl
            date = pandas.Timestamp(MonthlyCrawl.date_of(crawl))
            self.size['date'][self.ncrawls] = date
            self.ncrawls += 1
        if cst == CST.size_estimate:
            item_type = ' '.join([item_type, 'estim.'])
            hll = CrawlStatsJSONDecoder.json_decode_hyperloglog(val)
            count = len(hll)
            self.hll[item_type][crawl] = hll
        elif cst == CST.size:
            count = val
        self.add_by_type(crawl, item_type, count)

    def add_by_type(self, crawl, item_type, count):
        self.size[item_type][self.crawls[crawl]] = count
        self.size_by_type['crawl'][self.N] = crawl
        date = pandas.Timestamp(MonthlyCrawl.date_of(crawl))
        self.size_by_type['date'][self.N] = date
        self.size_by_type['type'][self.N] = item_type
        self.size_by_type['size'][self.N] = count
        self.N += 1

    def cumulative_size(self):
        for item_type in self.hll.keys():
            item_type_cumul = ' '.join([item_type, 'cumul.'])
            item_type_new = ' '.join([item_type, 'new'])
            cumul_hll = HyperLogLog(HYPERLOGLOG_ERROR)
            n = 0
            hlls = []
            total = 0
            for crawl in sorted(self.hll[item_type]):
                total += self.size['page'][self.crawls[crawl]]
                self.add_by_type(crawl, 'page cumul.', total)
                n += 1
                hll = self.hll[item_type][crawl]
                last_cumul_hll_len = len(cumul_hll)
                cumul_hll.update(hll)
                # cumulative size
                self.add_by_type(crawl, item_type_cumul, len(cumul_hll))
                # new unseen items this crawl (since the first analyzed crawl)
                unseen = (len(cumul_hll) - last_cumul_hll_len)
                self.add_by_type(crawl, item_type_new, unseen)
                hlls.append(hll)
                # cumulative size for last N crawls
                for n_crawls in [2, 3, 6, 12]:
                    item_type_n_crawls = '{} cumul. last {} crawls'.format(
                        item_type, n_crawls)
                    if n_crawls <= len(hlls):
                        cum_hll = HyperLogLog(HYPERLOGLOG_ERROR)
                        for i in range(1, (n_crawls+1)):
                            if i > len(hlls):
                                break
                            cum_hll.update(hlls[-i])
                        size_last_n = len(cum_hll)
                    else:
                        size_last_n = 'nan'
                    self.add_by_type(crawl, item_type_n_crawls, size_last_n)

    def read_data(self, stream):
        for line in stream:
            keyval = line.split('\t')
            if len(keyval) == 2:
                key = json.loads(keyval[0])
                val = json.loads(keyval[1])
                size_plot.add(key, val)
            else:
                logging.error("Not a key-value pair: {}".find(line))
        self.cumulative_size()
        self.size = pandas.DataFrame(self.size)
        self.size.to_csv('data/crawlsize.csv')
        self.size_by_type = pandas.DataFrame(self.size_by_type)
        self.size_by_type.to_csv('data/crawlsizebytype.csv')

    def plot(self):
        # -- size per crawl (pages, URL and content digest)
        row_types = ['page', 'url',  # 'url estim.',
                     'digest estim.']
        self.size_plot(self.size_by_type, row_types, '',
                       'Crawl Size', 'Pages / Unique Items',
                       'crawlsize.png')
        # -- cumulative size
        row_types = ['page cumul.', 'url estim. cumul.',
                     'digest estim. cumul.']
        self.size_plot(self.size_by_type, row_types, ' cumul\.$',
                       'Crawl Size Cumulative',
                       'Pages / Unique Items Cumulative',
                       'crawlsize_cumulative.png')
        # -- new items per crawl
        row_types = ['page', 'url estim. new',
                     'digest estim. new']
        self.size_plot(self.size_by_type, row_types, ' new$',
                       'New Items per Crawl (not observed in prior crawls)',
                       'Pages / New Items', 'crawlsize_new.png')
        # -- cumulative URLs over last N crawls (this and preceding N-1 crawls)
        row_types = ['url', '1 crawl',  # 'url' replaced by '1 crawl'
                     'url estim. cumul. last 2 crawls',
                     'url estim. cumul. last 3 crawls',
                     'url estim. cumul. last 6 crawls',
                     'url estim. cumul. last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='url', value='1 crawl', inplace=True)
        self.size_plot(data, row_types, '^url estim\. cumul\. last ',
                       'URLs Cumulative Over Last N Crawls',
                       'Unique URLs cumulative',
                       'crawlsize_url_last_n_crawls.png')
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
                       '^digest estim\. cumul\. last ',
                       'Content Digest Cumulative Over Last N Crawls',
                       'Unique content digests cumulative',
                       'crawlsize_digest_last_n_crawls.png')
        # -- URLs, hosts, domains, tlds (normalized)
        data = self.size_by_type
        row_types = ['url', 'tld', 'domain', 'host']
        data = data[data['type'].isin(row_types)]
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
                       'Unique Items', 'crawlsize_domain.png')

    def size_plot(self, data, row_filter, type_name_norm,
                  title, ylabel, img_file):
        if len(row_filter) > 0:
            data = data[data['type'].isin(row_filter)]
        if type_name_norm is not '':
            for value in row_filter:
                if re.search(type_name_norm, value):
                    replacement = re.sub(type_name_norm, '', value)
                    data.replace(to_replace=value, value=replacement,
                                 inplace=True)
        if PLOTLIB == 'ggplot':
            # date_label = "%Y\n%b"
            date_label = "%Y\n%W"  # year + week number
            p = ggplot(data,
                       aes(x='date', y='size', color='type')) \
                + ggtitle(title) \
                + ylab(ylabel) \
                + xlab(' ') \
                + scale_x_date(breaks=date_breaks('3 months'),
                               labels=date_label) \
                + geom_line() + geom_point()
        elif PLOTLIB == 'rpy2.ggplot2':
            # convert size to float because R uses 32-bit signed integers,
            # values > 2 bln. (2^31) will overflow
            data['size'] = data['size'].astype(float)
            p = ggplot2.ggplot(data) \
                + ggplot2.aes_string(x='date', y='size', color='type') \
                + ggplot2.geom_line() + ggplot2.geom_point() \
                + ggplot2.labs(title=title, x='', y=ylabel, color='')
        img_path = os.path.join(PLOTDIR, img_file)
        p.save(img_path)
        # data.to_csv(img_path + '.csv')
        return p


if __name__ == '__main__':
    size_plot = CrawlSizePlot()
    size_plot.read_data(sys.stdin)
    size_plot.plot()
