# derived from
#   http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip
# fetched 2019-02-06, see also
#   http://s3-us-west-1.amazonaws.com/umbrella-static/index.html
#
# "The popularity list contains our most queried domains based on
# passive DNS usage across our Umbrella global network of more than
# 100 Billion requests per day with 65 million unique active users, in
# more than 165 countries. Unlike Alexa, the metric is not based on
# only browser based 'http' requests from users but rather takes into
# account the number of unique client IPs invoking this domain
# relative to the sum of all requests to all domains. In other words,
# our popularity ranking reflects the domain’s relative internet
# activity agnostic to the invocation protocols and applications where
# as ’site ranking’ models (such as Alexa) focus on the web activity
# over port 80 mainly from browsers.
#
# As for Alexa, the site’s rank is based on combined measure of unique
# visitors (Alexa users who visit the site per day) and page views
# (total URL requests from Alexa users for a site). Umbrella
# popularity lists are generated on a daily basis reflecting the
# actual world-wide usage of domains by Umbrella global network users
# and includes root domains, subdomains in addition to TLDs (Alexa
# list has only this). In addition, Umbrella popularity algorithm also
# applies data normalization methodologies to smoothen potential
# biases that may occur in the data due to sampling of the DNS usage
# data."
#
#
# NOTE: The list contains also domain names from intranets - 'localhost',
#       'belkin', 'dlinkrouter', 'dmz', etc.  These are filtered out by
#       allowing only IANA-registered domain name suffixes.
#

cisco_umbrella_top_1m_tlds_about = {
  'date': '2019-02-06',
  'source': 'http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip'
}

cisco_umbrella_top_1m_tlds = {
  # zcat top-1m.csv.zip \
  #  | perl -ne 'chomp; s/^\d+,//; s/.+\.//; $h{$_}++;
  #              END {
  #                for (sort { $h{$b} <=> $h{$a} } keys %h) {
  #                  print "\047", $_, "\047:", $h{$_}, ", ";
  #                }
  #              }' \
  #  | fold --width=70 -s | perl -lpe 's/^/  /; s/:/: /g; s/\s+$//'
  'com': 579421, 'net': 155319, 'org': 41951, 'ru': 14293, 'uk': 11216,
  'edu': 10324, 'biz': 9884, 'io': 9316, 'de': 9179, 'me': 7807,
  'info': 7483, 'cn': 6274, 'in': 6267, 'cc': 5401, 'co': 5352, 'gov': 5068,
  'br': 4846, 'fr': 4752, 'nl': 4499, 'it': 4251, 'us': 3929, 'tv': 3813,
  'eu': 3689, 'ca': 3585, 'jp': 3570, 'pl': 3361, 'vn': 2666, 'ua': 2572,
  'es': 2249, 'au': 1901, 'mx': 1504, 'ch': 1462, 'be': 1455, 'id': 1386,
  'se': 1253, 'dk': 1236, 'il': 1198, 'pt': 1180, 'link': 1153, 'cz': 1133,
  'xyz': 1078, 'email': 1065, 'no': 1054, 'tr': 1044, 'kr': 996, 'club': 962,
  'hu': 898, 'tw': 890, 'at': 866, 'mobi': 861, 'gr': 801, 'ir': 778,
  'nz': 740, 'to': 735, 'pro': 707, 'cloud': 656, 'ro': 645, 'ar': 633,
  'my': 631, 'hk': 612, 'online': 600, 'cl': 561, 'top': 540, 'za': 536,
  'fi': 534, 'th': 526, 'mil': 489, 'sg': 488, 'sk': 486, 'pw': 463,
  'name': 447, 'ie': 438, 'ng': 431, 'by': 419, 'ms': 402, 'st': 376,
  'ec': 369, 'fm': 364, 'site': 362, 'ai': 361, 'ws': 357, 'is': 333,
  'ph': 330, 'live': 326, 'pk': 325, 'im': 318, 'pe': 317, 'icu': 282,
  've': 269, 'ae': 269, 'su': 264, 'media': 256, 'bg': 254, 'ly': 250,
  'lt': 248, 'kz': 228, 'xxx': 227, 'gg': 223, 'do': 218, 'space': 216,
  'hr': 211, 'services': 207, 'app': 202, 'cr': 198, 'tech': 196,
  'systems': 182, 'gl': 175, 'ga': 172, 'rs': 166, 'host': 163, 'news': 162,
  'video': 154, 'box': 154, 'network': 148, 'bz': 142, 'md': 142, 'sh': 140,
  'ee': 138, 'lv': 138, 'tc': 137, 'eg': 131, 'tk': 131, 'la': 128,
  'asia': 128, 'solutions': 127, 'life': 127, 'si': 126, 'lk': 125,
  'nu': 124, 'one': 123, 'fun': 122, 'int': 122, 'stream': 122, 'world': 121,
  'zone': 118, 'bid': 118, 'uy': 113, 'gt': 113, 'rocks': 113, 'bd': 112,
  'lu': 111, 'am': 110, 'ag': 109, 'cat': 108, 'today': 108, 'sa': 105,
  'store': 102, 'click': 102, 'ninja': 101, 'digital': 100, 'website': 94,
  'aero': 94, 'win': 92, 'li': 85, 're': 85, 'ba': 84, 'ke': 82, 'work': 78,
  'pa': 77, 'ovh': 76, 'games': 74, 'support': 73, 'hn': 70, 'dz': 69,
  'vip': 68, 'sc': 67, 'al': 66, 'arpa': 65, 'sex': 63, 'tools': 63,
  'guru': 60, 'ml': 60, 'az': 59, 'global': 59, 'py': 58, 'management': 58,
  'download': 57, 'travel': 57, 'ma': 56, 'coop': 56, 'cm': 55, 'cu': 54,
  'aws': 54, 'works': 54, 'vc': 53, 'sv': 53, 'cy': 53, 'cool': 51,
  'jobs': 51, 'chat': 51, 'so': 50, 'kh': 50, 'plus': 50, 'np': 50, 'cf': 49,
  'kg': 47, 'technology': 47, 'uz': 47, 'gs': 47, 'qa': 46, 'date': 46,
  'bo': 46, 'lb': 46, 'pub': 45, 'ge': 45, 'ac': 43, 'ni': 42, 'blog': 41,
  'bet': 41, 'tf': 41, 'ad': 40, 'sx': 39, 'af': 39, 'cx': 37, 'money': 37,
  'ps': 36, 'gh': 33, 'tn': 33, 'goog': 32, 'xn--p1ai': 32, 'agency': 32,
  'zw': 32, 'as': 31, 'tt': 31, 'mn': 30, 'mk': 30, 'pm': 30, 'press': 29,
  'shop': 29, 'events': 29, 'run': 29, 'mt': 29, 'wiki': 28, 'trade': 28,
  'porn': 28, 'pr': 27, 'tl': 27, 'tube': 26, 'om': 26, 'studio': 26,
  'sn': 24, 'ci': 24, 'mm': 23, 'gdn': 23, 'ug': 23, 'team': 23, 'moe': 23,
  'sexy': 23, 'software': 22, 'pics': 21, 'tips': 21, 'vg': 21, 'review': 20,
  'iq': 20, 'tz': 20, 'sap': 20, 'mg': 20, 'science': 20, 'land': 20,
  'na': 20, 'party': 19, 'gq': 19, 'google': 19, 'help': 19, 'lol': 19,
  'wtf': 19, 'center': 19, 'mu': 18, 'company': 18, 'cd': 17, 'gy': 17,
  'ink': 17, 'jm': 17, 'sncf': 17, 'fyi': 17, 'engineering': 17, 'group': 17,
  'va': 17, 'market': 17, 'eus': 17, 'tm': 16, 'cash': 16, 'cricket': 16,
  'care': 16, 'guide': 15, 'film': 15, 'mv': 15, 'bm': 15, 'buzz': 15,
  'pg': 15, 'ne': 15, 'ooo': 15, 'direct': 15, 'bn': 14, 'expert': 14,
  'lat': 14, 'game': 14, 'watch': 14, 'scot': 14, 'photos': 13, 'ao': 13,
  'love': 13, 'bh': 13, 'uno': 13, 'design': 13, 'ky': 13, 'report': 13,
  'menu': 13, 'ltd': 12, 'bank': 12, 'moscow': 12, 'movie': 12, 'bs': 12,
  'bw': 12, 'mz': 12, 'nyc': 12, 'ht': 11, 'tj': 11, 'sm': 11, 'leclerc': 11,
  'jo': 11, 'yandex': 11, 'dj': 11, 'show': 11, 'gd': 11, 'london': 11,
  'nc': 10, 'rw': 10, 'training': 10, 'et': 10, 'social': 10, 'express': 10,
  'gift': 10, 'church': 10, 'ye': 10, 'health': 10, 'dm': 10, 'bike': 10,
  'fj': 10, 'school': 10, 'city': 10, 'hosting': 10, 'photo': 9, 'llc': 9,
  'rip': 9, 'community': 9, 'recipes': 9, 'men': 9, 'domains': 9,
  'supply': 9, 'education': 9, 'dev': 8, 'sky': 8, 'pn': 8, 'delivery': 8,
  'law': 8, 'audio': 8, 'gratis': 8, 'kw': 8, 'cab': 8, 'gm': 8, 'pet': 8,
  'rest': 8, 'build': 8, 'tel': 8, 'loan': 7, 'energy': 7, 'farm': 7, 'lc': 7,
  'museum': 7, 'cv': 7, 'red': 7, 'vision': 7, 'ist': 7, 'ki': 7, 'fit': 7,
  'je': 7, 'onl': 7, 'art': 7, 'pictures': 7, 'wf': 7, 'webcam': 7, 'pink': 7,
  'vu': 7, 'zm': 7, 'supplies': 6, 'codes': 6, 'faith': 6, 'marketing': 6,
  'pharmacy': 6, 'academy': 6, 'wang': 6, 'gold': 6, 'blue': 6, 'fail': 6,
  'football': 6, 'business': 6, 'gi': 6, 'sl': 6, 'bio': 6, 'exchange': 6,
  'post': 6, 'fo': 6, 'style': 6, 'army': 6, 'gp': 6, 'cafe': 6, 'paris': 6,
  'hm': 6, 'gal': 6, 'cisco': 5, 'uol': 5, 'here': 5, 'nf': 5, 'house': 5,
  'dog': 5, 'taxi': 5, 'bi': 5, 'sb': 5, 'schwarz': 5, 'sr': 5, 'careers': 5,
  'kim': 5, 'bt': 5, 'canon': 5, 'pf': 5, 'sy': 5, 'yt': 5, 'ads': 4,
  'tokyo': 4, 'international': 4, 'realtor': 4, 'earth': 4, 'legal': 4,
  'nr': 4, 'dhl': 4, 'garden': 4, 'meet': 4, 'consulting': 4, 'abbott': 4,
  'weir': 4, 'toys': 4, 'ski': 4, 'bb': 4, 'deals': 4, 'bradesco': 4,
  'fitness': 4, 'bot': 4, 'golf': 4, 'cw': 4, 'fish': 4, 'kpmg': 4, 'bj': 4,
  'best': 4, 'cam': 4, 'boutique': 4, 'diet': 3, 'sd': 3, 'cheap': 3, 'td': 3,
  'mo': 3, 'ck': 3, 'tours': 3, 'bnpparibas': 3, 'tax': 3, 'bzh': 3,
  'directory': 3, 'adult': 3, 'fashion': 3, 'new': 3, 'istanbul': 3,
  'neustar': 3, 'band': 3, 'bar': 3, 'vacations': 3, 'bf': 3, 'tg': 3,
  'inc': 3, 'limited': 3, 'koeln': 3, 'barclays': 3, 'wales': 3, 'ren': 3,
  'camera': 3, 'kiwi': 3, 'vet': 3, 'solar': 3, 'discount': 3, 'partners': 3,
  'haus': 3, 'lease': 3, 'glass': 3, 'forsale': 3, 'radio': 3, 'builders': 3,
  'hsbc': 3, 'racing': 3, 'shopping': 3, 'ax': 3, 'vi': 3, 'coffee': 2,
  'nrw': 2, 'bingo': 2, 'cars': 2, 'saxo': 2, 'crs': 2, 'beer': 2,
  'brother': 2, 'pizza': 2, 'chrome': 2, 'dance': 2, 'fans': 2, 'town': 2,
  'flights': 2, 'car': 2, 'storage': 2, 'nra': 2, 'sony': 2, 'mc': 2,
  'nico': 2, 'coach': 2, 'mp': 2, 'degree': 2, 'camp': 2, 'trust': 2,
  'graphics': 2, 'miami': 2, 'sale': 2, 'reviews': 2, 'mw': 2, 'rugby': 2,
  'ls': 2, 'finance': 2, 'cards': 2, 'how': 2, 'moda': 2, 'madrid': 2,
  'quebec': 2, 'office': 2, 'xn--9dbq2a': 2, 'dating': 2, 'gallery': 2,
  'kn': 2, 'basketball': 2, 'tattoo': 2, 'cg': 2, 'lgbt': 2, 'foundation': 2,
  'africa': 2, 'barclaycard': 2, 'baby': 1, 'bing': 1, 'hitachi': 1,
  'vin': 1, 'goo': 1, 'hockey': 1, 'insure': 1, 'actor': 1, 'saarland': 1,
  'java': 1, 'gmail': 1, 'youtube': 1, 'ltda': 1, 'brussels': 1, 'navy': 1,
  'xn--54b7fta0cc': 1, 'institute': 1, 'green': 1, 'prod': 1, 'diamonds': 1,
  'ice': 1, 'cern': 1, 'itau': 1, 'seven': 1, 'associates': 1,
  'williamhill': 1, 'auction': 1, 'abc': 1, 'xn--j1amh': 1, 'holiday': 1,
  'xn--c1avg': 1, 'study': 1, 'tatar': 1, 'ss': 1, 'xn--d1acj3b': 1,
  'vote': 1, 'docs': 1, 'amex': 1, 'page': 1, 'itv': 1, 'healthcare': 1,
  'honda': 1, 'cymru': 1, 'place': 1, 'play': 1, 'dental': 1, 'yahoo': 1,
  'audible': 1, 'fage': 1, 'college': 1, 'eco': 1, 'aw': 1, 'gifts': 1,
  'mr': 1, 'jaguar': 1, 'berlin': 1, 'photography': 1, 'secure': 1,
  'xn--80asehdb': 1, 'crown': 1, 'gn': 1, 'landrover': 1, 'horse': 1,
  'ventures': 1, 'kp': 1, 'vanguard': 1, 'casa': 1, 'luxury': 1,
}
