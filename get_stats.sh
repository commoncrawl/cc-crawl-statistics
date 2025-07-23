#!/bin/bash

set -o pipefail

if aws s3 ls s3://commoncrawl/crawl-analysis/ | sed -E 's@.* @@; s@/$@@' >./stats/crawls.txt; then
    ON_AWS=true;
    echo "Running on AWS (AWS CLI configured for authenticated access)"
else
    echo "Downloading from https://data.commoncrawl.org/ using curl"
    # list of crawls enumerated in crawlstats.py
    python3 -c 'from crawlstats import MonthlyCrawl; [print(c) for c in sorted(MonthlyCrawl.by_name.keys())]' >./stats/crawls.txt
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
