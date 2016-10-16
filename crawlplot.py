import json
import logging
import os.path

PLOTLIB = 'rpy2.ggplot2'
PLOTDIR = 'plots'

if PLOTLIB == 'ggplot':
    from ggplot import *
elif PLOTLIB == 'rpy2.ggplot2':
    from rpy2.robjects.lib import ggplot2
    from rpy2.robjects import pandas2ri
    pandas2ri.activate()


class CrawlPlot:

    def read_data(self, stream):
        for line in stream:
            keyval = line.split('\t')
            if len(keyval) == 2:
                key = json.loads(keyval[0])
                val = json.loads(keyval[1])
                self.add(key, val)
            else:
                logging.error("Not a key-value pair: {}".find(line))

    def line_plot(self, data, title, ylabel, img_file):
        if PLOTLIB == 'ggplot':
            # date_label = "%Y\n%b"
            date_label = "%Y\n%W"  # year + week number
            p = ggplot(data,
                       aes(x='date', y='size', color='type')) \
                + ggtitle(title) \
                + ylab(ylabel) \
                + xlab(' ') \
                + scale_x_date(breaks=date_breaks('3 months'),
                               labels=date_label) \
                + geom_line() + geom_point()
        elif PLOTLIB == 'rpy2.ggplot2':
            # convert size to float because R uses 32-bit signed integers,
            # values > 2 bln. (2^31) will overflow
            data['size'] = data['size'].astype(float)
            p = ggplot2.ggplot(data) \
                + ggplot2.aes_string(x='date', y='size', color='type') \
                + ggplot2.geom_line() + ggplot2.geom_point() \
                + ggplot2.labs(title=title, x='', y=ylabel, color='')
        img_path = os.path.join(PLOTDIR, img_file)
        p.save(img_path)
        # data.to_csv(img_path + '.csv')
        return p
