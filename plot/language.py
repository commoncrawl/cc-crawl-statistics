import string
import sys

from plot.table import TabularStats
from crawlstats import CST, MonthlyCrawl


class LanguageStats(TabularStats):

    MIN_AVERAGE_COUNT = 500
    MAX_LANGUAGES = 200

    def __init__(self):
        super().__init__()
        self.MAX_TYPE_VALUES = LanguageStats.MAX_LANGUAGES

    def add(self, key, val):
        self.add_check_type(key, val, CST.primary_language)


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    plot_name = 'languages'
    column_header = 'language'
    if len(plot_crawls) == 0:
        plot_crawls = MonthlyCrawl.get_last(3)
        print(plot_crawls)
    else:
        plot_name += '-' + '-'.join(plot_crawls)
    plot = LanguageStats()
    plot.read_data(sys.stdin)
    plot.transform_data(LanguageStats.MAX_LANGUAGES,
                        LanguageStats.MIN_AVERAGE_COUNT,
                        None)
    plot.save_data(plot_name)
    plot.plot(plot_crawls, plot_name, column_header,
              ['iso639-3-language'])
