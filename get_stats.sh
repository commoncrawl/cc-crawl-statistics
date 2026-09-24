#!/bin/bash

# Download crawl statistics and top-domains csv files into ./stats/
#
# Usage: ./get_stats.sh
# Test:  Override TOP_DOMAINS_S3/URL, eg.
#        TOP_DOMAINS_S3=s3://test-bucket/test-prefix/crawl-analysis ./get_stats.sh


set -o pipefail

TOP_DOMAINS_FILE=domains-top-1000-extended.csv.gz
TOP_DOMAINS_FOLDER=./stats/top-domains

CRAWL_ANALYSIS_S3=s3://commoncrawl/crawl-analysis
CRAWL_ANALYSIS_URL=https://data.commoncrawl.org/crawl-analysis

# Override to test, see above.
TOP_DOMAINS_S3=${TOP_DOMAINS_S3:-$CRAWL_ANALYSIS_S3}
TOP_DOMAINS_URL=${TOP_DOMAINS_URL:-$CRAWL_ANALYSIS_URL}


if aws s3 ls ${CRAWL_ANALYSIS_S3}/ | sed -E 's@.* @@; s@/$@@' >./stats/crawls.txt; then
    ON_AWS=true;
    echo "Running on AWS (AWS CLI configured for authenticated access)"
else
    echo "Downloading from ${CRAWL_ANALYSIS_URL} using curl"
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
        aws s3 cp ${CRAWL_ANALYSIS_S3}/$crawl/stats/part-00000.gz ./stats/$crawl.gz
    else
        curl --silent ${CRAWL_ANALYSIS_URL}/$crawl/stats/part-00000.gz >./stats/$crawl.gz
    fi
    # top-domains csv might be missing for older crawls, in that case continue without failing
    TOP_DOMAINS_TARGET=${TOP_DOMAINS_FOLDER}/${crawl}.${TOP_DOMAINS_FILE}
    if [ -e ${TOP_DOMAINS_TARGET} ]; then
        echo "  ... top-domains exist"
    elif $ON_AWS; then
        aws s3 cp ${TOP_DOMAINS_S3}/$crawl/stats/${TOP_DOMAINS_FILE} ${TOP_DOMAINS_TARGET}
    else
        curl --silent --fail ${TOP_DOMAINS_URL}/$crawl/stats/${TOP_DOMAINS_FILE} -o ${TOP_DOMAINS_TARGET} || { rm -f ${TOP_DOMAINS_TARGET}; false; }
    fi
done <./stats/crawls.txt
