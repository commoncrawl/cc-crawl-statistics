Crawler-Related Metrics
=======================

Crawler-related metrics are extracted from the crawler log files, cf. [../stats/crawler/](https://github.com/commoncrawl/cc-crawl-statistics/blob/master/stats/crawler/) and include
- the size of the URL database (CrawlDb)
- the fetch list size (number of URLs scheduled for fetching)
- the response status of the fetch:
  - success
  - redirect
  - denied (forbidden by HTTP 403 or robots.txt)
  - failed (404, host not found, etc.)
- usage of http/https URL protocols (schemes)

The first plot shows absolute number for the metrics.

![Crawler metrics](./crawler/metrics.png)

The relative portion of the fetch status is shown in the second graphics.

![Percentage of fetch status](./crawler/fetch_status_percentage.png)

The next figure shows the relative usage of http and https URL protocols (schemes). The increasing usage HTTPS on the web is reflected. But also crawler properties such as sampling, deduplication and URL canonicalization) may influence the actual amount of HTTPS URLs in a single monthly crawl.

![Percentage of HTTP vs. HTTPS URLs](./crawler/url_protocols_percentage.png)
