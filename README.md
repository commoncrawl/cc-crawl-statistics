Basic Statistics of Common Crawl Monthly Archives
=================================================

Analyze the [Common Crawl](http://commoncrawl.org/) to get some crawl statistics:
* size of the monthly crawls
  * fetched pages
  * unique URLs
  * unique documents (by content digets)
  * number of different hosts, domains, top-level domains
* distribution of pages/urls on hosts, domains, tlds
* and ...
  * mime types
  * protocols / schemes (http vs. https)


Step 1: Count Items
-------------------

The items (URLs, hosts, domains, etc.) are counted using the Common Crawl index files
on AWS S3 `s3://commoncrawl/cc-index/collections/*/indexes/cdx-*.gz`.

1. create a list of cdx files to process - usually from one monthly crawl (here: `CC-MAIN-2016-26`)
   but could be multiple crawls in one turn or also a subset for testing:
   ```
   for i in `seq 0 299`; do
        echo s3://commoncrawl/cc-index/collections/CC-MAIN-2016-26/indexes/cdx-`printf %05d $i`.gz
   done >input-2016-26.txt
   ``` 

2. run `crawlstats.py --job=count` to process the cdx files and count the items:
   ```
   python3 crawlstats.py --job=count --logging-level=info --no-exact-counts \
        --no-output --output-dir .../count/ .../input-2016-26.txt
   ```

Help on command-line parameters (including [mrjob](https://pythonhosted.org/mrjob/) options) are shown by
`python3 crawlstats.py --help`.
The option `--no-exact-counts` is recommended (and is the default) to save storage space and computation time
when URLs and content digests. 


Step 2: Aggregate Counts
------------------------

Run `crawlstats.py --job=stats` on the output of step 1:
```
python3 crawlstats.py --job=stats --logging-level=info --max-top-hosts-domains=500 \
     --no-output --output-dir .../stats/ .../count/
```
The max. number of most frequent thosts and domains contained in the output is set by the option
`--max-top-hosts-domains=N`.


Step 3: Plot the Data
---------------------

First, download the output of step 2 to local disk. Alternatively, fetch the data from the Common Crawl
Public Data Set bucket on AWS S3:
```
while read crawl; do
    aws s3 cp s3://commoncrawl/crawl-analysis/$crawl/stats/part-00000.gz ./stats/$crawl.gz
done <<EOF
CC-MAIN-2016-40
CC-MAIN-2016-36
CC-MAIN-2016-30
CC-MAIN-2016-26
CC-MAIN-2016-22
CC-MAIN-2016-18
CC-MAIN-2016-07
CC-MAIN-2015-48
CC-MAIN-2015-40
CC-MAIN-2015-35
CC-MAIN-2015-32
CC-MAIN-2015-27
CC-MAIN-2015-22
CC-MAIN-2015-18
CC-MAIN-2015-14
CC-MAIN-2015-11
CC-MAIN-2015-06
CC-MAIN-2014-52
EOF
```
To prepare the plots:
```
gzip -dc stats/CC-MAIN-*.gz | python3 plot_crawl_size.py
```
The full list of commands to prepare all plots is found in [plot.sh].
Also the plots are available, see [plots/].