#!/bin/bash

# filter data to speed-up reading while plotting
zgrep -h '^\["size'       stats/CC-MAIN-*.gz >stats/size.json
zgrep -h '^\["histogram"' stats/CC-MAIN-*.gz >stats/histogram.json
zgrep -h '^\["tld"'       stats/CC-MAIN-*.gz >stats/tld.json

python3 plot_crawl_size.py <stats/size.json

python3 plot_overlap.py    <stats/size.json

python3 plot_histogram.py  <stats/histogram.json

(cat stats/crawler/CC-MAIN-*.json; grep -E '"CC-MAIN-201(6-[^0][0-9]|[789]-)' stats/size.json) \
	| python3 plot_crawler_metrics.py

python3 plot_tld.py        <stats/tld.json
