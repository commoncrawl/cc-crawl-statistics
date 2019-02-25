# derived from
#   http://downloads.majestic.com/majestic_million.csv
# fetched 2019-02-06
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
  'date': '2019-02-06',
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
  'com': 495190, 'org': 72365, 'net': 44704, 'ru': 43014, 'cn': 29361,
  'uk': 25616, 'de': 23928, 'jp': 15220, 'pl': 11514, 'nl': 11167,
  'info': 10601, 'it': 9829, 'fr': 9542, 'br': 8905, 'au': 8457,
  'club': 8136, 'tw': 7140, 'us': 6584, 'ca': 6393, 'in': 6014, 'co': 5533,
  'es': 5240, 'eu': 4791, 'ua': 4010, 'edu': 3975, 'cz': 3689, 'se': 3549,
  'ch': 3285, 'ir': 3220, 'vn': 3156, 'biz': 3050, 'be': 2827, 'ro': 2817,
  'at': 2743, 'za': 2550, 'nu': 2428, 'dk': 2396, 'hu': 2252, 'tr': 2154,
  'gr': 2110, 'top': 2105, 'io': 2064, 'me': 2057, 'tv': 2017, 'xyz': 1881,
  'gov': 1721, 'xn--p1ai': 1715, 'site': 1668, 'mx': 1636, 'no': 1631,
  'cc': 1559, 'fi': 1497, 'nz': 1481, 'ar': 1478, 'cl': 1463, 'kr': 1435,
  'mobi': 1406, 'ie': 1322, 'pt': 1285, 'cf': 1258, 'by': 1157, 'il': 1133,
  'id': 1109, 'my': 1085, 'sk': 1073, 'online': 1057, 'kz': 1014, 'tk': 1012,
  'su': 904, 'hk': 877, 'store': 849, 'lt': 836, 'sg': 827, 'pro': 720,
  'hr': 650, 'pw': 646, 'space': 602, 'pk': 568, 'ng': 566, 'th': 530,
  'shop': 528, 'lv': 525, 'live': 514, 'gq': 505, 'ee': 504, 'doctor': 502,
  'icu': 487, 'si': 487, 'cat': 480, 'world': 478, 'ph': 461, 'rs': 445,
  'ae': 444, 'name': 443, 'bg': 432, 'to': 429, 'pe': 420, 'life': 403,
  'ga': 401, 'ws': 367, 'is': 362, 'xn--fiqs8s': 355, 'ml': 353, 'fm': 326,
  'ke': 317, 'fun': 296, 'sa': 279, 'win': 270, 'ma': 261, 'website': 260,
  'video': 255, 'ge': 252, 'md': 251, 'bid': 247, 'stream': 232, 'uz': 232,
  'ovh': 231, 'asia': 228, 'lk': 220, 'az': 220, 'am': 218, 'bd': 216,
  'reisen': 207, 'ec': 206, 'tech': 206, 'news': 205, 've': 198, 'mk': 193,
  'ba': 186, 'ooo': 185, 'np': 175, 'uy': 174, 'lu': 172, 'today': 169,
  'vip': 167, 'science': 166, 'travel': 162, 'work': 160, 'ly': 150,
  'men': 147, 'ai': 147, 'network': 144, 'im': 139, 'la': 138, 'review': 136,
  'tn': 136, 'aero': 131, 'ltd': 129, 'bz': 127, 'ink': 127, 'do': 126,
  'int': 123, 'coop': 123, 'st': 119, 'trade': 118, 'al': 117, 'guru': 116,
  'press': 114, 'services': 114, 'eg': 113, 'mn': 112, 'host': 108,
  'kg': 105, 'media': 104, 'cy': 98, 'li': 95, 'py': 93, 'webcam': 92,
  'party': 92, 'zw': 90, 'link': 89, 'wiki': 89, 'one': 86, 'cx': 86,
  'mil': 85, 'company': 81, 'eus': 80, 'mo': 80, 'global': 77, 'tz': 75,
  'cu': 75, 'gt': 74, 'tel': 73, 'blog': 72, 'gdn': 72, 'cr': 71, 'ms': 71,
  'mt': 70, 'sh': 69, 'gs': 68, 'rocks': 67, 'gg': 67, 'vc': 66, 'jo': 66,
  'lb': 65, 'zone': 65, 'bo': 65, 'ag': 63, 'cricket': 62, 'tips': 62,
  'so': 62, 'ps': 60, 'team': 60, 'ug': 59, 'center': 57, 'qa': 57,
  'accountant': 55, 'ninja': 55, 'pub': 55, 'agency': 55, 'dz': 54, 'tc': 53,
  'vu': 53, 're': 52, 'tj': 51, 'city': 51, 'xxx': 50, 'blue': 47,
  'moscow': 47, 'ac': 46, 'kh': 45, 'xn--p1acf': 45, 'london': 45,
  'design': 45, 'gh': 45, 'tt': 44, 'group': 44, 'mu': 44, 'sc': 44,
  'app': 43, 'cm': 42, 'studio': 41, 'click': 40, 'af': 40, 'nyc': 40,
  'tokyo': 39, 'pet': 39, 'movie': 38, 'tools': 38, 'directory': 38,
  'art': 38, 'promo': 37, 'as': 37, 'date': 36, 'social': 36, 'digital': 35,
  'pink': 35, 'sn': 35, 'wang': 35, 'cloud': 35, 'wales': 35, 'vg': 35,
  'pa': 34, 'scot': 33, 'college': 33, 'bio': 33, 'sv': 33, 'na': 33,
  'download': 32, 'bt': 32, 'rent': 32, 'ni': 32, 'band': 31, 'mz': 31,
  'kw': 31, 'toys': 31, 'museum': 30, 'cd': 30, 'jobs': 30, 'rw': 30,
  'bw': 30, 'va': 29, 'education': 29, 'hn': 29, 'solutions': 29, 'gd': 29,
  'actor': 29, 'mv': 29, 'systems': 28, 'om': 28, 'auction': 28,
  'schule': 27, 'expert': 27, 'community': 27, 'guide': 27, 'gal': 27,
  'love': 26, 'mg': 26, 'games': 26, 'ci': 26, 'tl': 26, 'mba': 26, 'gl': 26,
  'plus': 26, 'nf': 25, 'works': 25, 'et': 25, 'bet': 25, 'mc': 25,
  'paris': 25, 'loan': 24, 'zm': 24, 'yu': 24, 'berlin': 24, 'market': 24,
  'fund': 24, 'sy': 24, 'ht': 23, 'help': 23, 'nrw': 23, 'bh': 22,
  'events': 22, 'xn--80adxhks': 22, 'red': 22, 'gy': 21, 'support': 21,
  'cash': 21, 'iq': 21, 'dj': 20, 'gm': 20, 'technology': 20, 'fj': 20,
  'ao': 20, 'academy': 20, 'fail': 19, 'school': 19, 'ad': 19, 'faith': 19,
  'swiss': 19, 'foundation': 19, 'run': 19, 'moe': 18, 'fo': 18, 'nc': 18,
  'pn': 18, 'bzh': 18, 'pm': 18, 'racing': 17, 'xn--90ais': 17,
  'reviews': 17, 'exchange': 17, 'cv': 17, 'land': 17, 'gi': 16, 'ren': 16,
  'jm': 16, 'google': 16, 'cars': 16, 'sm': 16, 'email': 16, 'tf': 16,
  'ky': 16, 'mw': 15, 'sx': 15, 'coffee': 15, 'software': 15, 'cafe': 15,
  'sd': 15, 'bb': 15, 'xn--j1amh': 15, 'pg': 15, 'pr': 15, 'gallery': 14,
  'care': 14, 'poker': 14, 'bf': 14, 'xin': 14, 'amsterdam': 14, 'codes': 13,
  'earth': 13, 'uno': 13, 'sr': 13, 'gp': 13, 'church': 13, 'pics': 13,
  'brussels': 13, 'mm': 12, 'bm': 12, 'capital': 12, 'cool': 12,
  'institute': 12, 'ls': 12, 'photo': 12, 'international': 12, 'tm': 12,
  'je': 11, 'chat': 11, 'bike': 11, 'africa': 11, 'istanbul': 11,
  'photos': 11, 'show': 11, 'money': 11, 'onl': 11, 'pf': 11, 'casino': 11,
  'consulting': 11, 'camp': 11, 'report': 11, 'mr': 11, 'lc': 10,
  'finance': 10, 'photography': 10, 'clinic': 10, 'tours': 10,
  'graphics': 10, 'yt': 10, 'bi': 10, 'town': 10, 'legal': 10, 'bank': 9,
  'marketing': 9, 'ngo': 9, 'farm': 9, 'bn': 9, 'kim': 9, 'dm': 9, 'ax': 9,
  'abbott': 9, 'xn--80asehdb': 9, 'bayern': 9, 'tg': 9, 'energy': 9,
  'porn': 8, 'sale': 8, 'lol': 8, 'bs': 8, 'nr': 8, 'pictures': 8, 'cymru': 8,
  'fyi': 8, 'business': 8, 'ye': 8, 'deals': 8, 'audio': 8, 'rest': 7,
  'ki': 7, 'game': 7, 'buzz': 7, 'sexy': 7, 'hm': 7, 'fit': 7, 'sex': 7,
  'film': 7, 'domains': 7, 'ski': 7, 'coach': 7, 'best': 7, 'barcelona': 7,
  'taipei': 7, 'style': 7, 'dev': 7, 'sz': 7, 'sl': 7, 'fitness': 7,
  'house': 7, 'law': 7, 'place': 7, 'fish': 6, 'eco': 6, 'express': 6,
  'basketball': 6, 'canon': 6, 'parts': 6, 'ne': 6, 'realtor': 6, 'green': 6,
  'vi': 6, 'direct': 6, 'cg': 6, 'ist': 6, 'hosting': 6, 'recipes': 6,
  'engineering': 6, 'wtf': 6, 'partners': 6, 'training': 6, 'engineer': 6,
  'vision': 6, 'bj': 6, 'gratis': 6, 'mp': 6, 'kiwi': 6, 'gop': 5,
  'properties': 5, 'delivery': 5, 'tirol': 5, 'watch': 5, 'cern': 5,
  'careers': 5, 'sb': 5, 'estate': 5, 'joburg': 5, 'football': 5, 'koeln': 5,
  'desi': 5, 'bar': 5, 'wien': 5, 'vote': 5, 'hamburg': 5, 'wf': 5,
  'camera': 5, 'neustar': 5, 'fashion': 5, 'weber': 5, 'mom': 5, 'taxi': 4,
  'corsica': 4, 'university': 4, 'surf': 4, 'kp': 4, 'shoes': 4, 'wine': 4,
  'dating': 4, 'kn': 4, 'lgbt': 4, 'health': 4, 'bnpparibas': 4, 'vegas': 4,
  'beer': 4, 'rip': 4, 'repair': 4, 'productions': 4, 'vet': 4, 'gold': 4,
  'family': 4, 'gift': 4, 'aq': 4, 'saarland': 4, 'srl': 4, 'dance': 4,
  'dental': 4, 'supply': 4, 'how': 4, 'solar': 3, 'casa': 3, 'build': 3,
  'tp': 3, 'pizza': 3, 'construction': 3, 'cab': 3, 'flowers': 3,
  'credit': 3, 'jetzt': 3, 'xn--6qq986b3xl': 3, 'futbol': 3, 'garden': 3,
  'boutique': 3, 'cheap': 3, 'pharmacy': 3, 'frl': 3, 'gifts': 3, 'yoga': 3,
  'quebec': 3, 'auto': 3, 'builders': 3, 'xn--d1acj3b': 3, 'cards': 3,
  'lat': 3, 'lighting': 3, 'sandvik': 3, 'villas': 3, 'krd': 3, 'ck': 3,
  'tube': 3, 'sport': 3, 'xn--3ds443g': 3, 'sydney': 3, 'clothing': 3,
  'lawyer': 3, 'archi': 3, 'brother': 2, 'army': 2, 'barclays': 2,
  'discount': 2, 'aws': 2, 'hockey': 2, 'alsace': 2, 'an': 2, 'mortgage': 2,
  'rio': 2, 'kpmg': 2, 'km': 2, 'restaurant': 2, 'dog': 2, 'menu': 2,
  'cam': 2, 'catering': 2, 'moda': 2, 'active': 2, 'yokohama': 2,
  'vlaanderen': 2, 'haus': 2, 'apple': 2, 'komatsu': 2, 'xn--6frz82g': 2,
  'shiksha': 2, 'black': 2, 'kred': 2, 'bot': 2, 'tattoo': 2, 'gf': 2,
  'golf': 2, 'miami': 2, 'hiv': 2, 'vin': 2, 'guitars': 2, 'physio': 2,
  'post': 2, 'healthcare': 2, 'xn--80aswg': 2, 'tax': 2, 'kitchen': 2,
  'tatar': 2, 'broker': 2, 'equipment': 2, 'nico': 2, 'xn--e1a4c': 2,
  'nagoya': 2, 'forsale': 2, 'contractors': 2, 'kyoto': 2, 'diamonds': 2,
  'immobilien': 2, 'page': 2, '" "': 2, 'industries': 2, 'radio': 2,
  'horse': 2, 'okinawa': 2, 'holiday': 2, 'luxury': 2, 'loans': 2,
  'citic': 1, 'enterprises': 1, 'vanguard': 1, 'kaufen': 1, 'sbi': 1,
  'surgery': 1, 'yandex': 1, 'fast': 1, 'sony': 1, 'tickets': 1,
  'dentist': 1, 'associates': 1, 'schmidt': 1, 'kpn': 1, 'bingo': 1,
  'new': 1, 'glass': 1, 'security': 1, 'property': 1, 'financial': 1,
  'gu': 1, 'holdings': 1, 'diet': 1, 'gmail': 1, 'gw': 1, 'forum': 1,
  'bible': 1, 'investments': 1, 'fans': 1, 'gent': 1, 'abc': 1,
  'barclaycard': 1, 'fage': 1, 'here': 1, 'theater': 1, 'realestate': 1,
  'attorney': 1, 'xn--3e0b707e': 1, 'markets': 1, 'mq': 1, 'goo': 1,
  'reise': 1, 'box': 1, 'ismaili': 1, 'fan': 1, 'rentals': 1, 'irish': 1,
  'gn': 1, 'florist': 1, 'td': 1, 'hitachi': 1, 'goog': 1, 'exposed': 1,
  'flickr': 1, 'rehab': 1, 'monash': 1, 'voyage': 1, 'computer': 1, 'you': 1,
  'uol': 1, 'cs': 1, 'pioneer': 1, 'limo': 1, 'bradesco': 1, 'madrid': 1,
  'flights': 1, 'bbc': 1, 'dhl': 1, 'juegos': 1, 'free': 1, 'leclerc': 1,
  'jll': 1, 'lidl': 1, 'cuisinella': 1, 'edeka': 1, 'cologne': 1, 'cw': 1,
  'hot': 1, 'honda': 1, 'immo': 1, 'ipiranga': 1, 'youtube': 1, 'jewelry': 1,
  'saxo': 1, 'sncf': 1, 'baidu': 1, 'charity': 1, 'softbank': 1, 'jcb': 1,
  'audi': 1, 'bv': 1, 'rmit': 1, 'shopping': 1, 'java': 1, 'rwe': 1, 'ses': 1,
  'fk': 1, 'ruhr': 1, 'xn--kpry57d': 1, 'gmbh': 1, 'weir': 1, 'pictet': 1,
  'furniture': 1, 'melbourne': 1, 'rugby': 1, 'wedding': 1, 'ltda': 1,
  'supplies': 1, 'trust': 1, 'vodka': 1, 'yahoo': 1, 'management': 1,
  'microsoft': 1, 'big': 1, 'sener': 1, 'theatre': 1, 'mobile': 1,
  'office': 1, 'soccer': 1, 'car': 1, 'qpon': 1, 'buy': 1, 'map': 1,
  'lixil': 1, 'chrome': 1, 'hiphop': 1, 'study': 1, 'sky': 1, 'lr': 1,
}
