---
layout: table
table_include:
 - selected-crawl-comparison-spearman-frequent-tlds.html
 - selected-crawl-comparison.html
table_sortlist: "{sortList: [[4,1]]}"
---

Estimation of Representativeness of a Recent Crawl
==================================================

The representativeness of the May 2017 crawl (CC-MAIN-2017-22) is estimated by a comparison with the frequency of top-level domains in

- the list of [top-1-million sites](http://s3.amazonaws.com/alexa-static/top-1m.csv.zip) published by [Alexa](https://support.alexa.com/hc/en-us/sections/200063274-Top-Sites), based on unique visitors and page views
- the [Cisco Umbrella Popularity list](http://s3-us-west-1.amazonaws.com/umbrella-static/index.html) which reflects DNS usage
- the [Majestic Million](http://downloads.majestic.com/majestic_million.csv), "[ordered by the number of referring subnets](https://blog.majestic.com/development/majestic-million-csv-daily/)"

All three lists have been fetched at the same time the crawl was performed. For the one million domains/sites in the lists the TLDs have been extracted, and for all TLDs the relative frequency has been calculated and compared to the relative frequency of pages, URLs, hosts and domains in the crawl.

The first table shows Spearman's rank correlation (*ρ*) for the 76 TLDs which cover at least 0.5% of the URLs.  The method is similar to [Sebastian Spiegler's analysis of the 2012 crawl archives](http://commoncrawl.org/2013/08/a-look-inside-common-crawls-210tb-2012-web-corpus/).  He reported *ρ* = 0.84 based on [W3Techs TLD usage statistics](https://w3techs.com/technologies/overview/top_level_domain/all) for comparison which were/are derived from the top Alexa sites.

As the three lists used for comparison have a different notion of popularity their correlation results differ.  There are also small differences between pages/URLs and hosts/domains.  It is an open question whether differences in the relative frequency by TLD are caused by Common Crawl's crawling strategy or a different average size of sites under various TLDs.



The second table shows the relative frequency per TLD for the lists and the recent crawl. The data in this tables was used to calculate the correlation matrix.