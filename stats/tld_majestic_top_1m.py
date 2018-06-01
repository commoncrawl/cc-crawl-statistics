# derived from
#   http://downloads.majestic.com/majestic_million.csv
# fetched 2018-05-22
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
  'date': '2018-05-22',
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
  'com': 491143, 'org': 73465, 'net': 46286, 'ru': 43284, 'de': 32762,
  'uk': 27735, 'cn': 23285, 'jp': 14266, 'pl': 13435, 'info': 11637,
  'it': 11342, 'nl': 11146, 'fr': 10326, 'au': 9164, 'br': 9000, 'ca': 6604,
  'in': 5781, 'cz': 5598, 'es': 5569, 'eu': 5502, 'us': 5181, 'club': 4847,
  'co': 4478, 'ua': 4080, 'se': 4061, 'edu': 3966, 'ch': 3427, 'at': 3349,
  'nu': 3260, 'ro': 3058, 'be': 3008, 'ir': 2985, 'biz': 2969, 'tr': 2839,
  'tw': 2815, 'za': 2787, 'vn': 2776, 'hu': 2760, 'dk': 2666, 'gr': 2350,
  'tv': 2053, 'xyz': 2004, 'me': 1929, 'top': 1816, 'gov': 1695, 'ar': 1690,
  'no': 1669, 'mx': 1666, 'cc': 1620, 'io': 1613, 'nz': 1542, 'mobi': 1497,
  'cl': 1495, 'pt': 1491, 'fi': 1481, 'sk': 1465, 'kr': 1431,
  'xn--p1ai': 1408, 'ie': 1388, 'hk': 1101, 'il': 1059, 'by': 1056,
  'my': 1021, 'tk': 1006, 'lt': 958, 'id': 949, 'kz': 935, 'su': 880,
  'online': 873, 'sg': 842, 'pro': 801, 'store': 662, 'site': 628, 'hr': 619,
  'space': 605, 'pw': 602, 'world': 591, 'reisen': 573, 'pk': 548, 'th': 528,
  'lv': 521, 'si': 507, 'ph': 480, 'rs': 480, 'ee': 480, 'name': 460,
  'shop': 456, 'to': 442, 'cat': 436, 'ae': 432, 'bg': 425, 'pe': 423,
  'ws': 406, 'ng': 405, 'life': 385, 'ga': 357, 'xn--fiqs8s': 354, 'is': 340,
  'fm': 322, 'gdn': 320, 'live': 314, 'ml': 310, 'ke': 276, 'ma': 271,
  'sa': 268, 'np': 258, 'stream': 258, 'bid': 258, 'md': 254, 'one': 250,
  'gq': 231, 'ec': 225, 'news': 223, 'am': 220, 'cf': 219, 'lk': 217,
  'work': 213, 'win': 212, 'asia': 211, 'az': 204, 'website': 200,
  'men': 195, 'fun': 194, 'mk': 192, 'ovh': 191, 'ge': 189, 've': 181,
  'science': 177, 'tech': 176, 'ba': 172, 'travel': 166, 'lu': 165,
  'bd': 163, 'uy': 162, 'uz': 157, 'today': 156, 'bz': 148, 'review': 145,
  'ly': 144, 'la': 137, 'party': 135, 'im': 130, 'mn': 129, 'do': 126,
  'st': 126, 'int': 122, 'tn': 119, 'kg': 116, 'trade': 114, 'coop': 114,
  'aero': 112, 'eg': 111, 'date': 107, 'zone': 106, 'webcam': 105,
  'accountant': 104, 'services': 103, 'al': 102, 'li': 101, 'zw': 95,
  'ai': 94, 'cy': 93, 'vip': 90, 'directory': 89, 'link': 89, 'mil': 85,
  'media': 83, 'cricket': 82, 'cx': 81, 'py': 81, 'so': 81, 'bo': 80,
  'network': 78, 'mo': 77, 'wiki': 76, 'jo': 76, 'cu': 72, 'tools': 72,
  'ms': 72, 'loan': 71, 'mt': 69, 'schule': 68, 'cr': 68, 'sh': 68, 'mba': 67,
  'systems': 65, 'guru': 64, 'ag': 64, 'lb': 63, 'vc': 63, 'tz': 61, 'ug': 61,
  'center': 60, 'ps': 59, 'gs': 58, 'global': 58, 'fail': 57, 'dz': 57,
  'gh': 57, 'gg': 56, 'gt': 55, 'qa': 55, 'download': 54, 'vu': 53,
  'design': 53, 'racing': 52, 'fund': 51, 'eus': 50, 'mu': 50, 'tt': 49,
  'cm': 49, 'blog': 49, 'kh': 49, 'rocks': 49, 're': 49, 'faith': 48,
  'tc': 47, 'xxx': 46, 'press': 45, 'click': 44, 'ac': 43, 'af': 41,
  'city': 40, 'as': 40, 'agency': 38, 'sc': 38, 'nyc': 38, 'xn--p1acf': 37,
  'tj': 36, 'tips': 36, 'company': 36, 'tokyo': 36, 'london': 35,
  'solutions': 34, 'ninja': 33, 'scot': 33, 'cd': 32, 'ni': 32, 'mz': 32,
  'kw': 31, 'sv': 31, 'sn': 31, 'group': 30, 'wang': 30, 'tl': 30, 'host': 30,
  'wales': 30, 'gd': 30, 'museum': 29, 'cloud': 29, 'movie': 29, 'na': 28,
  'zm': 28, 'gl': 27, 'yu': 27, 'ci': 27, 'va': 27, 'gal': 27, 'bt': 27,
  'nf': 26, 'jobs': 26, 'pa': 26, 'bh': 26, 'rw': 26, 'vg': 25, 'paris': 25,
  'fj': 25, 'hn': 25, 'red': 24, 'moscow': 24, 'bw': 24, 'om': 24, 'art': 24,
  'digital': 23, 'mg': 23, 'technology': 23, 'mc': 23, 'brussels': 22,
  'studio': 22, 'community': 22, 'et': 22, 'guide': 21, 'games': 21,
  'pub': 21, 'gy': 21, 'social': 21, 'ht': 21, 'events': 20, 'academy': 20,
  'pm': 20, 'nrw': 20, 'ao': 20, 'iq': 20, 'nc': 20, 'sy': 20,
  'xn--80adxhks': 19, 'berlin': 19, 'ad': 19, 'mm': 19, 'cv': 19,
  'works': 18, 'help': 18, 'pn': 18, 'ky': 18, 'dj': 18, 'reviews': 18,
  'amsterdam': 17, 'consulting': 17, 'bzh': 17, 'ltd': 17, 'fo': 17,
  'ink': 17, 'mw': 16, 'expert': 16, 'pg': 16, 'mv': 16, 'pr': 16, 'sd': 16,
  'video': 16, 'photography': 16, 'marketing': 16, 'jm': 15, 'plus': 15,
  'gm': 15, 'moe': 15, 'exchange': 15, 'bi': 15, 'tf': 15, 'cool': 14,
  'bf': 14, 'okinawa': 14, 'bio': 14, 'cash': 14, 'google': 14,
  'education': 14, 'kim': 13, 'bike': 13, 'market': 13, 'care': 13,
  'foundation': 13, 'church': 13, 'tm': 13, 'swiss': 13, 'gp': 13,
  'love': 13, 'xin': 13, 'house': 12, 'promo': 12, 'bb': 12, 'bm': 12,
  'casino': 12, 'international': 12, 'uno': 12, 'sx': 12, 'lc': 12, 'sm': 12,
  'gi': 12, 'pf': 12, 'ngo': 12, 'coffee': 11, 'bn': 11, 'fit': 11,
  'sexy': 11, 'energy': 11, 'land': 11, 'dm': 11, 'earth': 10, 'nr': 10,
  'email': 10, 'sr': 10, 'report': 10, 'camp': 10, 'capital': 10,
  'photo': 10, 'onl': 10, 'blue': 10, 'je': 10, 'photos': 9, 'istanbul': 9,
  'sydney': 9, 'xn--90ais': 9, 'team': 9, 'institute': 9, 'yt': 9, 'farm': 9,
  'bet': 9, 'mr': 9, 'wtf': 9, 'pictures': 9, 'pics': 9, 'sz': 9, 'bayern': 9,
  'support': 9, 'business': 8, 'lol': 8, 'deals': 8, 'ls': 8, 'cheap': 8,
  'buzz': 8, 'ist': 8, 'audio': 8, 'bank': 8, 'codes': 8, 'software': 8,
  'fyi': 8, 'fitness': 8, 'poker': 8, 'chat': 8, 'sale': 8, 'cafe': 8,
  'sl': 8, 'tg': 8, 'bs': 8, 'wien': 7, 'domains': 7, 'cymru': 7, 'ye': 7,
  'watch': 7, 'ki': 7, 'xn--j1amh': 7, 'legal': 7, 'taipei': 7, 'mom': 7,
  'family': 7, 'show': 7, 'coach': 7, 'mp': 7, 'black': 7, 'style': 7,
  'dating': 6, 'graphics': 6, 'hamburg': 6, 'run': 6, 'kitchen': 6,
  'gallery': 6, 'vision': 6, 'nagoya': 6, 'vegas': 6, 'taxi': 6, 'pet': 6,
  'menu': 6, 'ooo': 6, 'kiwi': 6, 'clinic': 6, 'ax': 6, 'dog': 6, 'vi': 5,
  'best': 5, 'wedding': 5, 'place': 5, 'srl': 5, 'neustar': 5, 'law': 5,
  'ski': 5, 'abbott': 5, 'express': 5, 'ren': 5, 'lat': 5, 'hm': 5,
  'football': 5, 'gold': 5, 'recipes': 5, 'joburg': 5, 'vote': 5,
  'university': 5, 'hosting': 5, 'cern': 5, 'partners': 5, 'ne': 5,
  'engineering': 5, 'wf': 5, 'desi': 4, 'surf': 4, 'saarland': 4,
  'repair': 4, 'wine': 4, 'gop': 4, 'money': 4, 'ventures': 4, 'camera': 4,
  'bnpparibas': 4, 'band': 4, 'aq': 4, 'basketball': 4, 'training': 4,
  'quebec': 4, 'sb': 4, 'pink': 4, 'ck': 4, 'africa': 4, 'rip': 4,
  'careers': 4, 'management': 4, 'forsale': 4, 'film': 4, 'bj': 4,
  'build': 4, 'fish': 4, 'kp': 4, 'bar': 4, 'porn': 4, 'game': 4,
  'boutique': 4, 'frl': 4, 'corsica': 4, 'gmbh': 4, 'school': 4, 'eco': 4,
  'construction': 3, 'green': 3, 'kn': 3, 'fashion': 3, 'yoga': 3,
  'productions': 3, 'tp': 3, 'shoes': 3, 'gift': 3, 'lgbt': 3,
  'xn--d1acj3b': 3, 'krd': 3, 'cw': 3, 'barcelona': 3, 'kaufen': 3, 'sex': 3,
  'tours': 3, 'haus': 3, 'how': 3, 'gratis': 3, 'auto': 3, 'rest': 3,
  'golf': 3, 'solar': 3, 'sandvik': 3, 'realtor': 3, 'industries': 3,
  'futbol': 3, 'gent': 3, 'ipaddr': 2, 'nico': 2, 'xn--80asehdb': 2,
  'jetzt': 2, 'attorney': 2, 'canon': 2, 'tattoo': 2, 'cards': 2,
  'vlaanderen': 2, 'rehab': 2, 'lawyer': 2, 'delivery': 2, 'diamonds': 2,
  'immo': 2, 'estate': 2, 'clothing': 2, 'direct': 2, 'km': 2, 'car': 2,
  'an': 2, 'app': 2, 'college': 2, 'aw': 2, 'archi': 2, 'moda': 2,
  'barclays': 2, 'gf': 2, 'cologne': 2, 'td': 2, 'bingo': 2, 'aws': 2,
  'toys': 2, 'bot': 2, 'dental': 2, 'dance': 2, 'cam': 2, 'xn--6frz82g': 2,
  'cars': 2, 'apple': 2, 'exposed': 2, 'supply': 2, 'melbourne': 2,
  'hockey': 2, 'tirol': 2, 'xn--90a3ac': 2, 'vet': 2, 'healthcare': 2,
  'active': 2, 'rio': 2, 'furniture': 2, 'holdings': 2, 'kred': 2,
  'equipment': 2, 'dev': 2, 'post': 2, 'study': 2, 'town': 2, 'glass': 2,
  'parts': 1, 'abc': 1, 'tube': 1, 'finance': 1, 'tax': 1, 'bargains': 1,
  'computer': 1, 'fage': 1, 'cruises': 1, 'flickr': 1, 'monash': 1, 'hiv': 1,
  'dhl': 1, 'vodka': 1, 'xn--c1avg': 1, 'barclaycard': 1, 'vin': 1,
  'xn--80ao21a': 1, 'lr': 1, 'theatre': 1, 'new': 1, 'citic': 1,
  'financial': 1, 'bradesco': 1, 'fast': 1, 'contractors': 1, 'democrat': 1,
  'leclerc': 1, 'hot': 1, 'army': 1, 'shiksha': 1, 'goog': 1,
  'xn--3ds443g': 1, 'goo': 1, 'um': 1, 'hitachi': 1, 'ing': 1,
  'properties': 1, 'ipiranga': 1, 'youtube': 1, 'free': 1, 'pharmacy': 1,
  'property': 1, 'career': 1, 'xn--80aswg': 1, 'rentals': 1, 'kyoto': 1,
  'builders': 1, 'tickets': 1, 'ismaili': 1, 'java': 1, 'koeln': 1,
  'garden': 1, 'jcb': 1, 'you': 1, 'box': 1, 'schmidt': 1, 'sncf': 1,
  'ltda': 1, 'cleaning': 1, 'fk': 1, 'country': 1, 'pioneer': 1, 'weir': 1,
  'engineer': 1, 'uol': 1, 'mortgage': 1, 'alsace': 1, 'restaurant': 1,
  'limited': 1, 'yahoo': 1, 'here': 1, 'health': 1, 'bible': 1, 'weber': 1,
  'sky': 1, 'miami': 1, 'arab': 1, 'forum': 1, 'komatsu': 1, 'saxo': 1,
  'mh': 1, 'hiphop': 1, 'trust': 1, 'soccer': 1, 'sener': 1, 'reise': 1,
  'supplies': 1, 'sbi': 1, 'qpon': 1, 'radio': 1, 'bbc': 1, 'juegos': 1,
  'markets': 1, 'florist': 1, 'discount': 1, 'yachts': 1, 'capetown': 1,
  'luxury': 1, 'big': 1, 'security': 1, 'ruhr': 1, 'baidu': 1, 'rent': 1,
  'adult': 1, 'theater': 1, 'catering': 1, 'dentist': 1, 'enterprises': 1,
  'beer': 1, 'gn': 1, 'buy': 1, 'xn--55qx5d': 1, 'hospital': 1, 'gu': 1,
  'immobilien': 1, 'microsoft': 1, 'tel': 1, 'sony': 1, 'cuisinella': 1,
  'pictet': 1, 'casa': 1, 'lidl': 1, 'cs': 1, 'lighting': 1, 'cg': 1,
  'jll': 1, 'bv': 1, 'apartments': 1, 'doctor': 1,
}
