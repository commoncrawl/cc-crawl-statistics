import heapq
import json
import logging
import re
import shutil

from collections import defaultdict, Counter
from enum import Enum
from gzip import GzipFile
from io import TextIOWrapper
from tempfile import TemporaryFile
from urllib.parse import urlparse

import boto
import mrjob.util
import tldextract

from hyperloglog import HyperLogLog
from isoweek import Week
from mrjob.job import MRJob, MRStep
from mrjob.protocol import TextValueProtocol, JSONProtocol


HYPERLOGLOG_ERROR = .01

LOGGING_FORMAT = '%(asctime)s: [%(levelname)s]: %(message)s'


def set_logging_level(option, opt_str, value, parser,
                      args=None, kwargs=None):
    level = str.upper(value)
    logging.basicConfig(format=LOGGING_FORMAT, level=level)
    mrjob.util.log_to_stream(level=level, format=LOGGING_FORMAT)


class MonthlyCrawl:
    """Enumeration of monthly crawl archives"""

    by_name = {
               'CC-MAIN-2013-20': 91,
               'CC-MAIN-2013-48': 92,
               'CC-MAIN-2014-10': 93,
               'CC-MAIN-2014-15': 94,
               'CC-MAIN-2014-23': 95,
               'CC-MAIN-2014-35': 96,
               'CC-MAIN-2014-41': 97,
               'CC-MAIN-2014-42': 98,
               'CC-MAIN-2014-49': 99,
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
               'CC-MAIN-2016-30': 15,
               'CC-MAIN-2016-36': 16,
               'CC-MAIN-2016-40': 17,
               'CC-MAIN-2016-44': 18,
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

    @staticmethod
    def date_of(crawl):
        [_, _, year, week] = crawl.split('-')
        return Week(int(year), int(week)).monday()

    @staticmethod
    def short_name(name):
        return name.replace('CC-MAIN-', '')


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


class CST(Enum):
    '''Enum for crawl statistics types. Every line (key-value pair)
    has a marker which indicates the type of the count / frequency:
    - pages, URLs, hosts, etc.
    - size (number of unique items), histograms, etc.
    The type marker (the first element in the key tuple) determines
    the format of the line (key-value pair):
      <<type, key_params...>, <values...>>
    The format may vary for different steps (job, mapper, reducer).
    The count job (CCCountJob) uses the numeric types to reduce
    the data size, while CCCountJob outputs the type names for better
    readability.'''
    # types of countable items
    #   <<type, item, crawl>, <count(s)>>
    # For hosts, domains, etc. MultiCount is used to hold two counts -
    # the number of pages and URLs per item.
    url = 0  # unique URLs
    digest = 1
    host = 2
    domain = 3
    tld = 4
    surt_domain = 5
    scheme = 6
    mimetype = 7
    page = 8  # fetched pages, including URL-level duplicates
    # crawl status (successful fetches, 404s, exceptions, etc.)
    crawl_status = 55
    # size of a crawl (total number of unique items):
    #  - pages,
    #  - URLs (one URL may be fetched multiple times),
    #  - content digests,
    #  - domains, hosts, top-level domains
    #  - mime types
    # format:
    #  <<size, item_type, crawl>, number_of_unique_items>
    size = 90
    # estimates for unique URLs and content digests by HyperLogLog
    size_estimate = 91
    # new items (URLs, content digests) for a given crawl
    # (only with exact counts for all crawls)
    new_items = 95
    # histogram (frequency of item counts per page or URL)
    #   <<type, item_type, crawl, counted_per, count>, frequency>
    histogram = 96


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
    def sum_values(values):
        counts = [0]
        size = 1
        for val in values:
            if isinstance(val, int):
                # compressed count, one unique count
                for i in range(0, size):
                    counts[i] += val
            else:
                if len(val) >= size:
                    # enlarge counts array
                    base_count = counts[-1]
                    for j in range(size, len(val)):
                        counts.append(base_count)
                    size = len(val)
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


class HostDomainCount:
    """Counts requiring URL parsing (host, domain, TLD, scheme).
    For each item both total pages and unique URLs are counted.
    """

    IPpattern = re.compile('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')

    def __init__(self):
        self.hosts = MultiCount(2)
        self.schemes = MultiCount(2)

    def add(self, url, count):
        uri = urlparse(url)
        self.hosts.incr(uri.netloc.lower(), count, 1)
        self.schemes.incr(uri.scheme, count, 1)

    def output(self, crawl):
        domains = MultiCount(3)  # pages, URLs, hosts
        tlds = MultiCount(4)     # pages, URLs, hosts, domains
        for scheme, counts in self.schemes.items():
            yield (CST.scheme.value, scheme, crawl), counts
        for host, counts in self.hosts.items():
            yield (CST.host.value, host, crawl), counts
            parsedhost = tldextract.extract(host)
            hosttld = parsedhost.suffix
            if hosttld == '':
                hostdomain = parsedhost.domain
                if self.IPpattern.match(host):
                    hosttld = '(ip address)'
            else:
                hostdomain = '.'.join([parsedhost.domain, parsedhost.suffix])
            domains.incr((hostdomain, hosttld), *counts, 1)
        for dom, counts in domains.items():
            tlds.incr(dom[1], *counts, 1)
            yield (CST.domain.value, dom[0], crawl), counts
        for tld, counts in tlds.items():
            yield (CST.tld.value, tld, crawl), counts


class SurtDomainCount:
    """Counters for one single SURT prefix/domain."""

    def __init__(self, surt_domain):
        self.surt_domain = surt_domain
        self.pages = 0
        self.url = defaultdict(int)
        self.digest = defaultdict(lambda: [0, 0])
        self.mime = defaultdict(lambda: [0, 0])

    def add(self, path, metadata):
        self.pages += 1
        mime = 'unk'
        if 'mime' in metadata:
            mime = metadata['mime']
        self.digest[metadata['digest']][0] += 1
        self.mime[mime][0] += 1
        if metadata['url'] not in self.url:
            self.digest[metadata['digest']][1] += 1
            self.mime[mime][1] += 1
        self.url[metadata['url']] += 1

    def unique_urls(self):
        return len(self.url)

    def output(self, crawl, exact_count=True):
        counts = (self.pages, self.unique_urls())
        hostDomainCount = HostDomainCount()
        for url, count in self.url.items():
            hostDomainCount.add(url, count)
            if exact_count:
                yield (CST.url.value, self.surt_domain, url), (crawl, count)
        if exact_count:
            for digest, counts in self.digest.items():
                yield (CST.digest.value, digest), (crawl, counts)
        for mime, counts in self.mime.items():
            yield (CST.mimetype.value, mime, crawl), counts
        for key, val in hostDomainCount.output(crawl):
            yield key, val
        yield((CST.surt_domain.value, self.surt_domain, crawl),
              (self.pages, self.unique_urls(), len(hostDomainCount.hosts)))


class CCStatsJob(MRJob):
    '''Job to get crawl statistics from Common Crawl index
       --job=count
            run count job (first step) to get counts
            from Common Crawl index files (cdx-*.gz)
       --job=stats
            run statistics job (second step) on output
            from count job'''

    OUTPUT_PROTOCOL = JSONProtocol

    JOBCONF = {
        'mapreduce.task.timeout': '9600000',
        'mapreduce.map.speculative': 'false',
        'mapreduce.reduce.speculative': 'false',
        'mapreduce.job.jvm.numtasks': '-1',
    }

    s3pattern = re.compile('^s3://([^/]+)/(.+)')
    gzpattern = re.compile('\.gz$')
    crawlpattern = re.compile('(CC-MAIN-2\d{3}-\d{2})')
    dupl_items = 96

    def configure_options(self):
        """Custom command line options for common crawl index statistics"""
        super(CCStatsJob, self).configure_options()
        self.add_passthrough_option(
            '--job', dest='job_to_run',
            default='', choices=['count', 'stats', ''],
            help='''Job(s) to run ("count", "stats", or empty to run both)''')
        self.add_passthrough_option(
            '--exact-counts', dest='exact_counts',
            action='store_true', default=None,
            help='''Exact counts for URLs and content digests,
                    this increases the output size significantly''')
        self.add_passthrough_option(
            '--no-exact-counts', dest='exact_counts',
            action='store_false', default=None,
            help='''No exact counts for URLs and content digests
                    to save storage space and computation time''')
        self.add_passthrough_option(
            '--max-top-hosts-domains', dest='max_hosts',
            type='int', default=200,
            help='''Max. number of most frequent hosts or domains shown
                    in final statistics''')
        self.add_passthrough_option(
            '--logging-level', dest='logging_level', default='INFO',
            type='str', action='callback', callback=set_logging_level,
            help='''Initialize logging and set level''')

    def input_protocol(self):
        if self.options.job_to_run != 'stats':
            logging.debug('Reading text input from cdx files')
            return TextValueProtocol()
        logging.debug('Reading JSON input from count job')
        return JSONProtocol()

    def hadoop_input_format(self):
        input_format = self.HADOOP_INPUT_FORMAT
        if self.options.job_to_run != 'stats':
            input_format = 'org.apache.hadoop.mapred.lib.NLineInputFormat'
        logging.info("Setting input format for {} job: {}".format(
            self.options.job_to_run, input_format))
        return input_format

    def mapper_init(self):
        self.conn = boto.connect_s3()

    def count_mapper(self, _, line):
        cdx_path = line.split('\t')[-1]
        logging.info('Opening {0}'.format(cdx_path))
        try:
            crawl_name = 'unknown'
            crawl_name_match = self.crawlpattern.search(cdx_path)
            if crawl_name_match is not None:
                crawl_name = crawl_name_match.group(1)
            s3match = self.s3pattern.search(cdx_path)
            if s3match is None:
                # assume local file
                cdxtemp = open(cdx_path, mode='rb')
            else:
                # s3://
                bucket = s3match.group(1)
                s3path = s3match.group(2)
                cdxkey = self.conn.lookup(bucket).get_key(s3path)
                cdxtemp = TemporaryFile(mode='w+b')
                shutil.copyfileobj(cdxkey, cdxtemp)
                cdxtemp.seek(0)
            if self.gzpattern.search(cdx_path) is None:
                cdxstream = cdxtemp
            else:
                cdxstream = GzipFile(mode='rb', fileobj=cdxtemp)
                cdxstream = TextIOWrapper(cdxstream, 'utf-8', 'strict', '\n')
            return self._process_cdx(crawl_name, cdxstream)
        except Exception as exc:
            logging.error('Failed to read {0}: {1}'.format(cdx_path, exc))
            raise

    def _process_cdx(self, crawl_name, cdx):
        '''Process a single cdx file. Input lines are sorted by SURT URL
        which allows to aggregate URL counts for one SURT domain in memory.
        It may happen that one SURT domain spans over multiple cdx files.
        In this case (and without --exact-counts) the count of unique URLs
        and the URL histograms may be slightly off in case the same URL occurs
        also in a second cdx file. However, this problem is negligible because
        there are only 300 cdx files. '''
        self.increment_counter('cdx-stats', 'cdx files processed', 1)
        crawl = MonthlyCrawl.get_by_name(crawl_name)
        pages_total = 0
        urls_total = 0
        urls_hll = HyperLogLog(HYPERLOGLOG_ERROR)
        digest_hll = HyperLogLog(HYPERLOGLOG_ERROR)
        url_histogram = Counter()
        count = None
        for line in cdx:
            pages_total += 1
            if (pages_total % 1000) == 0:
                self.increment_counter('cdx-stats', 'cdx lines read', 1000)
            parts = line.split(' ')
            [surt_domain, path] = parts[0].split(')', 1)
            if count is None:
                count = SurtDomainCount(surt_domain)
            if surt_domain != count.surt_domain:
                # output accumulated statistics for one SURT domain
                for pair in count.output(crawl, self.options.exact_counts):
                    yield pair
                urls_total += count.unique_urls()
                for url, cnt in count.url.items():
                    urls_hll.add(url)
                    url_histogram[cnt] += 1
                for digest in count.digest:
                    digest_hll.add(digest)
                count = SurtDomainCount(surt_domain)
            json_string = ' '.join(parts[2:])
            try:
                metadata = json.loads(json_string)
            except:
                # ignore
                continue
            count.add(path, metadata)
        self.increment_counter('cdx-stats',
                               'cdx lines read', pages_total % 1000)
        for key, val in count.output(crawl, self.options.exact_counts):
            yield key, val
        urls_total += count.unique_urls()
        for url, cnt in count.url.items():
            urls_hll.add(url)
            url_histogram[cnt] += 1
        for digest in count.digest:
            digest_hll.add(digest)
        if not self.options.exact_counts:
            for count, frequency in url_histogram.items():
                yield((CST.histogram.value, CST.url.value, crawl,
                       CST.page.value, count), frequency)
        yield (CST.size.value, CST.page.value, crawl), pages_total
        if not self.options.exact_counts:
            yield (CST.size.value, CST.url.value, crawl), urls_total
        yield((CST.size_estimate.value, CST.url.value, crawl),
              CrawlStatsJSONEncoder.json_encode_hyperloglog(urls_hll))
        yield((CST.size_estimate.value, CST.digest.value, crawl),
              CrawlStatsJSONEncoder.json_encode_hyperloglog(digest_hll))
        self.increment_counter('cdx-stats', 'cdx files finished', 1)

    def reducer_init(self):
        self.counters = Counter()
        self.mostfrequent = defaultdict(list)

    def count_reducer(self, key, values):
        outputType = key[0]
        if outputType == CST.size.value:
            yield key, sum(values)
        elif outputType == CST.histogram.value:
            yield key, sum(values)
        elif outputType in (CST.url.value, CST.digest.value):
            # only with --exact-counts
            crawls = MonthlyCrawlSet()
            new_crawls = set()
            page_count = MultiCount(2)
            for val in values:
                if type(val) is list:
                    if (outputType == CST.url.value):
                        (crawl, pages) = val
                        page_count.incr(crawl, pages, 1)
                    else:  # digest
                        (crawl, (pages, urls)) = val
                        page_count.incr(crawl, pages, urls)
                    crawls.add(crawl)
                    new_crawls.add(crawl)
                else:
                    # crawl set bit mask
                    crawls.update(val)
            yield key, crawls.get_bits()
            for new_crawl in new_crawls:
                if crawls.is_new(new_crawl):
                    self.counters[(CST.new_items.value,
                                   outputType, new_crawl)] += 1
            # url/digest duplicate histograms
            for crawl, counts in page_count.items():
                items = (1+counts[0]-counts[1])
                self.counters[(CST.histogram.value, outputType,
                               crawl, CST.page.value, items)] += 1
            # size in terms of unique URLs and unique content digests
            for crawl, counts in page_count.items():
                self.counters[(CST.size.value, outputType, crawl)] += 1
        elif outputType in (CST.mimetype.value,
                            CST.scheme.value,
                            CST.tld.value,
                            CST.domain.value,
                            CST.surt_domain.value,
                            CST.host.value):
            yield key, MultiCount.sum_values(values)
        elif outputType == CST.size_estimate.value:
            hll = HyperLogLog(HYPERLOGLOG_ERROR)
            for val in values:
                hll.update(
                    CrawlStatsJSONDecoder.json_decode_hyperloglog(val))
            yield(key,
                  CrawlStatsJSONEncoder.json_encode_hyperloglog(hll))
        else:
            logging.error('Unhandled type {}\n'.format(outputType))
            raise

    def stats_mapper(self, key, value):
        if key[0] in (CST.url.value, CST.digest.value):
            return
        yield key, value

    def stats_reducer(self, key, values):
        outputType = CST(key[0])
        item = key[1]
        crawl = MonthlyCrawl.to_name(key[2])
        if outputType in (CST.size, CST.new_items, CST.size_estimate):
            verbose_key = (outputType.name, CST(item).name, crawl)
            if outputType == CST.size:
                val = sum(values)
            elif outputType == CST.new_items:
                val = MultiCount.sum_values(values)
            elif outputType == CST.size_estimate:
                # already "reduced" in count job
                for val in values:
                    break
            yield verbose_key, val
        elif outputType == CST.histogram:
            yield((outputType.name, CST(item).name, crawl,
                   CST(key[3]).name, key[4]), sum(values))
        elif outputType in (CST.mimetype, CST.scheme, CST.surt_domain,
                            CST.tld, CST.domain, CST.host):
            item = key[1]
            for counts in values:
                self.counters[(CST.size.name, outputType.name, crawl)] += 1
                page_count = MultiCount.get_count(0, counts)
                url_count = MultiCount.get_count(1, counts)
                self.counters[(CST.histogram.name, outputType.name,
                               crawl, CST.page.name, page_count)] += 1
                self.counters[(CST.histogram.name, outputType.name,
                               crawl, CST.url.name, url_count)] += 1
                if outputType in (CST.domain, CST.surt_domain, CST.tld):
                    host_count = MultiCount.get_count(2, counts)
                    self.counters[(CST.histogram.name, outputType.name,
                                   crawl, CST.host.name, host_count)] += 1
                if outputType == CST.tld:
                    domain_count = MultiCount.get_count(3, counts)
                    self.counters[(CST.histogram.name, outputType.name,
                                   crawl, CST.domain.name, domain_count)] += 1
                if outputType in (CST.domain, CST.host, CST.surt_domain):
                    outKey = (outputType.name, crawl)
                    outVal = (page_count, url_count, item)
                    if outputType in (CST.domain, CST.surt_domain):
                        outVal = (page_count, url_count, host_count, item)
                    # take most common
                    if len(self.mostfrequent[outKey]) < self.options.max_hosts:
                        heapq.heappush(self.mostfrequent[outKey], outVal)
                    else:
                        heapq.heappushpop(self.mostfrequent[outKey], outVal)
                else:
                    yield((outputType.name, item, crawl), counts)
        else:
            logging.error('Unhandled type {}\n'.format(outputType))
            raise

    def reducer_final(self):
        for (counter, count) in self.counters.items():
            yield counter, count
        for key, mostfrequent in self.mostfrequent.items():
            (outputType, crawl) = key
            if outputType in (CST.domain.name, CST.surt_domain.name):
                for (pages, urls, hosts, item) in mostfrequent:
                    yield((outputType, item, crawl),
                          MultiCount.compress(3, [pages, urls, hosts]))
            else:
                for (pages, urls, item) in mostfrequent:
                    yield((outputType, item, crawl),
                          MultiCount.compress(2, [pages, urls]))

    def steps(self):
        reduces = 10
        if self.options.exact_counts:
            # with exact counts need many reducers to aggregate the counts
            # in reasonable time and to get not too large partitions
            reduces = 200
        count_job = \
            MRStep(mapper_init=self.mapper_init,
                   mapper=self.count_mapper,
                   reducer_init=self.reducer_init,
                   reducer=self.count_reducer,
                   reducer_final=self.reducer_final,
                   jobconf={'mapreduce.job.reduces': reduces,
                            'mapreduce.output.fileoutputformat.compress':
                                "true",
                            'mapreduce.output.fileoutputformat.compress.codec':
                                'org.apache.hadoop.io.compress.BZip2Codec'})
        stats_job = \
            MRStep(mapper_init=self.mapper_init,
                   mapper=self.stats_mapper,
                   reducer_init=self.reducer_init,
                   reducer=self.stats_reducer,
                   reducer_final=self.reducer_final,
                   jobconf={'mapreduce.job.reduces': 1,
                            'mapreduce.output.fileoutputformat.compress':
                                "true",
                            'mapreduce.output.fileoutputformat.compress.codec':
                                'org.apache.hadoop.io.compress.GzipCodec'})
        if self.options.job_to_run == 'count':
            return [count_job]
        if self.options.job_to_run == 'stats':
            return [stats_job]
        return [count_job, stats_job]


if __name__ == '__main__':
    CCStatsJob.run()
