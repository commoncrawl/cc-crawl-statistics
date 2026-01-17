import re
import sys

from plot.table import TabularStats
from crawlstats import CST, MonthlyCrawl


class MimeTypeStats(TabularStats):

    MIN_AVERAGE_COUNT = 500
    MAX_MIME_TYPES = 100

    # see https://en.wikipedia.org/wiki/Media_type#Naming
    mime_pattern_str = \
        r'(?:x-)?[a-z]+/[a-z0-9]+' \
        r'(?:[.-](?:c\+\+[a-z]*|[a-z0-9]+))*(?:\+[a-z0-9]+)?'
    mime_pattern = re.compile(r'^'+mime_pattern_str+r'$')
    mime_extract_pattern = re.compile(r'^\s*(?:content\s*=\s*)?["\']?\s*(' +
                                      mime_pattern_str +
                                      r')(?:\s*[;,].*)?\s*["\']?\s*$')

    def __init__(self):
        super().__init__()
        self.MAX_TYPE_VALUES = MimeTypeStats.MAX_MIME_TYPES

    def norm_value(self, mimetype):
        if type(mimetype) is str:
            mimetype = mimetype.lower()
            m = MimeTypeStats.mime_extract_pattern.match(mimetype)
            if m:
                return m.group(1)
            return mimetype.strip('"\', \t')
        return ""

    def add(self, key, val):
        self.add_check_type(key, val, CST.mimetype)


if __name__ == '__main__':
    plot_crawls = sys.argv[1:]
    plot_name = 'mimetypes'
    column_header = 'mimetype'
    if len(plot_crawls) == 0:
        plot_crawls = MonthlyCrawl.get_latest(3)
        print(plot_crawls)
    else:
        plot_name += '-' + '-'.join(plot_crawls)
    plot = MimeTypeStats()
    plot.read_from_stdin_or_file()
    plot.transform_data(MimeTypeStats.MAX_MIME_TYPES,
                        MimeTypeStats.MIN_AVERAGE_COUNT,
                        MimeTypeStats.mime_pattern)
    plot.save_data_percentage(plot_name, dir_name='plots', type_name='mimetype')
    plot.plot(plot_crawls, plot_name, column_header, ['tablesearcher'])
