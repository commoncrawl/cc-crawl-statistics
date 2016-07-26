from crawlstats import MonthlyCrawl, MonthlyCrawlSet
from crawlstats import CrawlStatsJSONDecoder, CrawlStatsJSONEncoder
from crawlstats import CST
from crawlstats import MultiCount
from hyperloglog import HyperLogLog
import json
import jsonpickle

crawl1 = MonthlyCrawl.get_by_name('CC-MAIN-2014-52')
crawl2 = MonthlyCrawl.get_by_name('CC-MAIN-2015-06')
crawl3 = MonthlyCrawl.get_by_name('CC-MAIN-2016-26')


def test_monthly_crawl():
    assert(crawl1 != crawl2)
    assert(crawl1 < crawl2)
    assert('{}'.format(crawl1) == json.dumps(crawl1))
    assert('CC-MAIN-2014-52' == MonthlyCrawl.to_name(crawl1))


def test_monthly_crawl_set():
    crawls = MonthlyCrawlSet()
    assert('0' == json.dumps(crawls, cls=CrawlStatsJSONEncoder))

    # add crawl 1 - CC-MAIN-2014-52
    crawls.add(crawl1)
    assert(crawl1 in crawls)
    assert('1' == json.dumps(crawls, cls=CrawlStatsJSONEncoder))
    assert(crawls.is_newest(crawl1))

    # add crawl 2 - CC-MAIN-2015-06
    crawls.add(crawl2)
    assert(crawl2 in crawls)
    assert(crawls.is_newest(crawl2))
    assert(not crawls.is_newest(crawl1))

    # create second crawl set and add crawl 3 - CC-MAIN-2016-26
    crawls2 = MonthlyCrawlSet()
    crawls2.add(crawl3)
    assert(crawl3 in crawls2)

    # merge the two crawl sets
    crawls.update(crawls2)
    assert(crawl3 in crawls)
    assert(3 == len(crawls))

    # check iterator over crawl set
    for crawl in crawls.get_crawls():
        assert(crawl in crawls)
        assert((crawl == crawl1) or (crawl == crawl2) or (crawl == crawl3))
        crawl = MonthlyCrawl.to_name(crawl)
        assert((crawl == 'CC-MAIN-2014-52') or
               (crawl == 'CC-MAIN-2015-06') or
               (crawl == 'CC-MAIN-2016-26'))

    # check is_newest in merged crawl set
    assert(not crawls.is_newest(crawl2))
    assert(crawls.is_newest(crawl3))

    # check deletions from crawl set
    crawls.discard(crawl2)
    assert(crawl2 not in crawls)
    assert(crawl1 in crawls)

    # check is_new
    assert(not crawls.is_new(crawl2))
    assert(not crawls.is_new(crawl3))
    crawls.discard(crawl1)
    assert(crawls.is_new(crawl3))
    # although crawl2 is not in crawls there is no older crawl
    assert(crawls.is_new(crawl2))


def test_crawlstatstype():
    cst = CST.url
    assert(cst.value == CST.url.value)


def test_json_hyperloglog():
    hll1 = HyperLogLog(.01)
    for i in range(0, 50):
        hll1.add(i)
    jsons = json.dumps(hll1, cls=CrawlStatsJSONEncoder)
    hll2 = json.loads(jsons, cls=CrawlStatsJSONDecoder)
    assert(hll1.card() == hll2.card())
    # test jsonpickle serialization
    jsonp = jsonpickle.encode(hll2)
    hll3 = jsonpickle.decode(jsonp)
    assert(hll1.card() == hll3.card())


def test_multicount():
    cnt = MultiCount(2)
    cnt.incr('a', 1, 1)
    assert([1, 1] == cnt.get('a'))
    assert(1 == cnt.get_compressed('a'))
    cnt.incr('a', 2, 1)
    assert([3, 2] == cnt.get_compressed('a'))
    assert([3, 2] == MultiCount.sum_values(2, [[2, 1], 1]))
    assert([6, 4, 3] == MultiCount.sum_values(3, [[3, 2, 1], [2, 1], 1]))
    cnt.incr('b', *[2, 1])
