import heapq

import numpy
import pandas

from collections import defaultdict, Counter

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, MultiCount


class TabularStats(CrawlPlot):

    def __init__(self):
        self.crawls = set()
        self.types = defaultdict(dict)
        self.type_stats = defaultdict(dict)
        self.types_total = Counter()
        self.size = defaultdict(dict)
        self.N = 0

    def norm_value(self, typeval):
        return typeval

    def add_check_type(self, key, val, requ_type_cst):
        cst = CST[key[0]]
        if cst != requ_type_cst and cst != CST.size:
            return
        typeval = key[1]
        crawl = key[2]
        self.crawls.add(crawl)
        typeval = self.norm_value(typeval)
        if cst == CST.size:
            self.size[crawl][typeval] = int(val)
            return
        if crawl in self.types[typeval]:
            self.types[typeval][crawl] = \
                MultiCount.sum_values([val, self.types[typeval][crawl]])
        else:
            self.types[typeval][crawl] = val
        npages = MultiCount.get_count(0, val)
        self.types_total[typeval] += npages
        if 'known_values' not in self.size[crawl]:
            self.size[crawl]['known_values'] = 0
        self.size[crawl]['known_values'] += npages

    def transform_data(self, top_n, min_avg_count, check_pattern=None):
        print("Number of different values after first normalization: {}"
              .format(len(self.types)))
        typevals_for_deletion = set()
        typevals_mostfrequent = []
        for typeval in self.types:
            total_count = self.types_total[typeval]
            average_count = int(total_count / len(self.crawls))
            if average_count >= min_avg_count:
                if not check_pattern or check_pattern.match(typeval):
                    print('{}\t{}\t{}'.format(typeval,
                                              average_count, total_count))
                    fval = (total_count, typeval)
                    if len(typevals_mostfrequent) < top_n:
                        heapq.heappush(typevals_mostfrequent, fval)
                    else:
                        heapq.heappushpop(typevals_mostfrequent, fval)
                    continue  # ok, keep this type value
                else:
                    print('Type value frequent but invalid: <{}> (avg. count = {})'
                          .format(typeval, average_count))
            elif average_count >= (min_avg_count/10):
                if not check_pattern or check_pattern.match(typeval):
                    print('Skipped type value because of low frequency: <{}> (avg. count = {}, min. = {})'
                          .format(typeval, average_count, (min_avg_count/10)))
            typevals_for_deletion.add(typeval)
        # map low frequency or invalid type values to empty type
        keep_typevals = set()
        for (_, typeval) in typevals_mostfrequent:
            keep_typevals.add(typeval)
        for typeval in self.types:
            if (typeval not in keep_typevals and
                    typeval not in typevals_for_deletion):
                print('Skipped type value because not in top {}: <{}> (avg. count = {})'
                      .format(top_n, typeval,
                              int(self.types_total[typeval]/len(self.crawls))))
                typevals_for_deletion.add(typeval)
        typevals_other = dict()
        for typeval in typevals_for_deletion:
            for crawl in self.types[typeval]:
                if crawl in typevals_other:
                    val = typevals_other[crawl]
                else:
                    val = 0
                typevals_other[crawl] = \
                    MultiCount.sum_values([val, self.types[typeval][crawl]])
            self.types.pop(typeval, None)
        self.types['<other>'] = typevals_other
        print('Number of different type values after cleaning and'
              ' removal of low frequency types: {}'
              .format(len(self.types)))
        # unknown values
        for crawl in self.crawls:
            known_values = 0
            if 'known_values' in self.size[crawl]:
                known_values = self.size[crawl]['known_values']
            unknown = (self.size[crawl]['page'] - known_values)
            if unknown > 0:
                print("{} unknown values in {}".format(unknown, crawl))
                self.types['<unknown>'][crawl] = unknown
        for typeval in self.types:
            for crawl in self.types[typeval]:
                self.type_stats['type'][self.N] = typeval
                self.type_stats['crawl'][self.N] = crawl
                value = self.types[typeval][crawl]
                n_pages = MultiCount.get_count(0, value)
                self.type_stats['pages'][self.N] = n_pages
                n_urls = MultiCount.get_count(1, value)
                self.type_stats['urls'][self.N] = n_urls
                self.N += 1
        self.type_stats = pandas.DataFrame(self.type_stats)

    def save_data(self, base_name, dir_name='data/'):
        self.type_stats.to_csv(dir_name + base_name + '.csv')

    def save_data_percentage(self, base_name, dir_name='data/', type_name='type'):
        if dir_name[-1] != '/':
            dir_name += '/'
        data = self.type_stats
        data = data[['crawl', 'type', 'pages', 'urls']]
        sum_data = data.groupby(['crawl']).aggregate({'pages':'sum'}).add_suffix('_sum').reset_index()
        data = data.groupby(['crawl', 'type']).aggregate(numpy.sum).reset_index()
        data = pandas.merge(data, sum_data)
        data['%pages/crawl'] = 100.0 * data['pages'] / data['pages_sum']
        data.drop(['pages_sum'], inplace=True, axis=1)
        data = data.rename(columns={'type': type_name})
        data.to_csv(dir_name + base_name + '.csv', float_format='%.4f', index=None)

    def plot(self, crawls, name, column_header, xtra_css_classes=[]):
        # stats comparison for selected crawls
        field_percentage_formatter = '{0:,.4f}'.format
        data = self.type_stats
        data = data[data['crawl'].isin(crawls)]
        if data.size == 0:
            print("No data points in table for selected crawls ({})"
                  .format(crawls))
            return
        data[column_header] = data['type']
        data = data[['crawl', column_header, 'pages']]
        data = data.groupby(['crawl', column_header]).agg({'pages': 'sum'})
        data = data.groupby(level=0, as_index=False).apply(lambda x: 100.0*x/float(x.sum()))
        data = data.reset_index().pivot(index=column_header,
                                        columns='crawl', values='pages')
        print("\n-----\n")
        formatters = {c: field_percentage_formatter for c in crawls}
        print(data.to_string(formatters=formatters))
        css_classes = ['tablesorter', 'tablepercentage']
        css_classes.extend(xtra_css_classes)
        data.to_html('{}/{}-top-{}.html'.format(
                     PLOTDIR, name, self.MAX_TYPE_VALUES),
                     formatters=formatters,
                     classes=css_classes)

