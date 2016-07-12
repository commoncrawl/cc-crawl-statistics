from collections import defaultdict
from enum import Enum
from hyperloglog import HyperLogLog
import json


HYPERLOGLOG_ERROR = .01


class MonthlyCrawl:
    """Enumeration of monthly crawl archives"""

    by_name = {
               'CC-MAIN-2014-52': 0,
               'CC-MAIN-2015-06': 1,
               'CC-MAIN-2015-11': 2,
               'CC-MAIN-2015-14': 3,
               'CC-MAIN-2015-18': 4,
               'CC-MAIN-2015-22': 5,
               'CC-MAIN-2015-27': 6,
               'CC-MAIN-2015-32': 7,
               'CC-MAIN-2015-35': 8,
               'CC-MAIN-2015-40': 9,
               'CC-MAIN-2015-48': 10,
               'CC-MAIN-2016-07': 11,
               'CC-MAIN-2016-18': 12,
               'CC-MAIN-2016-22': 13,
               'CC-MAIN-2016-26': 14,
               }

    by_id = dict(map(reversed, by_name.items()))

    @staticmethod
    def get_by_name(name):
        return MonthlyCrawl.by_name[name]

    @staticmethod
    def to_name(crawl):
        return MonthlyCrawl.by_id[crawl]

    @staticmethod
    def to_bit_mask(crawl):
        return (1 << crawl)


class MonthlyCrawlSet:
    """Dense representation of a list of monthly crawls.
    Represent in which crawls a given item (URL, but also
    domain, host, digest) occurs.
    """

    def __init__(self, crawls=0):
        self.bits = crawls

    def add(self, crawl):
        self.bits |= MonthlyCrawl.to_bit_mask(crawl)

    def update(self, *others):
        for other in others:
            self.bits |= other.get_bits()

    def clear(self):
        self.bits = 0

    def discard(self, crawl):
        self.bits &= ~MonthlyCrawl.to_bit_mask(crawl)

    def __contains__(self, crawl):
        return (self.bits & MonthlyCrawl.to_bit_mask(crawl)) != 0

    def __len__(self):
        i = self.bits
        i = i - ((i >> 1) & 0x55555555)
        i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
        return (((i + (i >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24

    def get_bits(self):
        return self.bits

    def get_crawls(self):
        i = self.bits
        r = 0
        while (i):
            if (i & 1):
                yield r
            r += 1
            i >>= 1

    def is_new(self, crawl):
        """True if there are no older crawls in set (no lower id)"""
        if (self.bits == 0):
            return True
        i = self.bits
        i = (i ^ (i - 1)) >> 1  # set trailing 0s to 1s and zero rest
        r = 0
        while (i):
            if r == crawl:
                return True
            r += 1
            i >>= 1
        if (r < crawl):
            return False
        return True

    def is_newest(self, crawl):
        """True if crawl is the newest crawl in set (highest id)"""
        # i = self.bits
        # j = MonthlyCrawl.to_bit_mask(crawl)
        # return (i & ~j) < j
        return self.bits.bit_length() == (crawl + 1)


class CrawlStatsType(Enum):
    # countable items
    url = 0  # unique URLs
    digest = 1
    host = 2
    domain = 3
    tld = 4
    surt_domain = 5
    scheme = 6
    mimetype = 7
    page = 8
    # size of a crawl:
    #  total number of pages, URLs (one URL may be fetched multiple times),
    #  content digests, domains, hosts, etc.
    size = 90
    # estimates for unique URLs and content digests by HyperLogLog
    size_estimate = 91
    # new items for a given crawl (only with exact counts for all crawls)
    new_items = 95
    # histogram <<counted_item, crawl, count_per_item, bin/count>, frequency>
    histogram = 96
    # estimated histogram (for URL duplicate counts without exact counts)
    histogram_estim = 97


class MultiCount(defaultdict):
    """Dictionary with multiple counters for the same key"""

    def __init__(self, size):
        self.default_factory = lambda: [0]*size
        self.size = size

    def incr(self, key, *counts):
        for i in range(0, self.size):
            self[key][i] += counts[i]

    @staticmethod
    def compress(size, counts):
        compress_from = size-1
        last_val = counts[compress_from]
        while compress_from > 0 and last_val == counts[compress_from-1]:
            compress_from -= 1
        if compress_from == 0:
            return counts[0]
        else:
            return counts[0:compress_from+1]

    def get_compressed(self, key):
        return MultiCount.compress(self.size, self.get(key))

    @staticmethod
    def get_count(index, value):
        if isinstance(value, int):
            return value
        if len(value) <= index:
            return value[-1]
        return value[index]

    @staticmethod
    def sum_values(size, values):
        counts = [0]*size
        for val in values:
            if isinstance(val, int):
                # compressed count, one unique count
                for i in range(0, size):
                    counts[i] += val
            else:
                for i in range(0, len(val)):
                    counts[i] += val[i]
                if len(val) < size:
                    for j in range(i+1, size):
                        # add compressed counts
                        counts[j] += val[i]
        return MultiCount.compress(size, counts)


class CrawlStatsJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, MonthlyCrawlSet):
            return o.get_bits()
        if isinstance(o, HyperLogLog):
            return CrawlStatsJSONEncoder.json_encode_hyperloglog(o)
        return json.JSONEncoder.default(self, o)

    @staticmethod
    def json_encode_hyperloglog(o):
        return {'__type__': 'HyperLogLog',
                'card': o.card(),
                'p': o.p, 'M': o.M, 'm': o.m, 'alpha': o.alpha}


class CrawlStatsJSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object,
                                  *args, **kargs)

    def dict_to_object(self, dic):
        if '__type__' not in dic:
            return dic
        if dic['__type__'] == 'HyperLogLog':
            try:
                return CrawlStatsJSONDecoder.json_decode_hyperloglog(dic)
            except:
                print(dic['__type__'])
                raise
                return dic

    @staticmethod
    def json_decode_hyperloglog(dic):
        hll = HyperLogLog(.01)
        hll.p = dic['p']
        hll.m = dic['m']
        hll.alpha = dic['alpha']
        hll.M = dic['M']
        return hll
