import copy
import os.path
import pandas

from collections import defaultdict

from crawlstats import CST, CrawlStatsJSONDecoder, MonthlyCrawl

import pygraphviz

from crawlplot import CrawlPlot


class CrawlOverlap(CrawlPlot):

    MAX_MATRIX_SIZE = 30

    def __init__(self):
        super().__init__()

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
        g.write(os.path.join(self.PLOTDIR, 'crawlsimilarity_url.dot'))
        g.draw(os.path.join(self.PLOTDIR, 'crawlsimilarity_url.svg'), prog='fdp')

    def plot_similarity_matrix_with_rpy2_ggplot2(self, data, midpoint, title, textsize, img_path):
        from rpy2.robjects.lib import ggplot2

        p = ggplot2.ggplot(data) \
            + ggplot2.aes_string(x='crawl2', y='crawl1',
                                fill='similarity', label='sim_rounded') \
            + ggplot2.geom_tile(color="white") \
            + ggplot2.scale_fill_gradient2(low="red", high="blue", mid="white",
                                        midpoint=midpoint, space="Lab") \
            + self.GGPLOT2_THEME \
            + ggplot2.coord_fixed() \
            + ggplot2.theme(**{'axis.text.x':
                            ggplot2.element_text(angle=45,
                                                    vjust=1, hjust=1),
                            **self.GGPLOT2_THEME_KWARGS}) \
            + ggplot2.labs(title=title, x='', y='') \
            + ggplot2.geom_text(color='black', size=textsize)

        p.save(img_path)
        return p
    
    def plot_similarity_matrix_with_matplotlib(self, data, decimals, title, cell_textsize, img_path):
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
        from matplotlib.colors import Normalize

        # Pivot data to create matrix
        pivot_data = data.pivot(index='crawl1', columns='crawl2', values='similarity')

        # Round the similarity values to match the displayed precision
        # This ensures cells with the same displayed value have the same color
        pivot_data_rounded = pivot_data.round(decimals)

        # Create figure with square aspect ratio
        # 7 inches * 300 DPI = 2100 pixels
        fig_size = self.DEFAULT_FIGSIZE
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))

        # Create color map: red (low) -> white (mid) -> blue (high)
        # ggplot2 uses these exact color names: "red", "white", "blue"
        vmin = pivot_data_rounded.min().min()
        vmax = pivot_data_rounded.max().max()

        if vmin < 0:
            # specific color map for negative values
            colors = [
                '#ff0801',
                '#ff6b48',
                '#ffa388',
                '#ffd2c4',
                '#fff4ef',
                '#FFFFFF',
                '#eadaff',
                '#c6a5ff',
                '#a073ff',
                '#6e43ff',
                '#4020ff',
                '#1306ff'
            ]
        else:
            colors = [
                '#fff4ef',
                '#FFFFFF',
                '#eadaff',
                '#c6a5ff',
                '#a073ff',
                '#6e43ff',
                '#4020ff',
                '#1306ff'
            ]
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('red_white_blue', colors, N=n_bins)

        # Use TwoSlopeNorm to center white at the midpoint
        # norm = TwoSlopeNorm(vmin=0,  # data['similarity'].min()
        #                 vcenter=midpoint,
        #                 vmax=data['similarity'].max())
        norm = Normalize(vmin=vmin,
                        vmax=vmax)
        
        # Add grey grid lines behind everything
        ax.set_axisbelow(True)
        ax.grid(True, which='major', linewidth=0.8, color='#E6E6E6', zorder=-1)

        # Create heatmap with origin='lower' to match ggplot2 (bottom-up)
        # Set zorder=1 to draw heatmap above the white grid
        # Use rounded data so cells with same displayed value have same color
        im = ax.imshow(pivot_data_rounded.values, cmap=cmap, norm=norm, aspect='equal', origin='lower', zorder=1)

        # Add text annotations (on top of everything with zorder=2)
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                similarity = pivot_data.iloc[i, j]
                # Skip NaN values
                if pandas.isna(similarity):
                    continue

                # Draw white rectangle border around each cell with zorder=1 after the heatmap
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                    fill=False, edgecolor='white', linewidth=0.5, zorder=1)
                ax.add_patch(rect)


                # Get the rounded text for this cell
                matching_rows = data[(data['crawl1'] == pivot_data.index[i]) &
                                    (data['crawl2'] == pivot_data.columns[j])]
                if len(matching_rows) > 0:
                    text_val = matching_rows['sim_rounded'].iloc[0]
                    # Cell text should be 80% of axis tick font size (12 * 0.8 = 9.6)
                    ax.text(j, i, text_val, ha='center', va='center',
                        color='black', fontsize=cell_textsize, zorder=2)

        # Set ticks and labels
        ax.set_xticks(np.arange(len(pivot_data.columns)))
        ax.set_yticks(np.arange(len(pivot_data.index)))
        ax.set_xticklabels(pivot_data.columns, fontsize=10)
        ax.set_yticklabels(pivot_data.index, fontsize=10)

        # Set tick colors
        ax.tick_params(axis='both', which='both', colors='#FFFFFF', zorder=0)

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('black')

        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', va='top')

        # Set title
        ax.set_title(title, fontsize=12, fontweight='normal', pad=20, loc='left')
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Add colorbar using the same norm as the heatmap
        # aspect controls width ratio, shrink controls height
        cbar = plt.colorbar(im, ax=ax, aspect=5, pad=0.04, shrink=0.2)
        cbar.ax.set_title('similarity', fontsize=10, pad=10, loc="left")
        cbar.ax.tick_params(labelsize=8)
        cbar.outline.set_visible(False)

        # # Manually set evenly spaced tick positions in the normalized space
        # # This places ticks at regular intervals regardless of the TwoSlopeNorm
        # vmin = 0
        # vmax = round(data['similarity'].max(), 2)
        # tick_values = np.linspace(vmin, vmax, num=5)
        # cbar.set_ticks(tick_values)

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
        plt.savefig(img_path, dpi=self.DEFAULT_DPI, bbox_inches='tight', facecolor='white')
        plt.close()

        return fig


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
        cell_textsize = 6

        if (data['similarity'].max()-data['similarity'].min()) > .2:
            decimals = 2
            textsize = 2.8
            minshown = .005
            cell_textsize = 8

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

        img_path = os.path.join(self.PLOTDIR, image_file)

        if self.PLOTLIB == "rpy2.ggplot2":
            return self.plot_similarity_matrix_with_rpy2_ggplot2(data=data, midpoint=midpoint, title=title, textsize=textsize, img_path=img_path)
        
        elif self.PLOTLIB == "matplotlib":
            return self.plot_similarity_matrix_with_matplotlib(data=data, decimals=decimals, title=title, cell_textsize=cell_textsize, img_path=img_path)
        
        else:
            raise ValueError("Invalid PLOTLIB")


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
