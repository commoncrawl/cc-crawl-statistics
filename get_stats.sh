#!/bin/bash

set -o pipefail

if aws s3 ls s3://commoncrawl/crawl-analysis/ | sed -E 's@.* @@; s@/$@@' >./stats/crawls.txt; then
    ON_AWS=true;
    echo "Running on AWS (AWS CLI configured for authenticated access)"
else
    # extracting list of crawls from Python enum definition
    grep -Eo 'CC-MAIN-20[0-9][0-9]-[0-9]+' crawlstats.py | sort -u >./stats/crawls.txt
    ON_AWS=false
fi

while read crawl; do
    echo $crawl
    if [ -e stats/$crawl.gz ]; then
        echo "  ... exists"
        continue
    fi
    if $ON_AWS; then
        aws s3 cp s3://commoncrawl/crawl-analysis/$crawl/stats/part-00000.gz ./stats/$crawl.gz
    else
        curl --silent https://data.commoncrawl.org/crawl-analysis/$crawl/stats/part-00000.gz >./stats/$crawl.gz
    fi
done <./stats/crawls.txt
