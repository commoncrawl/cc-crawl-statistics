import copy
import os.path
import pandas
import sys

from collections import defaultdict

from crawlstats import CST, CrawlStatsJSONDecoder, MonthlyCrawl

from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri

import pygraphviz

from crawlplot import CrawlPlot, PLOTDIR, GGPLOT2_THEME

pandas2ri.activate()


class CrawlOverlap(CrawlPlot):

    def __init__(self):
        self.crawl_size = defaultdict(dict)
        self.overlap = defaultdict(dict)
        self.similarity = defaultdict(dict)  # Jaccard index

    def add(self, key, val):
        cst = CST[key[0]]
        if cst != CST.size_estimate:
            return
        item_type = key[1]
        crawl = key[2]
        hll = CrawlStatsJSONDecoder.json_decode_hyperloglog(val)
        self.crawl_size[item_type][crawl] = hll

    def fill_overlap_matrix(self):
        for item_type in self.crawl_size:
            for crawl1 in self.crawl_size[item_type]:
                hll1 = self.crawl_size[item_type][crawl1]
                size1 = len(hll1)
                self.overlap[item_type][crawl1] = defaultdict(list)
                self.similarity[item_type][crawl1] = defaultdict(float)
                for crawl2 in self.crawl_size[item_type]:
                    if crawl1 >= crawl2:
                        continue
                    hll2 = self.crawl_size[item_type][crawl2]
                    size2 = len(hll2)
                    union_hll = copy.deepcopy(hll1)
                    union_hll.update(hll2)
                    union = len(union_hll)
                    intersection = size1 + size2 - union
                    jaccard_sim = intersection / union
                    self.overlap[item_type][crawl1][crawl2] \
                        = [intersection, union, size1, size2]
                    self.similarity[item_type][crawl1][crawl2] = jaccard_sim
                    # print(item_type, crawl1, crawl2, size1, size2, union,
                    #       intersection, jaccard_sim)

    def save_overlap_matrix(self):
        for item_type in self.overlap:
            data = pandas.DataFrame(self.similarity[item_type])
            data.to_csv('data/crawlsimilarity_' + item_type + '.csv')
            data = pandas.DataFrame(self.overlap[item_type])
            data.to_csv('data/crawloverlap_' + item_type + '.csv')

    def plot_similarity_graph(self, show_edges=False):
        '''(trial) visualize similarity using GraphViz'''
        g = pygraphviz.AGraph(directed=False, overlap='scale', splines=True)
        g.node_attr['shape'] = 'plaintext'
        g.node_attr['fontsize'] = '12'
        if show_edges:
            g.edge_attr['color'] = 'lightgrey'
            g.edge_attr['fontcolor'] = 'grey'
            g.edge_attr['fontsize'] = '8'
        else:
            g.edge_attr['style'] = 'invis'
        for crawl1 in sorted(self.similarity['url']):
            for crawl2 in sorted(self.similarity['url'][crawl1]):
                similarity = self.similarity['url'][crawl1][crawl2]
                distance = 1.0 - similarity
                g.add_edge(MonthlyCrawl.short_name(crawl1),
                           MonthlyCrawl.short_name(crawl2),
                           len=(distance),
                           label='{0:.2f}'.format(distance))
        g.write(os.path.join(PLOTDIR, 'crawlsimilarity_url.dot'))
        g.draw(os.path.join(PLOTDIR, 'crawlsimilarity_url.svg'), prog='fdp')

    def plot_similarity_matrix(self, item_type, image_file, title):
        '''Plot similarities of crawls (overlap of unique items)
        as heat map matrix'''
        data = defaultdict(dict)
        n = 1
        for crawl1 in self.similarity[item_type]:
            for crawl2 in self.similarity[item_type][crawl1]:
                similarity = self.similarity[item_type][crawl1][crawl2]
                data['crawl1'][n] = MonthlyCrawl.short_name(crawl1)
                data['crawl2'][n] = MonthlyCrawl.short_name(crawl2)
                data['similarity'][n] = similarity
                data['sim_rounded'][n] = similarity  # to be rounded
                n += 1
        data = pandas.DataFrame(data)
        # select median of similarity values as midpoint of similarity scale
        midpoint = data.similarity.median()
        decimals = 3
        textsize = 2
        minshown = .0005
        if (data.similarity.max()-data.similarity.min()) > .2:
            decimals = 2
            textsize = 3
            minshown = .005
        data.sim_rounded = data.sim_rounded.apply(
            lambda x: ('{0:.'+str(decimals)+'f}').format(x).lstrip('0')
            if x >= minshown else '0')
        print('Median of similarities for', item_type, '=', midpoint)
        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl2', y='crawl1',
                                 fill='similarity', label='sim_rounded') \
            + ggplot2.geom_tile(color="white") \
            + ggplot2.scale_fill_gradient2(low="red", high="blue", mid="white",
                                           midpoint=midpoint, space="Lab") \
            + GGPLOT2_THEME \
            + ggplot2.coord_fixed() \
            + ggplot2.theme(**{'axis.text.x':
                               ggplot2.element_text(angle=45,
                                                    vjust=1, hjust=1)}) \
            + ggplot2.labs(title=title, x='', y='') \
            + ggplot2.geom_text(color='black', size=textsize)
        img_path = os.path.join(PLOTDIR, image_file)
        p.save(img_path)
        return p

if __name__ == '__main__':
    plot = CrawlOverlap()
    plot.read_data(sys.stdin)
    plot.fill_overlap_matrix()
    plot.save_overlap_matrix()
    # plot.plot_similarity_graph()
    plot.plot_similarity_matrix(
        'url', 'crawlsimilarity_matrix_url.png',
        'URL overlap between crawls (Jaccard similarity)')
    plot.plot_similarity_matrix(
        'digest', 'crawlsimilarity_matrix_digest.png',
        'Content overlap between crawls (Jaccard similarity on digest)')
