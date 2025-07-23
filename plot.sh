#!/bin/bash

N_CRAWLS=$(python3 -c 'from crawlstats import MonthlyCrawl; print(len(MonthlyCrawl.by_name))')
LATEST_CRAWL=$(python3 -c 'from crawlstats import MonthlyCrawl; print(sorted(MonthlyCrawl.by_name.keys())[-1])')

# verify that all stats files are downloaded, cf. get_stats.sh
N_CRAWLS_STATS_FILES=$(ls stats/CC-MAIN-*.gz | wc -l)
if [[ $N_CRAWLS -ne $N_CRAWLS_STATS_FILES ]]; then
    echo "Number of crawls registered in crawlstats.py ($N_CRAWLS) and"
    echo "the number of statistics files in stats/ ($N_CRAWLS_STATS_FILES) are not equal."
    echo "Exiting!"
    exit 1
fi

echo "Plotting crawl statistics for $N_CRAWLS crawls"
echo "Latest crawl is: $LATEST_CRAWL"
echo


# fail on any kind of error
set -exo pipefail


# register the latest crawl in the website configuration
sed -i 's@^latest_crawl:.*@latest_crawl: '$LATEST_CRAWL'@' _config.yml


function update_excerpt() {
    regex="$1"
    excerpt="$2"
    if [ -e "$excerpt" ]; then
        # short-cut for monthy update plots: only add data from latest crawl
        if ! zgrep -qF "$LATEST_CRAWL" $excerpt; then
            echo "Updating excerpt $excerpt with latest crawl $LATEST_CRAWL"
            zgrep -Eh "$regex" stats/$LATEST_CRAWL.gz | gzip >>$excerpt
        fi
        # sanity check: are all crawls excerpted?
        N_CRAWLS_EXCERPTED=$(zcat $excerpt | cut -f1 | jq -r '.[2]' | uniq | sort -u | wc -l)
        if [[ $N_CRAWLS_EXCERPTED -eq $N_CRAWLS ]]; then
            echo "Excerpt $excerpt includes $N_CRAWLS crawls as expected."
        else
            echo "Number of crawls excerpted in $excerpt ($N_CRAWLS_EXCERPTED) does not equal $N_CRAWLS"
            echo "Removing excerpt $excerpt"
            rm $excerpt
        fi
    fi
    if ! [ -e "$excerpt" ]; then
        echo "Rebuilding excerpt $excerpt"
        zcat stats/CC-MAIN-*.gz | grep -Eh "$regex" | gzip  >$excerpt
    fi
}

# filter data to speed-up reading while plotting
mkdir -p stats/excerpt
update_excerpt '^\["size'                               stats/excerpt/size.json.gz
update_excerpt '^\["histogram"'                         stats/excerpt/histogram.json.gz
update_excerpt '^\["tld"'                               stats/excerpt/tld.json.gz
update_excerpt '^\["(size|domain)"'                     stats/excerpt/domain.json.gz
update_excerpt '^\["(size", *"page|mimetype)"'          stats/excerpt/mimetype.json.gz
update_excerpt '^\["(size", *"page|mimetype_detected)"' stats/excerpt/mimetype_detected.json.gz
update_excerpt '^\["(size", *"page|charset)"'           stats/excerpt/charset.json.gz
update_excerpt '^\["(size", *"page|primary_language|languages)"' stats/excerpt/language.json.gz
update_excerpt '^\["scheme"'                            stats/excerpt/url_protocol.json.gz

mkdir -p data

zcat stats/excerpt/size.json.gz \
     | python3 plot/crawl_size.py

zcat stats/excerpt/size.json.gz \
     | python3 plot/overlap.py

# zcat stats/excerpt/histogram.json.gz \
#     | python3 plot/histogram.py "$LATEST_CRAWL"

(cat stats/crawler/CC-MAIN-*.json;
 zcat stats/excerpt/size.json.gz | grep '^\["size"';
 zcat stats/excerpt/url_protocol.json.gz) \
	| python3 plot/crawler_metrics.py

zcat stats/excerpt/tld.json.gz \
    | python3 plot/tld.py CC-MAIN-2008-2009 CC-MAIN-2012 CC-MAIN-2014-10 \
              CC-MAIN-2016-30 CC-MAIN-2019-09 CC-MAIN-2022-49 $LATEST_CRAWL

zcat stats/excerpt/mimetype.json.gz \
    | python3 plot/mimetype.py

zcat stats/excerpt/mimetype_detected.json.gz \
    | python3 plot/mimetype_detected.py

zcat stats/excerpt/charset.json.gz \
    | python3 plot/charset.py

zcat stats/excerpt/language.json.gz \
    | python3 plot/language.py

zcat stats/excerpt/domain.json.gz \
    | python3 plot/domain.py

echo -e "\n\nAll crawl statistics plotted\n"