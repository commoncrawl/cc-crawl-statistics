# derived from
#   http://downloads.majestic.com/majestic_million.csv
# fetched 2017-06-12
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
 'date':'2017-06-12'
}
majestic_top_1m_tlds = {
 # cut -d, -f4 majestic_million.csv | tail -n+2 \
 #  | perl -ne 'chomp; $h{$_}++; 
 #              END { print "\047", $_, "\047:", $h{$_}, ", " for sort { $h{$b} <=> $h{$a} } keys %h }' \
 #  | fold -s
 'com':499246, 'org':69105, 'net':48370, 'ru':46265, 'de':34933, 'cn':26685, 
 'uk':24010, 'jp':16300, 'pl':14826, 'info':11723, 'it':11013, 'nl':10727, 
 'fr':9124, 'au':7968, 'br':7776, 'us':6065, 'top':6004, 'eu':6003, 'ca':5884, 
 'es':4950, 'in':4775, 'ua':4068, 'edu':3930, 'cz':3904, 'co':3695, 'se':3529, 
 'ch':3306, 'at':3300, 'tw':2878, 'ro':2840, 'xyz':2826, 'be':2822, 'biz':2775, 
 'gr':2445, 'hu':2445, 'ir':2365, 'tr':2285, 'za':2211, 'dk':2197, 'vn':2117, 
 'cc':2040, 'tv':2005, 'no':1633, 'me':1616, 'mx':1592, 'kr':1585, 'ar':1569, 
 'gov':1538, 'xn--p1ai':1514, 'gdn':1384, 'fi':1376, 'cl':1297, 'nz':1294, 
 'ie':1241, 'by':1182, 'pw':1154, 'bid':1152, 'science':1127, 'pt':1121, 
 'sk':1069, 'nu':1036, 'hk':1003, 'il':973, 'io':938, 'my':924, 'site':917, 
 'club':916, 'su':907, 'kz':900, 'cricket':898, 'party':856, 'lt':830, 
 'pro':803, 'sg':792, 'trade':780, 'webcam':712, 'review':663, 'tk':653, 
 'id':608, 'hr':595, 'click':595, 'mobi':564, 'online':554, 'link':540, 
 'th':501, 'lv':483, 'ovh':458, 'name':456, 'si':448, 'pk':446, 'ee':442, 
 'to':424, 'bg':413, 'rs':404, 'ph':401, 'cat':392, 'pe':384, 'ae':361, 
 'ws':351, 'tech':344, 'website':341, 'date':341, 'life':326, 'is':319, 
 'ng':312, 'fm':305, 'win':298, 'accountant':283, 'ga':273, 'ke':265, 'md':249, 
 'space':243, 'sa':243, 'np':237, 'ma':223, 'ec':214, 'stream':211, 'asia':210, 
 'men':209, 'lk':196, 'ge':195, 'am':191, 'red':186, 'uz':181, 've':167, 
 'az':164, 'mk':163, 'ba':156, 'travel':151, 'la':150, 'gq':149, 'kim':147, 
 'uy':147, 'ly':143, 'bd':141, 'lu':140, 'ml':139, 'bz':136, 'im':135, 
 'sexy':130, 'tn':130, 'faith':128, 'news':122, 'st':120, 'do':119, 'int':117, 
 'cf':115, 'download':114, 'today':108, 'mn':107, 'christmas':105, 
 'fashion':104, 'coop':102, 'press':102, 'loan':101, 'zw':99, 'store':98, 
 'cy':97, 'host':95, 'eg':94, 'so':92, 'aero':91, 'mom':88, 'li':88, 'kg':85, 
 'mil':82, 'cx':81, 'wiki':80, 'al':79, 'bo':79, 'mo':77, 'casa':75, 'desi':72, 
 'world':72, 'cr':72, 'cu':71, 'py':68, 'ms':67, 'vip':67, 'jo':66, 'ag':65, 
 'vc':63, 'gs':63, 'guru':62, 'lol':61, 'shop':60, 'work':60, 'lb':60, 'vu':59, 
 'cm':57, 'sh':57, 'ps':56, 'center':56, 'ug':54, 'qa':52, 'live':49, 'mt':48, 
 'city':48, 'ai':47, 'gt':46, 'dz':46, 'tj':46, 'tz':45, 'tt':45, 'gh':45, 
 'ac':44, 'media':43, 'fund':42, 'mu':42, 'company':42, 'wang':41, 'kh':41, 
 'zone':41, 'solutions':41, 're':40, 'ninja':40, 'xxx':39, 'as':39, 'gg':38, 
 'tc':38, 'rocks':38, 'directory':38, 'sc':38, 'photography':37, 'eus':36, 
 'global':36, 'cool':33, 'tokyo':33, 'one':33, 'kw':33, 'af':32, 'email':31, 
 'mz':31, 'group':31, 'sn':30, 'ci':30, 'fail':30, 'london':29, 'cd':29, 
 'moscow':29, 'coffee':29, 'blog':29, 'bike':29, 'na':29, 'works':28, 'pn':28, 
 'tl':28, 'services':28, 'racing':28, 'museum':27, 'business':27, 'hn':27, 
 'tools':27, 'systems':27, 'fyi':27, 'nyc':26, 'gold':26, 'ni':26, 'gd':26, 
 'schule':26, 'sv':26, 'design':26, 'gl':25, 'vg':25, 'yu':24, 'pa':24, 
 'cheap':24, 'camera':24, 'pub':24, 'mg':24, 'va':24, 'xn--p1acf':23, 'tips':23, 
 'nc':23, 'nf':23, 'express':23, 'sucks':23, 'bw':23, 'berlin':23, 'jobs':22, 
 'ltd':22, 'help':22, 'bargains':22, 'cash':22, 'credit':22, 'zm':22, 
 'jetzt':22, 'reisen':21, 'exposed':21, 'paris':21, 'scot':21, 'network':21, 
 'associates':21, 'movie':21, 'om':21, 'reise':20, 'education':20, 'bh':20, 
 'wales':20, 'gripe':20, 'mba':20, 'mc':20, 'shopping':20, 'ad':20, 'mw':20, 
 'xn--80adxhks':19, 'academy':19, 'expert':19, 'gy':19, 'iq':19, 'gal':19, 
 'et':19, 'ao':19, 'dj':18, 'bzh':18, 'ren':17, 'ht':17, 'agency':17, 
 'reviews':17, 'sy':16, 'bt':16, 'gp':15, 'cloud':15, 'pr':15, 'ink':15, 
 'cv':15, 'moe':14, 'digital':14, 'fj':14, 'pg':14, 'rw':14, 'pm':14, 'sx':14, 
 'jm':14, 'bm':14, 'sd':14, 'tm':13, 'events':13, 'mm':13, 'sm':13, 'uno':13, 
 'ky':13, 'mv':13, 'bi':13, 'bio':13, 'video':13, 'gm':13, 'tf':12, 'onl':12, 
 'community':12, 'fo':12, 'report':12, 'bn':12, 'art':12, 'blue':12, 'mr':12, 
 'social':12, 'je':12, 'land':11, 'bb':11, 'nrw':11, 'gi':11, 'chat':11, 
 'wien':11, 'market':11, 'technology':11, 'bayern':10, 'gallery':10, 'yt':10, 
 'plus':10, 'nr':10, 'lc':10, 'black':10, 'pf':10, 'studio':10, 'photo':10, 
 'bf':9, 'xn--j1amh':9, 'ls':9, 'sr':9, 'dm':9, 'consulting':9, 'xn--fiqs8s':9, 
 'guide':8, 'marketing':8, 'ngo':8, 'house':8, 'brussels':8, 'foundation':8, 
 'google':8, 'xin':8, 'ki':8, 'money':7, 'love':7, 'farm':7, 'xn--90ais':7, 
 'institute':7, 'camp':7, 'properties':7, 'sz':7, 'photos':7, 'buzz':7, 
 'school':7, 'sydney':7, 'amsterdam':7, 'okinawa':7, 'ax':7, 'taipei':6, 
 'istanbul':6, 'sl':6, 'church':6, 'hm':6, 'ooo':6, 'vegas':6, 'watch':6, 
 'care':6, 'ye':6, 'deals':6, 'pictures':6, 'bs':6, 'energy':6, 'cymru':6, 
 'pet':5, 'games':5, 'law':5, 'training':5, 'fitness':5, 'tours':5, 'run':5, 
 'xn--80asehdb':5, 'vi':5, 'support':5, 'quebec':5, 'fit':5, 'international':5, 
 'earth':5, 'ne':5, 'best':5, 'taxi':5, 'place':5, 'mp':4, 'football':4, 
 'audio':4, 'fish':4, 'srl':4, 'estate':4, 'discount':4, 'hamburg':4, 'ist':4, 
 'sb':4, 'gratis':4, 'xn--c1avg':4, 'codes':4, 'clinic':4, 'swiss':4, 'ck':4, 
 'direct':4, 'menu':4, 'management':4, 'poker':4, 'rest':4, 'cern':4, 'pics':4, 
 'porn':4, 'team':4, 'recipes':4, 'bnpparibas':4, 'forsale':4, 'bj':4, 'tg':4, 
 'haus':4, 'kp':4, 'immo':4, 'band':4, 'glass':3, 'corsica':3, 'contractors':3, 
 'wf':3, 'golf':3, 'kiwi':3, 'legal':3, 'rip':3, 'vet':3, 'gent':3, 'tel':3, 
 'bar':3, 'dance':3, 'family':3, 'rent':3, 'tp':3, 'restaurant':3, 'saarland':3, 
 'wtf':3, 'abbott':3, 'xn--6frz82g':3, 'toys':3, 'coach':3, 'tax':3, 
 'vlaanderen':3, 'melbourne':3, 'gop':3, 'hosting':3, 'archi':3, 'sale':3, 
 'university':3, 'kn':3, 'style':3, 'aq':3, 'productions':3, 'careers':3, 
 'study':3, 'nagoya':3, 'realtor':3, 'graphics':3, 'bank':3, 'wine':3, 'cam':2, 
 'supply':2, 'sex':2, 'cafe':2, 'diet':2, 'frl':2, 'ski':2, 'cw':2, 'td':2, 
 'engineering':2, 'film':2, 'barclays':2, 'construction':2, 'post':2, 
 'equipment':2, 'build':2, 'pink':2, 'domains':2, 'jcb':2, 'vote':2, 
 'coupons':2, 'ceo':2, 'kred':2, 'capetown':2, 'capital':2, 'koeln':2, 
 'ipaddr':2, 'rio':2, 'how':2, 'computer':2, 'clothing':2, 'joburg':2, 'yoga':2, 
 'tirol':2, 'aws':2, 'show':2, 'an':2, 'kitchen':2, 'alsace':2, 'lgbt':2, 
 'lighting':2, 'plumbing':1, 'republican':1, 'game':1, 'hiphop':1, 'qpon':1, 
 'vacations':1, 'uol':1, 'mortgage':1, 'cologne':1, 'neustar':1, 'healthcare':1, 
 'lidl':1, 'moda':1, 'tienda':1, 'ruhr':1, 'fage':1, 'rentals':1, 'dog':1, 
 'goo':1, 'futbol':1, 'yahoo':1, 'industries':1, 'boutique':1, 'furniture':1, 
 'xn--io0a7i':1, 'bible':1, 'abogado':1, 'flights':1, 'xn--80aswg':1, 'abc':1, 
 'eco':1, 'jll':1, 'college':1, 'apple':1, 'hot':1, 'monash':1, 'xn--tckwe':1, 
 'democrat':1, 'canon':1, 'xn--3ds443g':1, 'bet':1, 'casino':1, 'supplies':1, 
 'sandvik':1, 'tattoo':1, 'beer':1, 'immobilien':1, 'big':1, 'rehab':1, 
 'nico':1, 'gmbh':1, 'catering':1, 'pharmacy':1, 'you':1, 'lat':1, 'flickr':1, 
 'gu':1, 'solar':1, 'free':1, 'bradesco':1, 'doctor':1, 'fast':1, 'town':1, 
 'dentist':1, 'physio':1, 'er':1, 'voyage':1, 'lr':1, 'cg':1, 'microsoft':1, 
 'finance':1, 'gn':1, 'saxo':1, 'pictet':1, 'weir':1, 'cards':1, 'kinder':1, 
 'baidu':1, 'garden':1, 'vision':1, 'new':1, 'auto':1, 'bingo':1, 'dental':1, 
 'active':1, 'shoes':1, 'ryukyu':1, 'trust':1, 'youtube':1, 'fk':1, 'box':1, 
 'xn--6qq986b3xl':1, 'dating':1, 'here':1, 'juegos':1, 'builders':1, 'luxury':1, 
 'soccer':1, 'insure':1, 'holiday':1, 'car':1, 'markets':1, 'bbc':1, 'cs':1, 
 'goog':1, 'um':1, 'xn--d1acj3b':1, 'eh':1, 'parts':1, 'attorney':1, 'buy':1, 
 'barclaycard':1, 'surgery':1, 'flowers':1, 'exchange':1, 'theater':1, 
 'forum':1, 'sener':1, 'krd':1, 'enterprises':1, 'xn--55qx5d':1, 
 'blackfriday':1, 'km':1, 'aw':1, 
}
