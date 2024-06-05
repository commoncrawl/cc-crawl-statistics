Basic Statistics of Common Crawl Monthly Archives
=================================================

Analyze the [Common Crawl](https://commoncrawl.org/) data to get metrics about the monthly crawl archives:
* size of the monthly crawls, number of
  * fetched pages
  * unique URLs
  * unique documents (by content digest)
  * number of different hosts, domains, top-level domains
* distribution of pages/URLs on hosts, domains, top-level domains
* and ...
  * mime types
  * protocols / schemes (http vs. https)
  * content languages (since summer 2018)

This is a description how to generate the statistics from the Common Crawl URL index files.

The results are presented on https://commoncrawl.github.io/cc-crawl-statistics/.


Step 1: Count Items
-------------------

The items (URLs, hosts, domains, etc.) are counted using the Common Crawl index files
on AWS S3 `s3://commoncrawl/cc-index/collections/*/indexes/cdx-*.gz`.

1. define a pattern of cdx files to process - usually from one monthly crawl (here: `CC-MAIN-2016-26`)
   - either smaller set of local files for testing
   ```
   INPUT="test/cdx/cdx-0000[0-3].gz"
   ```
   - or one monthly crawl to be accessed via Hadoop on AWS S3:
   ```
   INPUT="s3a://commoncrawl/cc-index/collections/CC-MAIN-2016-26/indexes/cdx-*.gz"
   ```

2. run `crawlstats.py --job=count` to process the cdx files and count the items:
   ```
   python3 crawlstats.py --job=count --no-exact-counts \
        --no-output --output-dir .../count/ $INPUT
   ```

Help on command-line parameters (including [mrjob](https://pypi.org/project/mrjob/) options) are shown by
`python3 crawlstats.py --help`.
The option `--no-exact-counts` is recommended (and is the default) to save storage space and computation time
when counting URLs and content digests.


Step 2: Aggregate Counts
------------------------

Run `crawlstats.py --job=stats` on the output of step 1:
```
python3 crawlstats.py --job=stats --max-top-hosts-domains=500 \
     --no-output --output-dir .../stats/ .../count/
```
The max. number of most frequent thosts and domains contained in the output is set by the option
`--max-top-hosts-domains=N`.


Step 3: Download the Data
-------------------------

In order to prepare the plots, the the output of step 2 must be downloaded to local disk.
Simplest, the data is fetched from the Common Crawl Public Data Set bucket on AWS S3:
```sh
while read crawl; do
    aws s3 cp s3://commoncrawl/crawl-analysis/$crawl/stats/part-00000.gz ./stats/$crawl.gz
done <<EOF
CC-MAIN-2008-2009
...
EOF
```

One aggregated, gzip-compressed statistics file, is about 1 MiB in size. So you could just run
[get_stats.sh](get_stats.sh) to download the data files for all released monthly crawls.

Also the output of step 1 is provided on `s3://commoncrawl/`. The counts for every crawl is hold
in 10 bzip2-compressed files, together 1 GiB per crawl in average. To download the counts for one crawl:
- if you're on AWS and [AWS CLI]() is installed and configured
  ```sh
  CRAWL=CC-MAIN-2022-05
  aws s3 cp --recursive s3://commoncrawl/crawl-analysis/$CRAWL/count stats/count/$CRAWL
  ```
- otherwise
  ```sh
  CRAWL=CC-MAIN-2022-05
  mkdir -p stats/count/$CRAWL
  for i in $(seq 0 9); do
    curl https://data.commoncrawl.org/crawl-analysis/$CRAWL/count/part-0000$i.bz2 \
      >stats/count/$CRAWL/part-0000$i.bz2
  done
  ```


Step 4: Plot the Data
---------------------

To prepare the plots using the downloaded aggregated data:
```
gzip -dc stats/CC-MAIN-*.gz | python3 plot/crawl_size.py
```
The full list of commands to prepare all plots is found in [plot.sh](plot.sh). Don't forget to install the Python
modules [required for plotting](requirements_plot.txt).


Step 5: Local Site Preview
--------------------------

The [crawl statistics site](https://commoncrawl.github.io/cc-crawl-statistics/) is hosted by [Github pages](https://pages.github.com/). The site is updated as soon as plots or description texts are updated, committed and pushed to the Github repository.

To preview local changes, it's possible to serve the site locally:
1. build the Docker image with Ruby, Jekyll and the content to be served
   ```
   docker build -f site.Dockerfile -t cc-crawl-statistics-site:latest .
   ```
2. run a Docker container to serve the site preview
   ```
   docker run --network=host --rm -ti cc-crawl-statistics-site:latest
   ```
   The site should be served on localhost, port 4000 (http://127.0.0.1:4000).
   If not, the correct location is shown in the output of the `docker run` command.


Related Projects
----------------

The [columnar index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/)
simplifies counting and analytics a lot - easier to maintain, more transparent, reproducible and
extensible than running two MapReduce jobs, see the the list of example
- [SQL queries](https://github.com/commoncrawl/cc-index-table#query-the-table-in-amazon-athena) and
- [Jupyter notebooks](https://github.com/commoncrawl/cc-notebooks)

