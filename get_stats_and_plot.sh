#!/bin/bash
set -e

echo "Starting ..."

./get_stats.sh

# make sure plot directories exist
mkdir -p plots/crawler
mkdir -p plots/crawloverlap
mkdir -p plots/crawlsize
mkdir -p plots/throughput
mkdir -p plots/tld

./plot.sh

echo "Done."