#!/bin/bash

set -exo pipefail

LATEST_CRAWL=$(basename $(ls stats/CC-MAIN-201*.gz | tail -n 1) .gz)

function update_json() {
    regex="$1"
    excerpt="$2"
    if [ -e "$excerpt" ]; then
        if ! zgrep -qF "$LATEST_CRAWL" $excerpt; then
            zgrep -Eh "$regex" stats/$LATEST_CRAWL.gz | gzip >>$excerpt
        fi
    else
        zcat stats/CC-MAIN-*.gz | grep -Eh "$regex" | gzip  >$excerpt
    fi
}

# filter data to speed-up reading while plotting
update_json '^\["size'                               stats/excerpt/size.json.gz
update_json '^\["histogram"'                         stats/excerpt/histogram.json.gz
update_json '^\["tld"'                               stats/excerpt/tld.json.gz
update_json '^\["(size|mimetype)"'                   stats/excerpt/mimetype.json.gz
update_json '^\["(size|charset)"'                    stats/excerpt/charset.json.gz
update_json '^\["(size|primary_language|languages)"' stats/excerpt/language.json.gz

zcat stats/excerpt/size.json.gz \
     | python3 plot/crawl_size.py

zcat stats/excerpt/size.json.gz \
     | python3 plot/overlap.py

zcat stats/excerpt/histogram.json.gz \
    | python3 plot/histogram.py "$LATEST_CRAWL"

(cat stats/crawler/CC-MAIN-*.json;
 zgrep -E '"CC-MAIN-201(6-[^0][0-9]|[789]-)' stats/excerpt/size.json.gz | grep '^\["size"') \
	| python3 plot/crawler_metrics.py

zcat stats/excerpt/tld.json.gz \
    | python3 plot/tld.py CC-MAIN-2016-07 CC-MAIN-2017-04 CC-MAIN-2018-05 $LATEST_CRAWL

zcat stats/excerpt/mimetype.json.gz \
    | python3 plot/mimetype.py

zcat stats/excerpt/charset.json.gz \
    | python3 plot/charset.py

zcat stats/excerpt/language.json.gz \
    | python3 plot/language.py
