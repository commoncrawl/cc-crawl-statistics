import heapq
import logging

from collections import defaultdict, Counter
from crawlstat import MonthlyCrawl
from crawlstat import CrawlStatsType as cst
from crawlstat import MultiCount

from mrjob.job import MRJob, MRStep
from mrjob.protocol import JSONProtocol

# maximum number of most frequent hosts or domains shown in final statistics
MAX_TOP_HOSTS_DOMAINS = 200


class CCStatsJob(MRJob):

    INPUT_PROTOCOL = JSONProtocol
    OUTPUT_PROTOCOL = JSONProtocol

    logging.basicConfig(format='%(asctime)s: [%(levelname)s]: %(message)s',
                        level=logging.DEBUG)

    def mapper(self, key, value):
        if key[0] in (cst.url.value, cst.digest.value):
            return
        yield key, value

    def reducer_init(self):
        self.counters = Counter()
        self.mostfrequent = defaultdict(list)

    def reducer(self, key, values):
        outputType = cst(key[0])
        item = key[1]
        crawl = MonthlyCrawl.to_name(key[2])
        if outputType in (cst.size, cst.new_items, cst.size_estimate):
            verbose_key = (outputType.name, cst(item).name, crawl)
            if outputType == cst.size:
                val = sum(values)
            elif outputType == cst.new_items:
                val = MultiCount.sum_values(2, values)
            elif outputType == cst.size_estimate:
                # already "reduced" in count job
                for val in values:
                    break
            yield verbose_key, val
        elif outputType == cst.dupl_histogram:
            yield((outputType.name, cst(item).name, crawl, key[3]),
                  MultiCount.sum_values(2, values))
        elif outputType in (cst.mimetype, cst.scheme, cst.surt_domain,
                            cst.tld, cst.domain, cst.host):
            item = key[1]
            mostfrequent = []
            for counts in values:
                self.counters[(cst.size.name, outputType.name, crawl)] += 1
                page_count = MultiCount.get_count(0, counts)
                url_count = MultiCount.get_count(1, counts)
                self.counters[(cst.histogram.name, outputType.name,
                               crawl, cst.page.name, page_count)] += 1
                self.counters[(cst.histogram.name, outputType.name,
                               crawl, cst.url.name, url_count)] += 1
                if outputType in (cst.domain, cst.host, cst.surt_domain):
                    # take most common
                    if len(mostfrequent) <= MAX_TOP_HOSTS_DOMAINS:
                        heapq.heappush(self.mostfrequent[(outputType.name,
                                                          crawl)],
                                       (page_count, url_count, item))
                    else:
                        heapq.heappushpop(self.mostfrequent[(outputType.name,
                                                             crawl)],
                                          (page_count, url_count, item))
                else:
                    yield((outputType.name, item, crawl),
                          MultiCount.compress(2, [page_count, url_count]))
        else:
            logging.error('Unhandled type {}\n'.format(outputType))
            raise

    def reducer_final(self):
        for (counter, count) in self.counters.items():
            yield counter, count
        for key, mostfrequent in self.mostfrequent.items():
            (outputType, crawl) = key
            for (page_count, url_count, item) in mostfrequent:
                yield((outputType, item, crawl),
                      MultiCount.compress(2, [page_count, url_count]))

    def steps(self):
        # -Dmapreduce.job.counters.limit=x
        # -Dmapreduce.job.counters.groups.max=y
        return [
            MRStep(mapper=self.mapper,
                   reducer_init=self.reducer_init,
                   reducer=self.reducer,
                   reducer_final=self.reducer_final,
                   jobconf={'mapreduce.job.reduces': 1,
                            'mapreduce.output.fileoutputformat.compress':
                                "true",
                            'mapreduce.output.fileoutputformat.compress.codec':
                                'org.apache.hadoop.io.compress.GzipCodec'})
        ]

if __name__ == '__main__':
    CCStatsJob.run()
