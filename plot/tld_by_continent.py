import json
import os.path
import sys

from collections import defaultdict, Counter

import pandas

from rpy2.robjects.lib import ggplot2

from crawlplot import PLOTDIR, GGPLOT2_THEME
from crawlstats import MonthlyCrawl, MultiCount
from top_level_domain import TopLevelDomain


d = defaultdict(lambda: defaultdict(list))
dd = defaultdict(lambda: defaultdict(list))
tld_counts = defaultdict(lambda: Counter())

# mapping of country-code TLDs to continents
continent_cc_tlds = {
    'Africa': {'ao', 'bf', 'bi', 'bj', 'bw', 'cd', 'cf', 'cg', 'ci', 'cm', 'cv',
               'dj', 'dz', 'eg', 'eh', 'er', 'et', 'ga', 'gh', 'gm', 'gn', 'gq',
               'gw', 'ke', 'km', 'lr', 'ls', 'ly', 'ma', 'mg', 'ml', 'mr', 'mu',
               'mw', 'mz', 'na', 'ne', 'ng', 're', 'rw', 'sc', 'sd', 'sh', 'sl',
               'sn', 'so', 'ss', 'st', 'sz', 'td', 'tg', 'tn', 'tz', 'ug', 'yt',
               'za', 'zm', 'zw'},
    'Antarctica': {'aq'},
    'Asia': {'ae', 'af', 'am', 'az', 'bd', 'bh', 'bn', 'bt', 'cc', 'cn', 'cx',
             'ge', 'hk', 'id', 'il', 'in', 'io', 'iq', 'ir', 'jo', 'jp', 'kg',
             'kh', 'kp', 'kr', 'kw', 'kz', 'la', 'lb', 'lk', 'mm', 'mn', 'mo',
             'mv', 'my', 'np', 'om', 'ph', 'pk', 'ps', 'qa', 'sa', 'sg', 'sy',
             'th', 'tj', 'tm', 'tr', 'tw', 'uz', 'vn', 'ye',
             'tp' # Timor-Leste: deleted in favor of .tl in 2015
             },
    'Europe': {'ad', 'al', 'at', 'ba', 'be', 'bg', 'by', 'ch', 'cy', 'cz',
               'de', 'dk', 'ee', 'es', 'fi', 'fo', 'fr', 'gg', 'gi', 'gr',
               'hr', 'hu', 'ie', 'im', 'is', 'it', 'je', 'li', 'lt', 'lu', 'lv',
               'mc', 'md', 'me', 'mk', 'mt', 'nl', 'no',
               'pl', 'pt', 'ro', 'rs', 'ru', 'se', 'si', 'sj', 'sk', 'sm',
               'ua', 'uk', 'va',
               'xk',  # https://en.wikipedia.org/wiki/.xk
               'bv', # Bouvet Island (inactive, uninhabited Norwegian territory, South Atlantic Ocean)
               'gb' # Great Britain (reserved)
               },
    'North America': {'ag', 'ai', 'an', 'aw', 'bb', 'bm', 'bs', 'bz',
                      'ca', 'cr', 'cu', 'cw', 'dm', 'do', 'gd', 'gl', 'gp', 'gt',
                      'hn', 'ht', 'jm', 'kn', 'ky', 'lc', 'mq',     'ms', 'mx', 'ni',
                      'pa', 'pm', 'pr', 'sv', 'sx', 'tc', 'tt',
                      'us', 'vc', 'vg', 'vi',
                      'bl', # Saint Barthélemy (unused)
                      'bq', # Bonaire, Sint Eustatius and Saba (reserved)
                      'mf', # Saint Martin (unassigned)
                      },
    'Oceania': {'as', 'au', 'ck', 'fj', 'fm', 'gu', 'ki', 'mh', 'mp',
                'nc', 'nf', 'nr', 'nu', 'nz', 'pf', 'pg', 'pn', 'pw',
                'sb', 'tk', 'tl', 'to', 'tv', 'vu', 'wf', 'ws'
                },
    'South America': {'ar', 'bo', 'br', 'cl', 'co', 'ec', 'fk', 'gf', 'gy',
                      'pe', 'py', 'sr', 'uy', 've'},
}

# Geographic TLDs mapped to continents
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Geographic_top-level_domains
continent_geographic_tlds = {
    'Africa': {'africa', 'capetown', 'durban', 'joburg'},
    'Asia': {'abudhabi', 'arab', 'asia', 'doha', 'dubai', 'krd', 'kyoto',
             'nagoya', 'okinawa', 'osaka', 'ryukyu', 'taipei', 'tokyo', 'yokohama',
             # https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Internationalized_geographic_top-level_domains
             'xn--1qqw23a', '佛山', # Foshan, China
             'xn--xhq521b', '广东', # Guangdong, China
             'xn--80adxhks', 'москва', # Moscow, Russia
             'xn--p1acf', 'рус', # Russian language and culture - https://en.wikipedia.org/wiki/.%D1%80%D1%83%D1%81
             'xn--mgbca7dzdo', 'ابوظبي', # Abu Dhabi
             'xn--ngbrx', 'عرب', # Arab
             },
    'Europe': {
        # France
        'alsace', 'bzh', 'corsica', 'eus', 'paris',
        # Spain
        'bcn', 'barcelona', 'cat', 'eus', 'gal', 'madrid',
        # Germany
        'bayern', 'berlin', 'cologne', 'koeln', 'hamburg', 'nrw', 'ruhr', 'saarland',
        # other
        'eu', 'amsterdam', 'bar', 'brussels', 'cymru', 'wales', 'frl', 'gent', 'helsinki', 'irish', 'ist', 'istanbul', 'london', 'moscow', 'scot', 'stockholm', 'swiss', 'tatar', 'tirol', 'vlaanderen', 'wien', 'zuerich', 'su',
        # https://en.wikipedia.org/wiki/.ax
        'ax'
    },
    'North America': {'boston', 'miami', 'nyc', 'quebec', 'vegas'},
    'Oceania': {'kiwi', 'melbourne', 'sydney'},
    'South America': {'lat', 'rio'}
}

# list of "continents" to be shown in the output
continents = ['(other)', 'com,net', 'org', 'edu', 'gov,mil', 'North America', 'South America', 'Oceania', 'Africa', 'Asia', 'Europe']

# lookup tables TLD -> continent
tld_continent = {
    'gov': 'gov,mil', 'mil': 'gov,mil',
    'com': 'com,net', 'net': 'com,net',
    'org': 'org', 'edu': 'edu'
}

# frequency counts of TLDs that cannot be mapped to a continent
tld_unmapped = Counter()

# fill the lookup table with TLD -> continent mappings
for continent in continent_cc_tlds:
    for tld in continent_cc_tlds[continent]:
        tld_continent[tld] = continent

for continent in continent_geographic_tlds:
    for tld in continent_geographic_tlds[continent]:
        tld_continent[tld] = continent

for icctld in TopLevelDomain.tld_ccs:
    if TopLevelDomain.tld_ccs[icctld] in tld_continent:
        tld_continent[icctld] = tld_continent[TopLevelDomain.tld_ccs[icctld]]

def tld2continent(tld):
    continent = '(other)'
    tld = tld.lower()
    if tld in tld_continent and tld_continent[tld] != 'Antarctica':
        continent = tld_continent[tld]
    return continent

if __name__ == '__main__':
    for line in sys.stdin:
        keyval = line.split('\t')
        if len(keyval) == 2:
            [_, suffix, crawl] = json.loads(keyval[0])
            year = MonthlyCrawl.year_of(crawl)
            val = json.loads(keyval[1])
            tld = suffix.split('.')[-1].lower()
            tld_cnt = tld2continent(tld)
            if tld_cnt == '(other)':
                tld_unmapped[tld] += MultiCount.get_count(0, val)
            if tld:
                # print(tld)
                tld_counts['(any)'][tld] += MultiCount.get_count(0, val)
                tld_counts[str(year)][tld] += MultiCount.get_count(0, val)
            d[str(year)][tld_cnt].append(val)
            dd[MonthlyCrawl.short_name(crawl)][tld_cnt].append(val)

    print("\nyear\t{}".format("\t".join(continents)))
    continent_percentages = dict()
    for year in d:
        pages = dict()
        total = 0
        values = []
        for tld in continents:
            d[year][tld].append([0,0,0,0])
            val = MultiCount.sum_values(d[year][tld], False)
            total += val[0]
            values.append(val[0])
            # print("{}\t{}\t{}\t{}\t{}\t{}".format(year, tld, *val))
        percentages = [100*val/total for val in values]
        print("{}\t{}".format(year, "\t".join(
            map(lambda x: '{:.2f}'.format(x), percentages))))
        continent_percentages[year] = percentages
    continent_percentages = pandas.DataFrame.from_dict(continent_percentages,
                                                       orient='index',
                                                       columns=continents)
    continent_percentages.index.name = 'year'
    print(continent_percentages)

    top_tlds = tld_counts['(any)'].most_common(16)
    #print("\n", top_tlds)

    top_tlds_by_year = defaultdict(list)
    print("\nyear\t{}".format("\t".join([x[0] for x in top_tlds])))
    for year in tld_counts:
        total = sum(tld_counts[year].values())
        sys.stdout.write(year)
        for tld in top_tlds:
            perc = 100*tld_counts[year][tld[0]]/total
            sys.stdout.write('\t{:.2f}'.format(perc))
            top_tlds_by_year[year].append(perc)
        sys.stdout.write('\n')

    # table TLDs by year
    selected_tlds = pandas.DataFrame.from_dict(
        top_tlds_by_year,
        orient='index',
        columns=map(lambda tld: tld[0], top_tlds)
    )
    selected_tlds.index.name = 'year'
    selected_tlds.to_csv(
        os.path.join(PLOTDIR, 'tld', 'selected-tlds-by-year.csv'),
        index=True)
    css_classes = ['tablepercentage', 'tablesorter']
    selected_tlds.to_html(
        os.path.join(PLOTDIR, 'tld', 'selected-tlds-by-year.html'),
        float_format='%.2f',
        classes=css_classes,
        index_names=True)

    print("\ncrawl\t{}".format("\t".join(continents)))
    for crawl in dd:
        pages = dict()
        total = 0
        values = []
        for tld in continents:
            dd[crawl][tld].append([0,0,0,0])
            val = MultiCount.sum_values(dd[crawl][tld], False)
            total += val[0]
            values.append(val[0])
            # print("{}\t{}\t{}\t{}\t{}\t{}".format(year, tld, *val))
        print("{}\t{}".format(crawl, "\t".join(['{:.2f}'.format(100*val/total) for val in values])))

    # print unmapped TLDs to verify whether there are any TLDs
    # that need to be added to the mapping
    print("\n", len(tld_unmapped), " unmapped TLDs: ", str(tld_unmapped), "\n\n")


    data = continent_percentages.melt(id_vars=[], var_name='continent',
                                      value_name='perc', ignore_index=False)
    data['continent'] = pandas.Categorical(data['continent'],
                                           ordered=True,
                                           categories=continents.reverse())
    plot = ggplot2.ggplot(data.reset_index()) \
            + ggplot2.aes_string(x='year', y='perc', fill='continent', label='perc') \
            + ggplot2.geom_bar(stat='identity', position='stack') \
            + GGPLOT2_THEME + ggplot2.scale_fill_hue() \
            + ggplot2.labs(title='Percentage of Page Captures per TLD / Continent',
                           x='', y='Percentage', fill='TLD / Continent') \
            + ggplot2.theme(**{'legend.position': 'right',
                               'aspect.ratio': .7,
                               'panel.background': ggplot2.element_rect(fill='white', color='white'),
                               'plot.background': ggplot2.element_rect(fill='white', color='white'),
                               'axis.text.x':
                                ggplot2.element_text(angle=45,
                                                     vjust=1, hjust=1)})
    plot.save(os.path.join(PLOTDIR, 'tld', 'tlds-by-year-and-continent.png'))
    ### plot and table for print publication
    #plot = plot + ggplot2.labs(title='',
    #                           x='', y='', fill='TLD / Continent') \
    #            + ggplot2.theme()
    #plot.save(os.path.join(PLOTDIR, 'tld', 'tlds-by-year-and-continent.pdf'))
    #print(continent_percentages.to_latex(index=True, float_format='%.2f'))
    continent_percentages.to_csv(
        os.path.join(PLOTDIR, 'tld', 'tlds-by-year-and-continent.csv'),
        index=True)
    css_classes = ['tablepercentage', 'tablesorter']
    continent_percentages.to_html(
        os.path.join(PLOTDIR, 'tld', 'tlds-by-year-and-continent.html'),
        float_format='%.2f',
        classes=css_classes)

