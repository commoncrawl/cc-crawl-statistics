import sys

from plot.mimetype import MimeTypeStats
from crawlstats import CST, MonthlyCrawl


class MimeTypeDetectedStats(MimeTypeStats):

    def __init__(self):
        super().__init__()
        self.MAX_TYPE_VALUES = MimeTypeStats.MAX_MIME_TYPES

    def norm_value(self, mimetype):
        return mimetype

    def add(self, key, val):
        self.add_check_type(key, val, CST.mimetype_detected)


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    plot_name = 'mimetypes_detected'
    column_header = 'mimetype_detected'
    if len(plot_crawls) == 0:
        plot_crawls = MonthlyCrawl.get_latest(3)
        print(plot_crawls)
    else:
        plot_name += '-' + '-'.join(plot_crawls)
    plot = MimeTypeDetectedStats()
    plot.read_from_stdin_or_file()
    plot.transform_data(MimeTypeStats.MAX_MIME_TYPES,
                        MimeTypeStats.MIN_AVERAGE_COUNT,
                        None)
    plot.save_data_percentage(plot_name, dir_name='plots', type_name='mimetype_detected')
    plot.plot(plot_crawls, plot_name, column_header, ['tablesearcher'])
