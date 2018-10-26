import sys

from plot.table import TabularStats
from crawlstats import CST, MonthlyCrawl


class CharsetStats(TabularStats):

    MIN_AVERAGE_COUNT = 500
    MAX_CHARSETS = 100

    def __init__(self):
        super().__init__()
        self.MAX_TYPE_VALUES = CharsetStats.MAX_CHARSETS

    def add(self, key, val):
        self.add_check_type(key, val, CST.charset)


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    plot_name = 'charsets'
    column_header = 'charset'
    if len(plot_crawls) == 0:
        plot_crawls = MonthlyCrawl.get_last(3)
        print(plot_crawls)
    else:
        plot_name += '-' + '-'.join(plot_crawls)
    plot = CharsetStats()
    plot.read_data(sys.stdin)
    plot.transform_data(CharsetStats.MAX_CHARSETS,
                        CharsetStats.MIN_AVERAGE_COUNT,
                        None)
    plot.save_data(plot_name)
    plot.plot(plot_crawls, plot_name, column_header)
