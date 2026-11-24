"""
Plot the evolution of Common Crawl's coverage of the 24 official EU languages.

Reads the language statistics table (plots/languages.csv, written by
plot/language.py) and, for the crawls of the last N years (default: 2),
writes to the output directory:

- eu-languages-share.csv: share of HTML pages (%pages/crawl) per crawl
  and language (wide table)
- eu-languages-grid.png: small multiples, one panel per language,
  each with its own y-axis
- eu-languages-log.png: all languages in a single plot on a log scale

Only pandas and matplotlib are required (no crawlstats / mrjob).

Usage:
    python3 plot/language_eu_evolution.py [--csv plots/languages.csv]
                                          [--years 2]
                                          [--outdir data/languages-eu]
"""

import argparse
import datetime
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402


# official EU languages, ISO 639-3 codes as used by CLD2 in languages.csv
EU_LANGUAGES = {
    'bul': 'Bulgarian',
    'hrv': 'Croatian',
    'ces': 'Czech',
    'dan': 'Danish',
    'nld': 'Dutch',
    'eng': 'English',
    'est': 'Estonian',
    'fin': 'Finnish',
    'fra': 'French',
    'deu': 'German',
    'ell': 'Greek',
    'hun': 'Hungarian',
    'gle': 'Irish',
    'ita': 'Italian',
    'lav': 'Latvian',
    'lit': 'Lithuanian',
    'mlt': 'Maltese',
    'pol': 'Polish',
    'por': 'Portuguese',
    'ron': 'Romanian',
    'slk': 'Slovak',
    'slv': 'Slovenian',
    'spa': 'Spanish',
    'swe': 'Swedish',
}

SHARE_COLUMN = '%pages/crawl'

# categorical palette (fixed order), combined with line styles for the
# single plot showing all 24 languages: 8 hues x 3 line styles
SERIES_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100',
                 '#e87ba4', '#008300', '#6250d6', '#e34948']
LINE_STYLES = ['-', '--', ':']

TEXT_PRIMARY = '#1f1f1e'
TEXT_SECONDARY = '#5f5e5a'
GRID_COLOR = '#E6E6E6'
DPI = 300


def crawl_date(crawl):
    """Monday of the ISO week of a crawl named CC-MAIN-YYYY-WW
    (same as MonthlyCrawl.date_of in crawlstats.py)."""
    parts = crawl.split('-')
    if len(parts) != 4 or len(parts[3]) != 2:
        # early crawls (CC-MAIN-2008-2009, CC-MAIN-2012, ...) are
        # far outside any recent window
        return None
    return datetime.date.fromisocalendar(int(parts[2]), int(parts[3]), 1)


def load_shares(csv_path, years):
    data = pandas.read_csv(csv_path, keep_default_na=False)
    missing = sorted(set(EU_LANGUAGES) - set(data['primary_language']))
    if missing:
        sys.exit('Languages missing in {}: {}'.format(csv_path,
                                                      ', '.join(missing)))

    crawls = pandas.DataFrame({'crawl': data['crawl'].unique()})
    crawls['date'] = crawls['crawl'].map(crawl_date)
    crawls = crawls.dropna().sort_values('date')
    latest = crawls['date'].iloc[-1]
    try:
        start = latest.replace(year=latest.year - years)
    except ValueError:  # 29 February
        start = latest.replace(year=latest.year - years, day=28)
    crawls = crawls[crawls['date'] >= start]

    data = data[data['crawl'].isin(crawls['crawl'])
                & data['primary_language'].isin(EU_LANGUAGES)]
    shares = data.pivot(index='crawl', columns='primary_language',
                        values=SHARE_COLUMN)
    shares = shares.reindex(index=crawls['crawl'])
    if shares.isna().any().any():
        print('Warning: missing values for some crawls/languages:\n{}'
              .format(shares[shares.isna().any(axis=1)]), file=sys.stderr)
    shares.insert(0, 'date', pandas.to_datetime(crawls.set_index('crawl')['date']))

    # order languages by average share in the window (largest first)
    order = shares[list(EU_LANGUAGES)].mean().sort_values(ascending=False).index
    return shares[['date'] + list(order)], list(order)


def percent_formatter(value, _pos):
    if value == 0:
        return '0%'
    if abs(value) >= 1:
        return '{:g}%'.format(round(value, 1))
    return '{:.2g}%'.format(value)


def style_axes(ax):
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
    ax.grid(True, which='major', linewidth=0.8, color=GRID_COLOR, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis='both', which='both', length=0,
                   labelcolor=TEXT_SECONDARY)


def set_date_axis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))


def window_title(shares):
    return '{} – {}'.format(shares.index[0], shares.index[-1])


def plot_grid(shares, languages, img_path):
    ncols, nrows = 4, 6
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 18), sharex=True)
    for ax, lang in zip(axes.flat, languages):
        ax.plot(shares['date'], shares[lang], '-o', color=SERIES_COLORS[0],
                linewidth=1.5, markersize=3.5, zorder=3)
        ax.set_title('{} ({})'.format(EU_LANGUAGES[lang], lang),
                     loc='left', fontsize=12, color=TEXT_PRIMARY)
        # y-axis from 0, so that relative changes are not exaggerated
        ax.set_ylim(0, shares[lang].max() * 1.15)
        ax.yaxis.set_major_locator(plt.MaxNLocator(4))
        ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
        set_date_axis(ax)
        style_axes(ax)
        ax.tick_params(labelsize=9)
    for ax in axes.flat[len(languages):]:
        ax.set_visible(False)
    fig.suptitle('Share of HTML pages per EU language, {}'
                 .format(window_title(shares)),
                 x=0.01, y=0.995, ha='left', fontsize=16,
                 color=TEXT_PRIMARY)
    fig.text(0.01, 0.975,
             'Primary language detected by CLD2, percentage of page captures '
             'per crawl. Each panel has its own y-axis.',
             ha='left', fontsize=11, color=TEXT_SECONDARY)
    fig.tight_layout(rect=(0, 0, 1, 0.965), h_pad=2.0)
    fig.savefig(img_path, dpi=DPI, facecolor='white')
    plt.close(fig)


def spread_labels(values, min_gap):
    """Shift label positions (log10 space) apart by at least min_gap,
    keeping their order."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    pos = list(values)
    for k in range(1, len(order)):
        prev, cur = order[k - 1], order[k]
        if pos[cur] - pos[prev] < min_gap:
            pos[cur] = pos[prev] + min_gap
    # re-center the shifted block around the original mean
    shift = (sum(values) - sum(pos)) / len(pos)
    return [p + shift for p in pos]


def plot_log(shares, languages, img_path):
    import numpy

    fig, ax = plt.subplots(figsize=(12, 10))
    last = shares.iloc[-1]
    label_y = spread_labels([numpy.log10(last[lang]) for lang in languages],
                            min_gap=0.075)
    x_end = shares['date'].iloc[-1]
    x_label = x_end + pandas.Timedelta(days=25)
    for i, lang in enumerate(languages):
        color = SERIES_COLORS[i % len(SERIES_COLORS)]
        style = LINE_STYLES[i // len(SERIES_COLORS)]
        ax.plot(shares['date'], shares[lang], linestyle=style, color=color,
                linewidth=1.8, marker='o', markersize=2.5,
                label='{} ({})'.format(EU_LANGUAGES[lang], lang), zorder=3)
        y = 10 ** label_y[i]
        ax.plot([x_end, x_label], [last[lang], y], color=color,
                linewidth=0.6, linestyle=style, zorder=2)
        ax.text(x_label + pandas.Timedelta(days=5), y,
                '{} {}'.format(lang, percent_formatter(last[lang], None)),
                va='center', ha='left', fontsize=9, color=TEXT_PRIMARY)
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    ax.set_xlim(shares['date'].iloc[0] - pandas.Timedelta(days=15),
                x_end + pandas.Timedelta(days=150))
    set_date_axis(ax)
    # no date ticks in the label margin right of the latest crawl
    ticks = [t for t in mdates.MonthLocator(bymonth=[1, 7]).tick_values(
        shares['date'].iloc[0], x_end) if mdates.num2date(t).date() <= x_end.date()]
    ax.set_xticks(ticks)
    style_axes(ax)
    ax.grid(True, which='minor', axis='y', linewidth=0.4, color=GRID_COLOR)
    ax.set_ylabel('Share of HTML pages (log scale)', color=TEXT_SECONDARY)
    ax.set_title('Share of HTML pages per EU language, {}'
                 .format(window_title(shares)),
                 loc='left', fontsize=15, color=TEXT_PRIMARY, pad=14)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=4,
              frameon=False, fontsize=9, labelcolor=TEXT_PRIMARY,
              handlelength=3)
    fig.tight_layout()
    fig.savefig(img_path, dpi=DPI, facecolor='white')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--csv', default='plots/languages.csv',
                        help='language statistics (default: %(default)s)')
    parser.add_argument('--years', type=int, default=2,
                        help='number of years back from the latest crawl'
                             ' (default: %(default)s)')
    parser.add_argument('--outdir', default='data/languages-eu',
                        help='output directory (default: %(default)s)')
    args = parser.parse_args()
    if args.years < 1:
        parser.error('--years must be at least 1')

    shares, languages = load_shares(args.csv, args.years)
    print('Selected {} crawls: {}'.format(len(shares), ', '.join(shares.index)))

    os.makedirs(args.outdir, exist_ok=True)
    csv_out = os.path.join(args.outdir, 'eu-languages-share.csv')
    shares.to_csv(csv_out, float_format='%.4f', date_format='%Y-%m-%d')
    print('Wrote', csv_out)
    for name, func in [('eu-languages-grid.png', plot_grid),
                       ('eu-languages-log.png', plot_log)]:
        path = os.path.join(args.outdir, name)
        func(shares, languages, path)
        print('Wrote', path)


if __name__ == '__main__':
    main()
