#!/bin/bash

set -exo pipefail

LATEST_CRAWL=$(basename $(ls stats/CC-MAIN-201*.gz | tail -n 1) .gz)

function update_json() {
    regex="$1"
    excerpt="$2"
    if [ -e "$excerpt" ] && grep -qF "$LATEST_CRAWL" $excerpt; then
        zgrep -h "$regex" stats/$LATEST_CRAWL.gz  >>$excerpt
    else
        zcat stats/CC-MAIN-*.gz | grep -h "$regex" >$excerpt
    fi
}

# filter data to speed-up reading while plotting
update_json '^\["size'           stats/excerpt/size.json
update_json '^\["histogram"'     stats/excerpt/histogram.json
update_json '^\["tld"'           stats/excerpt/tld.json
update_json '^\["mimetype"'      stats/excerpt/mimetype.json
update_json '^\["charset"'       stats/excerpt/charset.json
update_json '^\["[^"]*language"' stats/excerpt/language.json

python3 plot/crawl_size.py <stats/excerpt/size.json

python3 plot/overlap.py    <stats/excerpt/size.json

python3 plot/histogram.py  <stats/excerpt/histogram.json

(cat stats/crawler/CC-MAIN-*.json; grep -E '"CC-MAIN-201(6-[^0][0-9]|[789]-)' stats/excerpt/size.json) \
	| python3 plot/crawler_metrics.py

python3 plot/tld.py CC-MAIN-2016-07 CC-MAIN-2017-04 CC-MAIN-2018-05 $LATEST_CRAWL <stats/excerpt/tld.json

python3 plot/mimetype.py <stats/excerpt/mimetype.json

python3 plot/charset.py  <stats/excerpt/charset.json
python3 plot/language.py <stats/excerpt/language.json
