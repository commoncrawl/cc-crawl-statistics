import os
import pandas
import re
import types

from collections import defaultdict
from hyperloglog import HyperLogLog


from crawlplot import CrawlPlot

from crawlstats import CST, CrawlStatsJSONDecoder, HYPERLOGLOG_ERROR,\
    MonthlyCrawl


class CrawlSizePlot(CrawlPlot):

    def __init__(self):
        super().__init__()

        self.size = defaultdict(dict)
        self.size_by_type = defaultdict(dict)
        self.type_index = defaultdict(dict)
        self.crawls = {}
        self.ncrawls = 0
        self.hll = defaultdict(dict)
        self.N = 0
        self.sum_counts = False

    def add(self, key, val):
        cst = CST[key[0]]
        if cst not in (CST.size, CST.size_estimate):
            return
        item_type = key[1]
        crawl = key[2]
        count = 0
        if cst == CST.size_estimate:
            item_type = ' '.join([item_type, 'estim.'])
            hll = CrawlStatsJSONDecoder.json_decode_hyperloglog(val)
            count = len(hll)
            self.hll[item_type][crawl] = hll
        elif cst == CST.size:
            count = val
        self.add_by_type(crawl, item_type, count)

    def add_by_type(self, crawl, item_type, count):
        if crawl not in self.crawls:
            self.crawls[crawl] = self.ncrawls
            self.size['crawl'][self.ncrawls] = crawl
            date = pandas.Timestamp(MonthlyCrawl.date_of(crawl))
            self.size['date'][self.ncrawls] = date
            self.ncrawls += 1
        else:
            date = self.size['date'][self.crawls[crawl]]
        if item_type in self.size and \
                self.crawls[crawl] in self.size[item_type]:
            # add count to existing record?
            if self.sum_counts:
                count += self.size[item_type][self.crawls[crawl]]
                self.size[item_type][self.crawls[crawl]] = count
                _N = self.type_index[item_type][self.crawls[crawl]]
                self.size_by_type['size'][_N] = count
            return
        self.size[item_type][self.crawls[crawl]] = count
        self.size_by_type['crawl'][self.N] = crawl
        self.size_by_type['date'][self.N] = date
        self.size_by_type['type'][self.N] = item_type
        self.size_by_type['size'][self.N] = count
        self.type_index[item_type][self.crawls[crawl]] = self.N
        self.N += 1

    def cumulative_size(self):
        latest_n_crawls_cumul = [2, 3, 4, 6, 9, 12]
        total_pages = 0
        sorted_crawls = sorted(self.crawls)
        for crawl in sorted_crawls:
            total_pages += self.size['page'][self.crawls[crawl]]
            self.add_by_type(crawl, 'page cumul.', total_pages)
        urls_cumul = defaultdict(dict)
        for item_type in self.hll.keys():
            item_type_cumul = ' '.join([item_type, 'cumul.'])
            item_type_new = ' '.join([item_type, 'new'])
            cumul_hll = HyperLogLog(HYPERLOGLOG_ERROR)
            n = 0
            hlls = []
            for crawl in sorted(self.hll[item_type]):
                n += 1
                hll = self.hll[item_type][crawl]
                last_cumul_hll_len = len(cumul_hll)
                cumul_hll.update(hll)
                # cumulative size
                self.add_by_type(crawl, item_type_cumul, len(cumul_hll))
                # new unseen items this crawl (since the first analyzed crawl)
                unseen = (len(cumul_hll) - last_cumul_hll_len)
                if unseen > len(hll):
                    # 1% error rate for cumulative HLLs is large in comparison
                    # to crawl size, adjust to size of items in this crawl
                    # (there can be no more new items than the size of the crawl)
                    unseen = len(hll)
                self.add_by_type(crawl, item_type_new, unseen)
                hlls.append(hll)
                # cumulative size for last N crawls
                for n_crawls in latest_n_crawls_cumul:
                    item_type_n_crawls = '{} cumul. last {} crawls'.format(
                        item_type, n_crawls)
                    if n_crawls <= len(hlls):
                        cum_hll = HyperLogLog(HYPERLOGLOG_ERROR)
                        for i in range(1, (n_crawls+1)):
                            if i > len(hlls):
                                break
                            cum_hll.update(hlls[-i])
                        size_last_n = len(cum_hll)
                        if item_type == 'url estim.':
                            urls_cumul[crawl][str(n_crawls)] = size_last_n
                    else:
                        size_last_n = 'nan'
                    self.add_by_type(crawl, item_type_n_crawls, size_last_n)
        for n, crawl in enumerate(sorted_crawls):
            for n_crawls in latest_n_crawls_cumul:
                if n_crawls > (n+1):
                    self.add_by_type(crawl,
                                     'page cumul. last {} crawls'.format(n_crawls),
                                     'nan')
                    continue
                cumul_pages = 0
                for c in sorted_crawls[(1+n-n_crawls):(n+1)]:
                    cumul_pages += self.size['page'][self.crawls[c]]
                self.add_by_type(crawl,
                                 'page cumul. last {} crawls'.format(n_crawls),
                                 cumul_pages)
                urls_cumul[crawl][str(n_crawls)] = urls_cumul[crawl][str(n_crawls)]/cumul_pages
        for crawl in urls_cumul:
            for n_crawls in urls_cumul[crawl]:
                self.add_by_type(crawl,
                                 'URLs/pages last {} crawls'.format(n_crawls),
                                 urls_cumul[crawl][n_crawls])

    def transform_data(self):
        self.size = pandas.DataFrame(self.size)
        self.size_by_type = pandas.DataFrame(self.size_by_type)

    def save_data(self):
        self.size.to_csv('data/crawlsize.csv')
        self.size_by_type.to_csv('data/crawlsizebytype.csv')

    def duplicate_ratio(self):
        # -- duplicate ratio
        data = self.size[['crawl', 'page', 'url', 'digest estim.']]
        data['1-(urls/pages)'] = 100 * (1.0 - (data['url'] / data['page']))
        data['1-(digests/pages)'] = \
            100 * (1.0 - (data['digest estim.'] / data['page']))
        floatf = '{0:.1f}%'.format
        print(data.to_string(formatters={'1-(urls/pages)': floatf,
                                         '1-(digests/pages)': floatf}),
              file=open('data/crawlduplicates.txt', 'w'))

    def plot(self):
        # -- size per crawl (pages, URL and content digest)
        row_types = ['page', 'url',  # 'url estim.',
                     'digest estim.']
        self.size_plot(self.size_by_type, row_types, '',
                       'Crawl Size', 'Pages / Unique Items',
                       'crawlsize/monthly.png',
                       data_export_csv='crawlsize/monthly.csv')
        # -- cumulative size
        row_types = ['page cumul.', 'url estim. cumul.',
                     'digest estim. cumul.']
        self.size_plot(self.size_by_type, row_types, r' cumul\.$',
                       'Crawl Size Cumulative',
                       'Pages / Unique Items Cumulative',
                       'crawlsize/cumulative.png',
                       data_export_csv='crawlsize/cumulative.csv')
        # -- new URLs per crawl
        row_types = ['url estim. new']
        self.size_plot(self.size_by_type, row_types, '',
                       'New URLs per Crawl (not observed in prior crawls)',
                       'New URLs', 'crawlsize/monthly_new.png',
                       data_export_csv='crawlsize/monthly_new.csv')
        # -- cumulative URLs over last N crawls (this and preceding N-1 crawls)
        row_types = ['url', '1 crawl',  # 'url' replaced by '1 crawl'
                     'url estim. cumul. last 2 crawls',
                     'url estim. cumul. last 3 crawls',
                     'url estim. cumul. last 4 crawls',
                     'url estim. cumul. last 6 crawls',
                     'url estim. cumul. last 9 crawls',
                     'url estim. cumul. last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='url', value='1 crawl', inplace=True)
        self.size_plot(data, row_types, r'^url estim\. cumul\. last | crawls?$',
                       'URLs Cumulative Over Last N Crawls',
                       'Unique URLs cumulative',
                       'crawlsize/url_last_n_crawls.png',
                       clabel='n crawls',
                       data_export_csv='crawlsize/url_last_n_crawls.csv')
        # -- ratio unique URLs by total page captures over last N crawls (this and preceding N-1 crawls)
        row_types = ['URLs/pages last 2 crawls',
                     'URLs/pages last 3 crawls',
                     'URLs/pages last 4 crawls',
                     'URLs/pages last 6 crawls',
                     'URLs/pages last 9 crawls',
                     'URLs/pages last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='url', value='1 crawl', inplace=True)
        self.size_plot(data, row_types, r'^URLs/pages last | crawls?$',
                       'Ratio Unique URLs / Total Pages Captured Over Last N Crawls',
                       'URLs/Pages',
                       'crawlsize/url_page_ratio_last_n_crawls.png',
                       clabel='n crawls',
                       data_export_csv='crawlsize/url_page_ratio_last_n_crawls.csv')
        # -- cumul. digests over last N crawls (this and preceding N-1 crawls)
        row_types = ['digest estim.', '1 crawl',  # 'url' replaced by '1 crawl'
                     'digest estim. cumul. last 2 crawls',
                     'digest estim. cumul. last 3 crawls',
                     'digest estim. cumul. last 6 crawls',
                     'digest estim. cumul. last 12 crawls']
        data = self.size_by_type
        data = data[data['type'].isin(row_types)]
        data.replace(to_replace='digest estim.', value='1 crawl', inplace=True)
        self.size_plot(data, row_types,
                       r'^digest estim\. cumul\. last | crawls?$',
                       'Content Digest Cumulative Over Last N Crawls',
                       'Unique content digests cumulative',
                       'crawlsize/digest_last_n_crawls.png',
                       clabel='n crawls')
        # -- URLs, hosts, domains, tlds (normalized)
        data = self.size_by_type
        row_types = ['url', 'tld', 'domain', 'host']
        data = data[data['type'].isin(row_types)]
        self.export_csv(data, 'crawlsize/domain.csv')
        # --- domains only (not yet normalized)
        self.size_plot(data[data['type'].isin(['domain'])], '', '',
                       'Unique Domains per Crawl',
                       '', 'crawlsize/registered-domains.png')
        # normalize scale (exponent) of counts so that they fit on one plot
        size_norm = data['size'] / 1000.0
        data['size'] = size_norm.where(data['type'] == 'tld',
                                       other=data['size'])
        data.replace(to_replace='tld', value='tld e+04', inplace=True)
        size_norm = size_norm / 10000.0
        data['size'] = size_norm.where(data['type'] == 'host',
                                       other=data['size'])
        data.replace(to_replace='host', value='host e+07', inplace=True)
        data['size'] = size_norm.where(data['type'] == 'domain',
                                       other=data['size'])
        data.replace(to_replace='domain', value='domain e+07', inplace=True)
        size_norm = size_norm / 100.0
        data['size'] = size_norm.where(data.type == 'url',
                                       other=data['size'])
        data.replace(to_replace='url', value='url e+09', inplace=True)
        self.size_plot(data, '', '',
                       'URLs / Hosts / Domains / TLDs per Crawl',
                       'Unique Items', 'crawlsize/domain.png')
        # -- URL status by year:
        # --   duplicates (pages - URLs), known URLs (URLs - new), new URLs
        data = self.size[['crawl', 'page', 'url', 'url estim. new']]
        data['year'] = data['crawl'].apply(lambda c: int(MonthlyCrawl.year_of(c)))
        by_year = data[['year', 'page', 'url', 'url estim. new']] \
            .groupby('year').agg(sum).reset_index()
        by_year['revisit'] = by_year['url'] - by_year['url estim. new']
        by_year['duplicate'] = by_year['page'] - by_year['url']
        by_year['new'] = by_year['url estim. new']
        print('URL status by year:')
        print(by_year)
        by_year_by_type = by_year[['year', 'new', 'revisit', 'duplicate', 'page']].melt(
            id_vars=['year', 'page'],
            value_vars=['new', 'revisit', 'duplicate'],
            var_name='url_status', value_name='page_captures')
        by_year_by_type['ratio'] = by_year_by_type['page_captures'] / by_year_by_type['page']
        by_year_by_type['perc'] = by_year_by_type['ratio'].apply(lambda x: round((100.0*x), 1)).astype(str) + '%'
        by_year_by_type['year'] = pandas.Categorical(by_year_by_type['year'], ordered=True)
        by_year_by_type['url_status'] = pandas.Categorical(by_year_by_type['url_status'],
                                                           ordered=True,
                                                           categories=['duplicate',
                                                                       'revisit', 'new'])
        by_year_by_type['page_captures'] = by_year_by_type['page_captures'].astype(float)

        # url_status_by_year
        img_path = os.path.join(self.PLOTDIR, 'crawlsize', 'url_status_by_year.png')

        if self.PLOTLIB == "rpy2.ggplot2":
            return self.plot_with_rpy2_ggplot2(by_year_by_type, img_path)
        elif self.PLOTLIB == "matplotlib":
            return self.plot_with_matplotlib(by_year_by_type, img_path)
        else:
            raise ValueError("Invalid PLOTLIB")
        
    def plot_with_rpy2_ggplot2(self, by_year_by_type, img_path):
        from rpy2.robjects.lib import ggplot2
        from rpy2 import robjects
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()

        p = ggplot2.ggplot(by_year_by_type) \
            + ggplot2.aes_string(x='year', y='page_captures', fill='url_status', label='perc') \
            + ggplot2.geom_bar(stat='identity', position='stack') \
            + ggplot2.geom_text(
                data=by_year_by_type[
                    by_year_by_type['url_status'].isin(['new'])
                    & ~by_year_by_type['year'].isin(by_year_by_type['year'].tolist()[0:3])],
                color='black', size=2,
                position=ggplot2.position_dodge(width=.5)) \
            + self.GGPLOT2_THEME \
            + ggplot2.scale_fill_manual(values=robjects.r('c("duplicate"="#00BA38", "revisit"="#619CFF", "new"="#F8766D")')) \
            + ggplot2.theme(**{'legend.position': 'right',
                            'aspect.ratio': .7,
                            **self.GGPLOT2_THEME_KWARGS},
                            **{'axis.text.x':
                            ggplot2.element_text(angle=45, size=10,
                                                    vjust=1, hjust=1)}) \
            + ggplot2.labs(title='Number of Page Captures', x='', y='', fill='URL status')
        p.save(img_path)

        return p


    def plot_with_matplotlib(self, by_year_by_type, img_path):
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.ticker import MultipleLocator, FormatStrFormatter

        # Create figure with specified aspect ratio
        aspect_ratio = 0.7
        title_fontsize = 12
        title_pad = 20
        ylabel_fontsize = 11
        bar_label_fontsize = 5
        ticks_fontsize = 9
        legend_fontsize = 10
        legend_title_fontsize = 11
        title = 'Number of Page Captures'

        fig, ax = plt.subplots(figsize=(self.DEFAULT_FIGSIZE, self.DEFAULT_FIGSIZE * aspect_ratio))

        # Prepare data for stacked bar chart
        years = by_year_by_type['year'].unique()
        # url_statuses = ['duplicate', 'revisit', 'new']
        url_statuses = ['new',  'revisit', 'duplicate',]

        colors = {
            'duplicate': '#00BA38', 
            'revisit': '#619CFF', 
            'new':   '#F8766D',
        }

        # Create stacked bars
        bottoms = np.zeros(len(years))
        bars = {}

        # Stacked bars from bottom to top
        for status in url_statuses:
            status_data = by_year_by_type[by_year_by_type['url_status'] == status]
            values = []
            labels = []

            for year in years:
                year_data = status_data[status_data['year'] == year]
                if len(year_data) > 0:
                    values.append(year_data['page_captures'].iloc[0])
                    labels.append(year_data['perc'].iloc[0])
                else:
                    values.append(0)
                    labels.append('')

            bars[status] = ax.bar(range(len(years)), values, bottom=bottoms,
                                color=colors[status], label=status, width=0.8)

            # Add text labels only for 'new' status, excluding first 3 years
            if status == 'new':
                for i, (bar, label) in enumerate(zip(bars[status], labels)):
                    if i >= 3 and label:  # Skip first 3 years
                        height = bar.get_height()

                        ax.text(bar.get_x() + bar.get_width() / 2.,
                            bottoms[i] + height,
                            label, ha='center', va='top',
                            color='black', fontsize=bar_label_fontsize)

            bottoms += values

        # Set labels and title
        ax.set_title(title, fontsize=title_fontsize, fontweight='normal',
                    pad=title_pad, loc='left')
        
        ax.set_xlabel('', fontsize=24)
        ax.set_ylabel('', fontsize=24)

        # Format x-axis
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years, rotation=45, ha='right', va='top', fontsize=ticks_fontsize)

        ax.set_xlim(-0.5, len(years) - 0.5)  # Remove x-axis padding

        # data min/max after plotting
        ymin, ymax = ax.get_ylim()

        # set specific ticks  (like ggplot2)
        minor = self.nice_tick_step(ymin, ymax, n=8)       # more grid lines
        major = 2 * minor                        # label every second one

        ax.yaxis.set_minor_locator(MultipleLocator(minor))
        ax.yaxis.set_major_locator(MultipleLocator(major))

        if ymax > 1e4:
            # scientific notation for large y values
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.0e'))

        grid_linewidth = 0.8

        ax.grid(True, which='minor', linewidth=grid_linewidth, color='#E6E6E6', zorder=0, axis='both')
        ax.grid(True, which='major', linewidth=grid_linewidth, color='#E6E6E6', zorder=0, axis='x')
        ax.grid(True, which='major', linewidth=grid_linewidth, color='#E6E6E6', zorder=0, axis='y')

        ax.set_axisbelow(True)

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Set tick colors
        ax.tick_params(axis='y', which='both', colors='#FFFFFF', length=8, width=grid_linewidth, labelsize=ticks_fontsize)
        ax.tick_params(axis='x', which='both', colors='#E6E6E6', length=8, width=grid_linewidth, labelsize=ticks_fontsize)
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')

        # Position legend on right side with reversed order
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(handles[::-1], labels[::-1], loc='center left', bbox_to_anchor=(1.0, 0.5),
                frameon=False, fontsize=legend_fontsize, title='URL status', title_fontsize=legend_title_fontsize)
        legend._legend_box.align = 'left'  # Align legend title to the left

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(img_path, dpi=self.DEFAULT_DPI, bbox_inches='tight', facecolor='white')
        plt.close()

        return fig


    def export_csv(self, data, csv):
        if csv is not None:
            data.reset_index().pivot(index='crawl',
                                     columns='type', values='size').to_csv(
                                         os.path.join(self.PLOTDIR, csv))

    def norm_data(self, data, row_filter, type_name_norm):
        if len(row_filter) > 0:
            data = data[data['type'].isin(row_filter)]
        if type_name_norm != '':
            for value in row_filter:
                replacement = value
                if isinstance(type_name_norm, str):
                    if re.search(type_name_norm, value):
                        while re.search(type_name_norm, replacement):
                            replacement = re.sub(type_name_norm,
                                                 '', replacement)
                elif isinstance(type_name_norm, types.FunctionType):
                    replacement = type_name_norm(value)
                if replacement != value:
                    data.replace(to_replace=value, value=replacement,
                                 inplace=True)
        return data

    def size_plot(self, data, row_filter, type_name_norm,
                  title, ylabel, img_file, clabel='', data_export_csv=None,
                  x='date', y='size', c='type'):
        # return
    
        data = self.norm_data(data, row_filter, type_name_norm)
        print(data)
        self.export_csv(data, data_export_csv)
        return self.line_plot(data, title, ylabel, img_file,
                              x=x, y=y, c=c, clabel=clabel, ratio=.9)


if __name__ == '__main__':
    plot = CrawlSizePlot()
    plot.read_from_stdin_or_file()
    plot.cumulative_size()
    plot.transform_data()
    plot.save_data()
    plot.duplicate_ratio()
    plot.plot()
