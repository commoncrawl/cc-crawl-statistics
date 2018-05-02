import heapq
import re
import sys

from collections import defaultdict, Counter

import pandas

from crawlplot import CrawlPlot, PLOTDIR
from crawlstats import CST, MonthlyCrawl, MultiCount


class MimeTypeStats(CrawlPlot):

    MIN_AVERAGE_COUNT = 500
    MAX_MIME_TYPES = 100

    # see https://en.wikipedia.org/wiki/Media_type#Naming
    mime_pattern_str = \
        '(?:x-)?[a-z]+/[a-z0-9]+' \
        '(?:[.-](?:c\+\+[a-z]*|[a-z0-9]+))*(?:\+[a-z0-9]+)?'
    mime_pattern = re.compile('^'+mime_pattern_str+'$')
    mime_extract_pattern = re.compile('^\s*(?:content\s*=\s*)?["\']?\s*(' +
                                      mime_pattern_str +
                                      ')(?:\s*[;,].*)?\s*["\']?\s*$')

    def __init__(self):
        self.crawls = set()
        self.types = defaultdict(dict)
        self.type_stats = defaultdict(dict)
        self.types_total = Counter()
        self.N = 0

    @staticmethod
    def norm_mimetype(mimetype):
        if type(mimetype) is str:
            mimetype = mimetype.lower()
            m = MimeTypeStats.mime_extract_pattern.match(mimetype)
            if m:
                return m.group(1)
            return mimetype.strip('"\', \t')
        return ""

    def add(self, key, val):
        cst = CST[key[0]]
        if cst != CST.mimetype:
            return
        mimetype = key[1]
        crawl = key[2]
        self.crawls.add(crawl)
        mimetype = MimeTypeStats.norm_mimetype(mimetype)
        if crawl in self.types[mimetype]:
            self.types[mimetype][crawl] = \
                MultiCount.sum_values([val, self.types[mimetype][crawl]])
        else:
            self.types[mimetype][crawl] = val
        npages = MultiCount.get_count(0, val)
        self.types_total[mimetype] += npages

    def transform_data(self, top_n, min_avg_count):
        print("Number of different MIME types after first normalization: {}"
              .format(len(self.types)))
        mimetypes_for_deletion = set()
        mimetypes_mostfrequent = []
        for mimetype in self.types:
            total_count = self.types_total[mimetype]
            average_count = int(total_count / len(self.crawls))
            if average_count >= top_n:
                if MimeTypeStats.mime_pattern.match(mimetype):
                    print('{}\t{}\t{}'.format(mimetype,
                                              average_count, total_count))
                    fval = (total_count, mimetype)
                    if len(mimetypes_mostfrequent) < top_n:
                        heapq.heappush(mimetypes_mostfrequent, fval)
                    else:
                        heapq.heappushpop(mimetypes_mostfrequent, fval)
                    continue  # ok, keep this MIME type
                else:
                    print('MIME type frequent but invalid: <{}> (avg. count = {})'
                          .format(mimetype, average_count))
            elif average_count >= (min_avg_count/10):
                if MimeTypeStats.mime_pattern.match(mimetype):
                    print('Skipped MIME type because of low frequency: <{}> (avg. count = {})'
                          .format(mimetype, average_count))
            mimetypes_for_deletion.add(mimetype)
        # map low frequency or invalid MIME types to empty type
        keep_mimetypes = set()
        for (_, mimetype) in mimetypes_mostfrequent:
            keep_mimetypes.add(mimetype)
        for mimetype in self.types:
            if (mimetype not in keep_mimetypes and
                    mimetype not in mimetypes_for_deletion):
                print('Skipped MIME type because not in top {}: <{}> (avg. count = {})'
                      .format(top_n, mimetype,
                              int(self.types_total[mimetype]/len(self.crawls))))
                mimetypes_for_deletion.add(mimetype)
        mimetypes_other = dict()
        for mimetype in mimetypes_for_deletion:
            for crawl in self.types[mimetype]:
                if crawl in mimetypes_other:
                    val = mimetypes_other[crawl]
                else:
                    val = 0
                mimetypes_other[crawl] = \
                    MultiCount.sum_values([val, self.types[mimetype][crawl]])
            self.types.pop(mimetype, None)
        self.types['<other>'] = mimetypes_other
        print('Number of different MIME types after cleaning and'
              ' removal of low frequency types: {}'
              .format(len(self.types)))
        for mimetype in self.types:
            for crawl in self.types[mimetype]:
                self.type_stats['mimetype'][self.N] = mimetype
                self.type_stats['crawl'][self.N] = crawl
                value = self.types[mimetype][crawl]
                n_pages = MultiCount.get_count(0, value)
                self.type_stats['pages'][self.N] = n_pages
                n_urls = MultiCount.get_count(1, value)
                self.type_stats['urls'][self.N] = n_urls
                self.N += 1
        self.type_stats = pandas.DataFrame(self.type_stats)

    def save_data(self):
        self.type_stats.to_csv('data/mimetypes.csv')

    def plot(self, crawls, name):
        # stats comparison for selected crawls
        field_percentage_formatter = '{0:,.4f}'.format
        data = self.type_stats
        data = data[data['crawl'].isin(crawls)]
        data = data[['crawl', 'mimetype', 'pages']]
        data = data.groupby(['crawl', 'mimetype']).agg({'pages': 'sum'})
        data = data.groupby(level=0).apply(lambda x: 100.0*x/float(x.sum()))
        data = data.reset_index().pivot(index='mimetype',
                                        columns='crawl', values='pages')
        print("\n-----\n")
        print(data.to_string(formatters={c: field_percentage_formatter
                                         for c in crawls}))
        print(data.to_html('{}/mimetypes{}-top-{}.html'.format(
                            PLOTDIR, name, MimeTypeStats.MAX_MIME_TYPES),
                           formatters={c: field_percentage_formatter
                                       for c in crawls},
                           classes=['tablesorter', 'tablepercentage']))


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    plot_name = '-'.join(plot_crawls)
    if len(plot_crawls) == 0:
        plot_crawls = MonthlyCrawl.get_last(3)
        plot_name = ''
        print(plot_crawls)
    plot = MimeTypeStats()
    plot.read_data(sys.stdin)
    plot.transform_data(MimeTypeStats.MAX_MIME_TYPES,
                        MimeTypeStats.MIN_AVERAGE_COUNT)
    plot.save_data()
    plot.plot(plot_crawls, plot_name)
