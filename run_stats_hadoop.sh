#!/bin/bash

CRAWL="$1"

if [ -z "$CRAWL" ]; then
    echo "Usage: $0 <CRAWL-YEAR-WEEK>"
    echo "  Argument indicating year and week of crawl (e.g., 2016-40) to be processed required"
    exit 1
elif [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "AWS credentials must passed to Boto via environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY!"
    exit 1
fi


OUTPUT_COUNT=ccstats/$CRAWL/count/
OUTPUT_STATS=ccstats/$CRAWL/stats/

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


for i in `seq 0 299`; do
    echo s3://commoncrawl/cc-index/collections/CC-MAIN-$CRAWL/indexes/cdx-`printf %05d $i`.gz
done >input-$CRAWL.txt

hadoop fs -mkdir -p ccstats/$CRAWL/
hadoop fs -put -f input-$CRAWL.txt ccstats/$CRAWL/input.txt

HADOOP_USER=${HADOOP_USER:-$USER}


LOGLEVEL="info"


python3 crawlstats.py --job=count \
        --logging-level=$LOGLEVEL \
        --no-exact-counts \
        --cmdenv AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
        --cmdenv AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
        -r hadoop \
        --jobconf "mapreduce.map.memory.mb=720" \
        --jobconf "mapreduce.map.java.opts=-Xmx512m" \
        --jobconf "mapreduce.reduce.memory.mb=640" \
        --jobconf "mapreduce.reduce.java.opts=-Xmx512m" \
        --jobconf "mapreduce.output.fileoutputformat.compress=true" \
        --output-dir hdfs:///user/$HADOOP_USER/$OUTPUT_COUNT \
        --no-output \
        --cleanup NONE \
        hdfs:///user/$HADOOP_USER/ccstats/$CRAWL/input.txt \
    2>&1 | tee cc-stats.$CRAWL.count.log
# Note: if tasks fail frequently while fetching the cdx-* files from S3,
#       check and increase Boto http_socket_timeout, cf.
#       http://boto.cloudhackers.com/en/latest/boto_config_tut.html

#for i in `seq 0 9`; do
#    hadoop distcp ccstats/$CRAWL/count/part-0000$i.bz2 s3a://commoncrawl/crawl-analysis/CC-MAIN-$CRAWL/count/part-0000$i.bz2
#done
hadoop distcp ccstats/$CRAWL/count s3a://commoncrawl/crawl-analysis/CC-MAIN-$CRAWL/count


python3 crawlstats.py --job=stats \
        --logging-level=$LOGLEVEL \
        --max-top-hosts-domains=500 \
        --min-urls-top-host-domain=100 \
        --cmdenv AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
        --cmdenv AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
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
