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
    # use minimal theme with white background set in plot constructor
    # https://ggplot2.tidyverse.org/reference/ggtheme.html
    GGPLOT2_THEME = ggplot2.theme_minimal(base_size=11)

    GGPLOT2_THEME_KWARGS = {
        'panel.background': ggplot2.element_rect(fill='white', color='white'),
        'plot.background': ggplot2.element_rect(fill='white', color='white')
    }
    # GGPLOT2_THEME = ggplot2.theme_grey()


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

    def line_plot(self, data, title, ylabel, img_file,
                  x='date', y='size', c='type', clabel='', ratio=1.0):
        if PLOTLIB == 'ggplot':
            # date_label = "%Y\n%b"
            date_label = "%Y\n%W"  # year + week number
            p = ggplot(data,
                       aes(x=x, y=y, color=c)) \
                + ggtitle(title) \
                + ylab(ylabel) \
                + xlab(' ') \
                + scale_x_date(breaks=date_breaks('3 months'),
                               labels=date_label) \
                + geom_line() + geom_point()
        elif PLOTLIB == 'rpy2.ggplot2':
            # convert y axis to float because R uses 32-bit signed integers,
            # values >= 2 bln. (2^31) will overflow
            data[y] = data[y].astype(float)
            if y != 'size' and 'size' in data.columns:
                data['size'] = data['size'].astype(float)
            p = ggplot2.ggplot(data) \
                + ggplot2.aes_string(x=x, y=y, color=c) \
                + ggplot2.geom_line(linewidth=.2) + ggplot2.geom_point() \
                + GGPLOT2_THEME \
                + ggplot2.theme(**{'legend.position': 'bottom',
                                   'aspect.ratio': ratio,
                                   **GGPLOT2_THEME_KWARGS}) \
                + ggplot2.labs(title=title, x='', y=ylabel, color=clabel)
        img_path = os.path.join(PLOTDIR, img_file)
        p.save(img_path)
        # data.to_csv(img_path + '.csv')
        return p
