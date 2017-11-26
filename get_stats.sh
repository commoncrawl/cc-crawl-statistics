#!/bin/bash

aws --no-sign-request s3 ls s3://commoncrawl/crawl-analysis/ | sed -E 's@.* @@; s@/$@@' \
 | while read crawl; do
    echo $crawl
    test -e stats/$crawl.gz && echo "  ... exists" && continue
    aws --no-sign-request s3 cp s3://commoncrawl/crawl-analysis/$crawl/stats/part-00000.gz ./stats/$crawl.gz
done
