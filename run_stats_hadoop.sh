#!/bin/bash

CRAWL="$1"

if [ -z "$CRAWL" ]; then
    echo "Usage: $0 <CRAWL-YEAR-WEEK>"
    echo "  Argument indicating year and week of crawl (e.g., 2016-40) to be processed required"
    exit 1
fi


OUTPUT_COUNT=ccstats/$CRAWL/count/
OUTPUT_STATS=ccstats/$CRAWL/stats/

hadoop fs -mkdir -p ccstats/$CRAWL/

# check that output paths do not exist (jobs will fail otherwise)
if hadoop fs -ls $OUTPUT_COUNT; then
    echo "Output path $OUTPUT_COUNT already exists: delete path before running the count job"
    exit 1
fi

if hadoop fs -ls $OUTPUT_STATS; then
    echo "Output path $OUTPUT_STATS already exists: delete path before running the stats job"
    exit 1
fi


set -e
set -x
set -o pipefail


INPUT="s3a://commoncrawl/cc-index/collections/CC-MAIN-$CRAWL/indexes/cdx-*.gz"

HADOOP_USER=${HADOOP_USER:-$USER}


LOGLEVEL="info"


python3 crawlstats.py --job=count \
        --logging-level=$LOGLEVEL \
        --no-exact-counts \
        -r hadoop \
        --jobconf "mapreduce.map.memory.mb=720" \
        --jobconf "mapreduce.map.java.opts=-Xmx512m" \
        --jobconf "mapreduce.reduce.memory.mb=640" \
        --jobconf "mapreduce.reduce.java.opts=-Xmx512m" \
        --jobconf "mapreduce.output.fileoutputformat.compress=true" \
        --output-dir hdfs:///user/$HADOOP_USER/$OUTPUT_COUNT \
        --no-output \
        --cleanup NONE \
        "$INPUT" \
    2>&1 | tee cc-stats.$CRAWL.count.log

#for i in `seq 0 9`; do
#    hadoop distcp ccstats/$CRAWL/count/part-0000$i.bz2 s3a://commoncrawl/crawl-analysis/CC-MAIN-$CRAWL/count/part-0000$i.bz2
#done
hadoop distcp ccstats/$CRAWL/count s3a://commoncrawl/crawl-analysis/CC-MAIN-$CRAWL/count


python3 crawlstats.py --job=stats \
        --logging-level=$LOGLEVEL \
        --max-top-hosts-domains=500 \
        --min-urls-top-host-domain=100 \
        -r hadoop \
        --jobconf "mapreduce.map.memory.mb=1200" \
        --jobconf "mapreduce.map.java.opts=-Xmx1024m" \
        --jobconf "mapreduce.reduce.memory.mb=1200" \
        --jobconf "mapreduce.reduce.java.opts=-Xmx1024m" \
        --jobconf "mapreduce.output.fileoutputformat.compress=true" \
        --no-output \
        --cleanup NONE \
        --output-dir hdfs:///user/$HADOOP_USER/$OUTPUT_STATS \
        hdfs:///user/$HADOOP_USER/$OUTPUT_COUNT \
    2>&1 | tee cc-stats.$CRAWL.stats.log

hadoop distcp ccstats/$CRAWL/stats/part-00000.gz s3a://commoncrawl/crawl-analysis/CC-MAIN-$CRAWL/stats/part-00000.gz
