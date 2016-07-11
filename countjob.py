import boto
import json
import logging
import re
import shutil
import tldextract

from collections import defaultdict, Counter
from gzip import GzipFile
from hyperloglog import HyperLogLog
from io import TextIOWrapper
from tempfile import TemporaryFile
from urllib.parse import urlparse

from mrjob.job import MRJob, MRStep
from mrjob.protocol import RawValueProtocol, JSONProtocol

from crawlstat import MonthlyCrawl, MonthlyCrawlSet, HYPERLOGLOG_ERROR
from crawlstat import CrawlStatsJSONEncoder, CrawlStatsJSONDecoder
from crawlstat import CrawlStatsType as cst
from crawlstat import MultiCount


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
        self.hosts.incr(uri.netloc, count, 1)
        self.schemes.incr(uri.scheme, count, 1)

    def output(self, crawl):
        domains = MultiCount(2)
        tlds = MultiCount(2)
        for scheme, counts in self.schemes.items():
            yield (cst.scheme.value, scheme, crawl), counts
        for host, counts in self.hosts.items():
            yield (cst.host.value, host, crawl), counts
            parsedhost = tldextract.extract(host)
            hosttld = parsedhost.suffix
            if hosttld == '':
                hostdomain = parsedhost.domain
                if self.IPpattern.match(host):
                    hosttld = '(ip address)'
            else:
                hostdomain = '.'.join([parsedhost.domain, parsedhost.suffix])
            tlds.incr(hosttld, *counts)
            domains.incr(hostdomain, *counts)
        for tld, counts in tlds.items():
            yield (cst.tld.value, tld, crawl), counts
        for dom, counts in domains.items():
            yield (cst.domain.value, dom, crawl), counts


class SurtDomainCount:
    """Counters for one single SURT prefix/host/domain"""

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

    def output(self, crawl):
        counts = (self.pages, self.unique_urls())
        yield (cst.surt_domain.value, self.surt_domain, crawl), counts
        hostDomainCount = HostDomainCount()
        for url, count in self.url.items():
            hostDomainCount.add(url, count)
            yield (cst.url.value, self.surt_domain, url), (crawl, count)
        for digest, counts in self.digest.items():
            yield (cst.digest.value, digest), (crawl, counts)
        for mime, counts in self.mime.items():
            yield (cst.mimetype.value, mime, crawl), counts
        for key, val in hostDomainCount.output(crawl):
            yield key, val


class CCStatsCountJob(MRJob):

    INPUT_PROTOCOL = RawValueProtocol
    OUTPUT_PROTOCOL = JSONProtocol

    HADOOP_INPUT_FORMAT = 'org.apache.hadoop.mapred.lib.NLineInputFormat'

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

    logging.basicConfig(format='%(asctime)s: [%(levelname)s]: %(message)s',
                        level=logging.DEBUG)

    def configure_options(self):
        """Custom command line options for common crawl index statistics"""
        super(CCStatsCountJob, self).configure_options()

    def mapper_init(self):
        self.conn = boto.connect_s3()

    def mapper(self, _, line):
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
        self.increment_counter('cdx-stats', 'cdx files processed', 1)
        crawl = MonthlyCrawl.get_by_name(crawl_name)
        pages_total = 0
        urls_total = 0
        urls_hll = HyperLogLog(HYPERLOGLOG_ERROR)
        digest_hll = HyperLogLog(HYPERLOGLOG_ERROR)
        count = None
        for line in cdx:
            pages_total += 1
            if pages_total == 1000:
                self.increment_counter('cdx-stats', 'cdx lines read', 1000)
            parts = line.split(' ')
            [surt_domain, path] = parts[0].split(')', 1)
            if count is None:
                count = SurtDomainCount(surt_domain)
            if surt_domain != count.surt_domain:
                # output accumulated statistics for on SURT domain
                for pair in count.output(crawl):
                    yield pair
                urls_total += count.unique_urls()
                for url in count.url:
                    urls_hll.add(url)
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
        for key, val in count.output(crawl):
            yield key, val
        urls_total += count.unique_urls()
        for url in count.url:
            urls_hll.add(url)
        for digest in count.digest:
            digest_hll.add(digest)
        yield (cst.size.value, cst.page.value, crawl), pages_total
        yield (cst.size.value, cst.url.value, crawl), urls_total
        yield((cst.size_estimate.value, cst.url.value, crawl),
              CrawlStatsJSONEncoder.json_encode_hyperloglog(urls_hll))
        yield((cst.size_estimate.value, cst.digest.value, crawl),
              CrawlStatsJSONEncoder.json_encode_hyperloglog(urls_hll))
        self.increment_counter('cdx-stats', 'cdx files finished', 1)

    def reducer_init(self):
        self.counters = Counter()

    def reducer(self, key, values):
        outputType = key[0]
        if outputType == cst.size.value:
            yield key, sum(values)
        elif outputType in (cst.url.value, cst.digest.value):
            crawls = MonthlyCrawlSet()
            new_crawls = set()
            page_count = MultiCount(2)
            for val in values:
                if type(val) is list:
                    if (outputType == cst.url.value):
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
                    self.counters[(cst.new_items.value, outputType, new_crawl)] += 1
            # url/digest duplicate histograms
            for crawl, counts in page_count.items():
                items = (1+counts[0]-counts[1])
                self.counters[(cst.dupl_histogram.value,
                               outputType, crawl, items)] += 1
            # size in terms of unique content digests
            if outputType == cst.digest.value:
                for crawl, counts in page_count.items():
                    self.counters[(cst.size.value, outputType, crawl)] += 1
        elif outputType in (cst.mimetype.value,
                            cst.scheme.value,
                            cst.tld.value,
                            cst.domain.value,
                            cst.surt_domain.value,
                            cst.host.value):
            yield key, MultiCount.sum_values(2, values)
        elif outputType == cst.size_estimate.value:
            hll = HyperLogLog(HYPERLOGLOG_ERROR)
            for val in values:
                hll.update(
                    CrawlStatsJSONDecoder.json_decode_hyperloglog(val))
            yield(key,
                  CrawlStatsJSONEncoder.json_encode_hyperloglog(hll))
        else:
            logging.error('Unhandled type {}\n'.format(outputType))
            raise

    def reducer_final(self):
        for (counter, count) in self.counters.items():
            yield counter, count

    def steps(self):
        return [
            MRStep(mapper_init=self.mapper_init,
                   mapper=self.mapper,
                   reducer_init=self.reducer_init,
                   reducer=self.reducer,
                   reducer_final=self.reducer_final,
                   jobconf={'mapreduce.job.reduces': 200,
                            'mapreduce.output.fileoutputformat.compress':
                                "true",
                            'mapreduce.output.fileoutputformat.compress.codec':
                                'org.apache.hadoop.io.compress.BZip2Codec'}),
        ]

if __name__ == '__main__':
    CCStatsCountJob.run()
