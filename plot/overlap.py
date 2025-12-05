import copy
import os.path
import pandas
import sys

from collections import defaultdict

from crawlstats import CST, CrawlStatsJSONDecoder, MonthlyCrawl

from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri

import pygraphviz

from crawlplot import CrawlPlot, PLOTDIR, GGPLOT2_THEME, GGPLOT2_THEME_KWARGS

pandas2ri.activate()


class CrawlOverlap(CrawlPlot):

    MAX_MATRIX_SIZE = 30

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
                        = [intersection, union, size1, size2,
                           (intersection/size2), jaccard_sim]
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
        print(data)
        # select median of similarity values as midpoint of similarity scale
        midpoint = data['similarity'].median()
        decimals = 3
        textsize = 2
        minshown = .0005
        if (data['similarity'].max()-data['similarity'].min()) > .2:
            decimals = 2
            textsize = 2.8
            minshown = .005
        data['sim_rounded'] = data['sim_rounded'].apply(
            lambda x: ('{0:.'+str(decimals)+'f}').format(x).lstrip('0')
            if x >= minshown else '0')
        print('Median of similarities for', item_type, '=', midpoint)
        matrix_size = len(self.similarity[item_type])
        if matrix_size > self.MAX_MATRIX_SIZE:
            n = 0
            for crawl1 in sorted(self.similarity[item_type], reverse=True):
                short_name = MonthlyCrawl.short_name(crawl1)
                if n > self.MAX_MATRIX_SIZE:
                    data = data[data['crawl1'] != short_name]
                    data = data[data['crawl2'] != short_name]
                n += 1
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
                                                    vjust=1, hjust=1),
                               **GGPLOT2_THEME_KWARGS}) \
            + ggplot2.labs(title=title, x='', y='') \
            + ggplot2.geom_text(color='black', size=textsize)
        img_path = os.path.join(PLOTDIR, image_file)
        p.save(img_path)

        ### matplotlib version
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
        from crawlplot import MATPLOTLIB_PATH_SUFFIX

        # Pivot data to create matrix
        pivot_data = data.pivot(index='crawl1', columns='crawl2', values='similarity')

        # Create figure with square aspect ratio
        matrix_size = len(pivot_data)
        fig_size = max(10, matrix_size * 0.8)  # Scale with matrix size
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))

        # Create color map: red (low) -> white (mid) -> blue (high)
        # ggplot2 uses these exact color names: "red", "white", "blue"
        colors = [(1.0, 0.0, 0.0),    # red
                  (1.0, 1.0, 1.0),    # white
                  (0.0, 0.0, 1.0)]    # blue
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('red_white_blue', colors, N=n_bins)

        # Use TwoSlopeNorm to center white at the midpoint
        norm = TwoSlopeNorm(vmin=data['similarity'].min(),
                           vcenter=midpoint,
                           vmax=data['similarity'].max())

        # Add grey grid lines behind everything
        ax.set_axisbelow(True)
        ax.grid(True, which='major', linewidth=0.8, color='#E6E6E6', zorder=-1)

        # Create heatmap with origin='lower' to match ggplot2 (bottom-up)
        # Set zorder=1 to draw heatmap above the white grid
        im = ax.imshow(pivot_data.values, cmap=cmap, norm=norm, aspect='equal', origin='lower', zorder=1)

        # Add text annotations (on top of everything with zorder=2)
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                similarity = pivot_data.iloc[i, j]
                # Skip NaN values
                if pandas.isna(similarity):
                    continue

                # Draw white rectangle border around each cell with zorder=1 after the heatmap
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                    fill=False, edgecolor='white', linewidth=2, zorder=1)
                ax.add_patch(rect)


                # Get the rounded text for this cell
                matching_rows = data[(data['crawl1'] == pivot_data.index[i]) &
                                    (data['crawl2'] == pivot_data.columns[j])]
                if len(matching_rows) > 0:
                    text_val = matching_rows['sim_rounded'].iloc[0]
                    # Cell text should be 80% of axis tick font size (12 * 0.8 = 9.6)
                    ax.text(j, i, text_val, ha='center', va='center',
                           color='black', fontsize=28, zorder=2)

        # Set ticks and labels
        ax.set_xticks(np.arange(len(pivot_data.columns)))
        ax.set_yticks(np.arange(len(pivot_data.index)))
        ax.set_xticklabels(pivot_data.columns, fontsize=30)
        ax.set_yticklabels(pivot_data.index, fontsize=30)

        # Set tick colors
        ax.tick_params(axis='both', which='both', colors='#FFFFFF', zorder=0)

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')

        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', va='top')

        # Set title
        ax.set_title(title, fontsize=36, fontweight='normal', pad=20, loc='left')
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Add colorbar - max 30% of plot height, centered vertically
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, shrink=0.3)
        cbar.ax.set_title('similarity', fontsize=30, pad=20)

        # Apply ggplot2-like styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # White background
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(img_path + MATPLOTLIB_PATH_SUFFIX, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        ###

        return p


if __name__ == '__main__':
    plot = CrawlOverlap()
    plot.read_from_stdin_or_file()
    plot.fill_overlap_matrix()
    plot.save_overlap_matrix()
    # plot.plot_similarity_graph()
    plot.plot_similarity_matrix(
        'url', 'crawloverlap/crawlsimilarity_matrix_url.png',
        'URL overlap between crawls (Jaccard similarity)')
    plot.plot_similarity_matrix(
        'digest', 'crawloverlap/crawlsimilarity_matrix_digest.png',
        'Content overlap between crawls (Jaccard similarity on digest)')
