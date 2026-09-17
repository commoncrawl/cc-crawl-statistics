#!/bin/bash

set -o pipefail

TOP_DOMAINS_SOURCE=domains-top-1000-extended.csv
TOP_DOMAINS_TARGET_EXTENSION=domains-top-1000.csv
TOP_DOMAINS_FOLDER=./stats/top-domains

if aws s3 ls s3://commoncrawl/crawl-analysis/ | sed -E 's@.* @@; s@/$@@' >./stats/crawls.txt; then
    ON_AWS=true;
    echo "Running on AWS (AWS CLI configured for authenticated access)"
else
    echo "Downloading from https://data.commoncrawl.org/ using curl"
    # list of crawls enumerated in crawlstats.py
    python3 -c 'from crawlstats import MonthlyCrawl; [print(c) for c in sorted(MonthlyCrawl.by_name.keys())]' >./stats/crawls.txt
    ON_AWS=false
fi

mkdir -p ${TOP_DOMAINS_FOLDER}

while read crawl; do
    echo $crawl
    if [ -e stats/$crawl.gz ]; then
        echo "  ... stats exist"
    elif $ON_AWS; then
        aws s3 cp s3://commoncrawl/crawl-analysis/$crawl/stats/part-00000.gz ./stats/$crawl.gz
    else
        curl --silent https://data.commoncrawl.org/crawl-analysis/$crawl/stats/part-00000.gz >./stats/$crawl.gz
    fi
    # top-domains csv might be missing for older crawls, in that case continue without failing
    TOP_DOMAINS_TARGET=${TOP_DOMAINS_FOLDER}/${crawl}.${TOP_DOMAINS_TARGET_EXTENSION}
    if [ -e ${TOP_DOMAINS_TARGET} ]; then
        echo "  ... top-domains exist"
    elif $ON_AWS; then
        aws s3 cp s3://commoncrawl/crawl-analysis/$crawl/stats/${TOP_DOMAINS_SOURCE} ${TOP_DOMAINS_TARGET}
    else
        curl --silent --fail https://data.commoncrawl.org/crawl-analysis/$crawl/stats/${TOP_DOMAINS_SOURCE} -o ${TOP_DOMAINS_TARGET} || rm -f ${TOP_DOMAINS_TARGET}
    fi
done <./stats/crawls.txt
