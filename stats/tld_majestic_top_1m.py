# derived from
#   http://downloads.majestic.com/majestic_million.csv
# fetched 2017-10-18
#
# see also
#
#   https://majestic.com/reports/majestic-million
#
# The Majestic Million is a list of the top 1 million website in the
# world, ordered by the number of referring subnets. A subnet is a bit
# complex – but to a layman it is basically anything within an IP
# range, ignoring the last three digits of the IP number.
#
#   https://majestic.com/support/faq#Where
#
# Where is the data coming from?
#   Our data comes from the World Wide Web itself. The Majestic-12:
#   Distributed Search Engine (http://www.majestic12.co.uk/) does not
#   meta-search or otherwise query other search engines: we are the
#   search engine! Over a long period of time we have developed
#   software capable of crawling and indexing large amounts of web
#   data. This index is a big stepping stone towards relevant
#   full-text search. The purpose of the index is to allow relevancy
#   research as well as to help fund continued activites in
#   development of a competitive community-driven general-purpose
#   web-scale search engine.
#

majestic_top_1m_tlds_about = {
  'date': '2017-10-18',
  'source': 'http://downloads.majestic.com/majestic_million.csv'
}

majestic_top_1m_tlds = {
  # cut -d, -f4 majestic_million.csv | tail -n+2 \
  #  | perl -ne 'chomp; $h{$_}++;
  #              END {
  #                for (sort { $h{$b} <=> $h{$a} } keys %h) {
  #                  print "\047", $_, "\047:", $h{$_}, ", ";
  #                }
  #              }' \
  #  | fold --width=70 -s | perl -lpe 's/^/  /; s/:/: /g; s/\s+$//'
  'com': 502000, 'org': 73338, 'net': 47548, 'ru': 45739, 'de': 28090,
  'uk': 26296, 'cn': 25039, 'jp': 14247, 'pl': 13441, 'info': 11578,
  'nl': 11098, 'it': 10912, 'fr': 9732, 'au': 8688, 'us': 8414, 'br': 7733,
  'ca': 6290, 'eu': 5399, 'es': 5172, 'in': 4977, 'top': 4774, 'cz': 4188,
  'ua': 4169, 'co': 4117, 'edu': 4025, 'se': 3635, 'ch': 3215, 'at': 3162,
  'ro': 3049, 'biz': 2976, 'tw': 2860, 'be': 2827, 'xyz': 2685, 'hu': 2557,
  'dk': 2557, 'za': 2500, 'ir': 2438, 'tr': 2424, 'gr': 2393, 'vn': 2120,
  'tv': 2051, 'cc': 1838, 'me': 1791, 'no': 1697, 'fi': 1692, 'gov': 1691,
  'kr': 1545, 'mx': 1545, 'ar': 1534, 'nz': 1485, 'gdn': 1479, 'club': 1392,
  'ie': 1347, 'xn--p1ai': 1282, 'mobi': 1257, 'cl': 1209, 'io': 1160,
  'sk': 1128, 'pt': 1116, 'by': 1081, 'il': 1038, 'my': 948, 'pro': 944,
  'hk': 916, 'su': 893, 'kz': 852, 'sg': 823, 'lt': 799, 'nu': 792,
  'bid': 725, 'id': 685, 'tk': 664, 'science': 650, 'site': 620, 'hr': 606,
  'pw': 599, 'reisen': 555, 'th': 513, 'lv': 512, 'online': 510,
  'review': 504, 'si': 490, 'name': 467, 'ee': 457, 'pk': 445, 'party': 441,
  'rs': 441, 'ph': 439, 'to': 431, 'cricket': 422, 'bg': 420, 'click': 411,
  'life': 410, 'pe': 407, 'cat': 405, 'world': 398, 'ae': 393, 'store': 367,
  'ws': 366, 'ovh': 351, 'space': 345, 'is': 338, 'link': 317, 'fm': 316,
  'shop': 307, 'trade': 307, 'ng': 305, 'ga': 256, 'ke': 250, 'sa': 249,
  'one': 231, 'md': 231, 'ma': 229, 'np': 228, 'gq': 223, 'ec': 221,
  'tech': 216, 'webcam': 210, 'lk': 210, 'work': 210, 'website': 207,
  'news': 204, 'am': 202, 'asia': 197, 'ge': 197, 'az': 183, 've': 180,
  'ml': 178, 'mk': 176, 'date': 171, 'stream': 165, 'la': 160, 'men': 159,
  'ba': 157, 'lu': 154, 'travel': 152, 'win': 151, 'uy': 145, 'uz': 145,
  'today': 143, 'ly': 142, 'im': 141, 'bz': 136, 'sexy': 136, 'cf': 135,
  'bd': 128, 'do': 126, 'live': 123, 'st': 123, 'int': 120,
  'accountant': 119, 'coop': 109, 'directory': 108, 'zone': 105, 'eg': 104,
  'tn': 102, 'mn': 102, 'aero': 102, 'cy': 97, 'systems': 93, 'kg': 92,
  'zw': 90, 'li': 90, 'mo': 89, 'schule': 86, 'mil': 84, 'tools': 84,
  'wiki': 84, 'fund': 84, 'mba': 82, 'so': 82, 'bo': 82, 'fail': 81, 'cx': 77,
  'ag': 76, 'al': 75, 'cu': 75, 'fashion': 75, 'christmas': 72, 'ms': 71,
  'desi': 70, 'cr': 69, 'vu': 68, 'casa': 66, 'guru': 66, 'jo': 66, 'ai': 65,
  'py': 65, 'sh': 64, 'lb': 63, 'media': 62, 'gs': 61, 'vip': 61, 'mt': 61,
  'ug': 56, 'vc': 56, 'ps': 56, 'xxx': 56, 'qa': 55, 'cm': 55, 'dz': 54,
  'lol': 53, 'gt': 51, 'tt': 51, 'tz': 50, 'gh': 49, 'solutions': 48,
  'press': 47, 'rocks': 46, 'red': 46, 're': 46, 'center': 45, 'global': 45,
  'tc': 45, 'ac': 44, 'eus': 44, 'kh': 43, 'ninja': 43, 'tokyo': 42, 'gg': 41,
  'wang': 41, 'sc': 39, 'mu': 39, 'as': 38, 'group': 38, 'tj': 38, 'tips': 36,
  'kw': 36, 'photography': 35, 'host': 34, 'city': 34, 'af': 33, 'blog': 33,
  'ltd': 32, 'design': 32, 'company': 31, 'download': 31, 'cd': 31,
  'services': 31, 'mz': 31, 'coffee': 30, 'network': 30, 'london': 30,
  'nyc': 30, 'tl': 29, 'museum': 29, 'sn': 29, 'works': 28, 'ni': 28,
  'nf': 28, 'gl': 28, 'xn--p1acf': 27, 'sv': 27, 'zm': 27, 'gold': 27,
  'ci': 27, 'pa': 27, 'hn': 27, 'yu': 26, 'fyi': 26, 'loan': 26, 'cloud': 26,
  'gd': 26, 'na': 25, 'om': 25, 'vg': 25, 'scot': 25, 'pn': 25, 'va': 25,
  'express': 24, 'jetzt': 24, 'brussels': 24, 'expert': 23, 'wales': 23,
  'paris': 23, 'camera': 23, 'sucks': 23, 'moscow': 23, 'jobs': 23,
  'credit': 22, 'business': 22, 'ht': 22, 'nc': 22, 'movie': 22,
  'associates': 22, 'bw': 21, 'gy': 21, 'ad': 21, 'bh': 21, 'mg': 21,
  'bargains': 21, 'agency': 21, 'exposed': 21, 'iq': 20, 'gripe': 20,
  'mc': 20, 'shopping': 20, 'reise': 20, 'xn--80adxhks': 20, 'berlin': 20,
  'education': 20, 'academy': 19, 'dj': 19, 'mw': 19, 'gal': 19, 'help': 18,
  'pub': 18, 'bike': 18, 'games': 18, 'kim': 18, 'mv': 18, 'et': 18, 'sy': 18,
  'ao': 17, 'digital': 17, 'rw': 17, 'social': 17, 'plus': 17, 'mom': 17,
  'cool': 17, 'pm': 17, 'email': 17, 'fj': 17, 'nagoya': 16, 'sd': 16,
  'xin': 16, 'fo': 16, 'bt': 16, 'ink': 16, 'foundation': 16, 'market': 16,
  'nrw': 16, 'bzh': 16, 'blue': 15, 'jm': 15, 'pr': 15, 'gm': 15, 'tf': 15,
  'faith': 14, 'ky': 14, 'community': 14, 'reviews': 14, 'report': 14,
  'gp': 14, 'video': 14, 'art': 14, 'cv': 14, 'cheap': 13, 'bio': 13,
  'pg': 13, 'tm': 13, 'love': 13, 'mm': 13, 'events': 13, 'bm': 13, 'sm': 12,
  'cash': 12, 'technology': 12, 'bf': 12, 'bn': 12, 'church': 12,
  'xn--80asehdb': 12, 'gi': 12, 'bb': 12, 'moe': 12, 'care': 12, 'sx': 11,
  'je': 11, 'ren': 11, 'farm': 11, 'camp': 11, 'guide': 11, 'bi': 11,
  'pet': 10, 'racing': 10, 'buzz': 10, 'team': 10, 'ooo': 10, 'dm': 10,
  'institute': 10, 'audio': 10, 'pics': 10, 'pictures': 10, 'pf': 10,
  'onl': 10, 'yt': 10, 'lc': 10, 'gratis': 10, 'sr': 9, 'training': 9,
  'chat': 9, 'black': 9, 'photo': 9, 'mr': 9, 'land': 9, 'uno': 9,
  'google': 9, 'ngo': 9, 'international': 9, 'studio': 9, 'support': 9,
  'cafe': 9, 'ls': 9, 'nr': 9, 'taipei': 8, 'ki': 8, 'ax': 8, 'diet': 8,
  'style': 8, 'fun': 8, 'photos': 8, 'house': 8, 'gallery': 8, 'sl': 7,
  'bs': 7, 'bayern': 7, 'amsterdam': 7, 'coach': 7, 'place': 7,
  'xn--j1amh': 7, 'xn--fiqs8s': 7, 'software': 7, 'haus': 7, 'money': 7,
  'bet': 7, 'consulting': 7, 'sz': 7, 'quebec': 6, 'codes': 6, 'wien': 6,
  'careers': 6, 'law': 6, 'hm': 6, 'university': 6, 'marketing': 6,
  'fish': 6, 'clinic': 6, 'energy': 6, 'xn--90ais': 6, 'vegas': 6,
  'xn--80aswg': 6, 'bank': 6, 'properties': 6, 'capital': 6, 'ye': 6,
  'hosting': 5, 'earth': 5, 'istanbul': 5, 'mp': 5, 'okinawa': 5, 'watch': 5,
  'fit': 5, 'poker': 5, 'taxi': 5, 'legal': 5, 'ist': 5, 'cymru': 5, 'srl': 5,
  'gop': 5, 'pink': 5, 'wtf': 5, 'bj': 5, 'casino': 5, 'recipes': 5,
  'forsale': 5, 'deals': 5, 'vi': 5, 'tg': 5, 'dental': 4, 'kp': 4,
  'hamburg': 4, 'rest': 4, 'porn': 4, 'graphics': 4, 'bnpparibas': 4,
  'sale': 4, 'abbott': 4, 'ne': 4, 'ski': 4, 'rip': 4, 'swiss': 4,
  'engineering': 4, 'corsica': 4, 'run': 4, 'menu': 4, 'band': 4,
  'exchange': 4, 'garden': 4, 'estate': 4, 'best': 4, 'sb': 4, 'dance': 4,
  'saarland': 4, 'lighting': 4, 'aq': 4, 'cern': 4, 'rent': 3, 'sex': 3,
  'sydney': 3, 'toys': 3, 'bar': 3, 'xn--6frz82g': 3, 'healthcare': 3,
  'vlaanderen': 3, 'archi': 3, 'family': 3, 'school': 3, 'cam': 3,
  'shoes': 3, 'coupons': 3, 'green': 3, 'dog': 3, 'glass': 3, 'realtor': 3,
  'frl': 3, 'eco': 3, 'ck': 3, 'immo': 3, 'lat': 3, 'show': 3, 'repair': 3,
  'tp': 3, 'kiwi': 3, 'wine': 3, 'fitness': 3, 'build': 3, 'attorney': 3,
  'management': 3, 'koeln': 3, 'lgbt': 3, 'domains': 3, 'game': 3, 'golf': 3,
  'discount': 3, 'krd': 3, 'kn': 2, 'builders': 2, 'auto': 2, 'how': 2,
  'active': 2, 'xn--c1avg': 2, 'tattoo': 2, 'solar': 2, 'cw': 2, 'cg': 2,
  'parts': 2, 'rio': 2, 'equipment': 2, 'lawyer': 2, 'bingo': 2,
  'melbourne': 2, 'gent': 2, 'tours': 2, 'moda': 2, 'town': 2, 'holdings': 2,
  'contractors': 2, 'yoga': 2, 'barcelona': 2, 'vet': 2, 'study': 2,
  'sandvik': 2, 'restaurant': 2, 'capetown': 2, 'computer': 2, 'wf': 2,
  'alsace': 2, 'furniture': 2, 'ceo': 2, 'kred': 2, 'aws': 2, 'direct': 2,
  'post': 2, 'nico': 2, 'aw': 2, 'ipaddr': 2, 'xn--55qx5d': 2, 'vision': 2,
  'productions': 2, 'vote': 2, 'barclays': 2, 'financial': 2, 'boutique': 2,
  'km': 2, 'supply': 2, 'cards': 2, 'yokohama': 2, 'holiday': 2,
  'kitchen': 2, 'an': 2, 'beer': 2, 'film': 2, 'plumbing': 2, 'rehab': 2,
  'dating': 2, 'condos': 1, 'cologne': 1, 'tel': 1, 'futbol': 1, 'ong': 1,
  'goo': 1, 'durban': 1, 'sky': 1, 'fast': 1, 'car': 1, 'forum': 1, 'here': 1,
  'eh': 1, 'cs': 1, 'markets': 1, 'florist': 1, 'gn': 1, 'catering': 1,
  'luxury': 1, 'flickr': 1, 'doctor': 1, 'tax': 1, 'goog': 1, 'surgery': 1,
  'jcb': 1, 'hitachi': 1, 'fox': 1, 'hot': 1, 'democrat': 1, 'clothing': 1,
  'mortgage': 1, 'joburg': 1, 'bible': 1, 'bbc': 1, 'fage': 1, 'cooking': 1,
  'gift': 1, 'dhl': 1, 'limited': 1, 'sener': 1, 'promo': 1, 'trading': 1,
  'microsoft': 1, 'monash': 1, 'td': 1, 'box': 1, 'jll': 1, 'uol': 1,
  'tirol': 1, 'cleaning': 1, 'enterprises': 1, 'neustar': 1, 'guitars': 1,
  'apple': 1, 'um': 1, 'theater': 1, 'gifts': 1, 'construction': 1,
  'shiksha': 1, 'lidl': 1, 'xn--90a3ac': 1, 'career': 1, 'schmidt': 1,
  'engineer': 1, 'supplies': 1, 'lr': 1, 'ruhr': 1, 'abc': 1, 'big': 1,
  'pharmacy': 1, 'finance': 1, 'kyoto': 1, 'kinder': 1, 'college': 1,
  'buy': 1, 'weir': 1, 'diamonds': 1, 'youtube': 1, 'basketball': 1,
  'yahoo': 1, 'new': 1, 'rentals': 1, 'juegos': 1, 'free': 1, 'soccer': 1,
  'barclaycard': 1, 'you': 1, 'fk': 1, 'gmbh': 1, 'limo': 1, 'partners': 1,
  'baidu': 1, 'xn--d1acj3b': 1, 'java': 1, 'gu': 1, 'ltda': 1, 'surf': 1,
  'vin': 1, 'insure': 1, 'bradesco': 1, 'saxo': 1, 'immobilien': 1,
  'xn--tckwe': 1, 'miami': 1, 'ismaili': 1, 'zip': 1, 'qpon': 1, 'trust': 1,
  'kaufen': 1, 'tickets': 1, 'voyage': 1, 'canon': 1, 'industries': 1,
  'pictet': 1,
}
