import fileinput
import idna
import re


class TopLevelDomain:
    """Classify top-level domains (TLDs) to provide the following information:
- type: generic, country-code, ...
- """

    tld_ccs = {}
    tld_types = {}
    short_types = {'generic': 'gTLD',
                   'generic-restricted': 'grTLD',
                   'infrastructure': 'ARPA',
                   'country-code': 'ccTLD',
                   'sponsored': 'sTLD',
                   'test': 'tTLD',
                   'internationalized generic': 'IDN gTLD',
                   'internationalized country-code TLD': 'IDN ccTLD',
                   'internationalized test TLD': 'IDN tTLD'
                   }

    def __init__(self, tld):
        self.tld = tld = tld.lower()
        self.first_level = self.tld
        self.tld_type = None
        self.sub_type = None
        if tld in TopLevelDomain.tld_ccs:
            self.first_level = TopLevelDomain.tld_ccs[tld]
        elif tld.find('.'):
            self.first_level = re.sub(r'^.+\.', '', tld)
        if tld in TopLevelDomain.tld_types:
            self.tld_type = TopLevelDomain.tld_types[tld]
        elif tld in TopLevelDomain.tld_ccs:
            self.tld_type = 'country-code'
            self.sub_type = 'internationalized'
            self.first_level = TopLevelDomain.tld_ccs[tld]
        elif self.first_level in TopLevelDomain.tld_types:
            self.tld_type = TopLevelDomain.tld_types[self.first_level]
            self.sub_type = 'second-level'

    def __str__(self):
        _str = self.tld + '('
        if self.tld_type:
            _str += self.tld_type
        if self.sub_type:
            _str += ', ' + self.sub_type
        if self.first_level and self.first_level != self.tld:
            _str += ' of ' + self.first_level
        idn = idna.encode(self.tld).decode('utf-8')
        if idn != self.tld:
            _str += ', idn: ' + idn
        _str += ')'
        return _str

    @staticmethod
    def _read_data():
        state = ''
        state_pattern = re.compile('^__([A-Z_]+)__$')
        for line in TopLevelDomain.__DATA__.splitlines():
            # print(line)
            if len(line) == 0 or '#' == line[0]:
                continue
            m = state_pattern.match(line)
            if m:
                state = m.group(1)
                continue
            if state == 'IANA':
                (tld, tld_type, _sponsoring_organization) = line.split('\t')
                tld = tld.strip('\u200e\u200f')
                tld = tld.lstrip('.')
                idn = idna.encode(tld).decode('utf-8')
                if idn != tld:
                    if tld_type == 'country-code':
                        tld_type = 'internationalized country-code TLD'
                    else:
                        tld_type = 'internationalized ' + tld_type
                    TopLevelDomain.tld_types[idn] = tld_type
                TopLevelDomain.tld_types[tld] = tld_type
            elif state == 'ICCTLD':
                (dns, idn, _country, _lang, _script,
                 _translit, _comment, cctld, _dnssec) = line.split('\t')
                dns = dns.lstrip('.')
                cctld = cctld.lstrip('.')
                idn = idn.lstrip('.')
                if '[' in idn:
                    # strip Wikipedia footnotes and links
                    idn = re.sub(r'\s*\[.+?\]\s*$', '', idn)
                for tld in (dns, idn):
                    TopLevelDomain.tld_types[tld] \
                        = 'internationalized country-code TLD'
                    TopLevelDomain.tld_ccs[tld] = cctld
            elif state == 'INTERNATIONAL_BRAND_TLD':
                (dns, idn, _entity, _script, _translit,
                 _comments, _dnssec) = line.split('\t')
                dns = dns.lstrip('.')
                idn = idn.lstrip('.')
                TopLevelDomain.tld_types[dns] = 'internationalized generic TLD'
                TopLevelDomain.tld_types[idn] = 'internationalized generic TLD'
            elif state == 'INTERNATIONAL_GEOGRAPHIC_TLD':
                # geographic TLDs (not internationalized) are classified in IANA list as generic
                (dns, idn, _entity, _script, _translit,
                 _comments, _other_tld, _dnssec) = line.split('\t')
                dns = dns.lstrip('.')
                idn = idn.lstrip('.')
                TopLevelDomain.tld_types[dns] = 'internationalized generic TLD'
                TopLevelDomain.tld_types[idn] = 'internationalized generic TLD'
            elif state == 'INTERNATIONAL_TEST_TLD':
                (dns, idn, _translit, _lang, _script, _test) = line.split('\t')
                dns = dns.lstrip('.')
                idn = idn.lstrip('.')
                TopLevelDomain.tld_types[dns] = 'internationalized test TLD'
                TopLevelDomain.tld_types[idn] = 'internationalized test TLD'

    @staticmethod
    def short_type(name):
        if name in TopLevelDomain.short_types:
            return TopLevelDomain.short_types[name]
        return name

    __DATA__ = '''\
__IANA__
# https://www.iana.org/domains/root/db
# (update 2025-01-16)
# Domain	Type	TLD Manager
.aaa	generic	American Automobile Association, Inc.
.aarp	generic	AARP
.abarth	generic	Not assigned
.abb	generic	ABB Ltd
.abbott	generic	Abbott Laboratories, Inc.
.abbvie	generic	AbbVie Inc.
.abc	generic	Disney Enterprises, Inc.
.able	generic	Able Inc.
.abogado	generic	Registry Services, LLC
.abudhabi	generic	Abu Dhabi Systems and Information Centre
.ac	country-code	Internet Computer Bureau Limited
.academy	generic	Binky Moon, LLC
.accenture	generic	Accenture plc
.accountant	generic	dot Accountant Limited
.accountants	generic	Binky Moon, LLC
.aco	generic	ACO Severin Ahlmann GmbH & Co. KG
.active	generic	Not assigned
.actor	generic	Dog Beach, LLC
.ad	country-code	Andorra Telecom
.adac	generic	Not assigned
.ads	generic	Charleston Road Registry Inc.
.adult	generic	ICM Registry AD LLC
.ae	country-code	Telecommunications and Digital Government Regulatory Authority (TDRA)
.aeg	generic	Aktiebolaget Electrolux
.aero	sponsored	Societe Internationale de Telecommunications Aeronautique (SITA INC USA)
.aetna	generic	Aetna Life Insurance Company
.af	country-code	Ministry of Communications and IT
.afamilycompany	generic	Not assigned
.afl	generic	Australian Football League
.africa	generic	ZA Central Registry NPC trading as Registry.Africa
.ag	country-code	UHSA School of Medicine
.agakhan	generic	Fondation Aga Khan (Aga Khan Foundation)
.agency	generic	Binky Moon, LLC
.ai	country-code	Government of Anguilla
.aig	generic	American International Group, Inc.
.aigo	generic	Not assigned
.airbus	generic	Airbus S.A.S.
.airforce	generic	Dog Beach, LLC
.airtel	generic	Bharti Airtel Limited
.akdn	generic	Fondation Aga Khan (Aga Khan Foundation)
.al	country-code	Electronic and Postal Communications Authority - AKEP
.alfaromeo	generic	Not assigned
.alibaba	generic	Alibaba Group Holding Limited
.alipay	generic	Alibaba Group Holding Limited
.allfinanz	generic	Allfinanz Deutsche Vermögensberatung Aktiengesellschaft
.allstate	generic	Allstate Fire and Casualty Insurance Company
.ally	generic	Ally Financial Inc.
.alsace	generic	REGION GRAND EST
.alstom	generic	ALSTOM
.am	country-code	"Internet Society" Non-governmental Organization
.amazon	generic	Amazon Registry Services, Inc.
.americanexpress	generic	American Express Travel Related Services Company, Inc.
.americanfamily	generic	AmFam, Inc.
.amex	generic	American Express Travel Related Services Company, Inc.
.amfam	generic	AmFam, Inc.
.amica	generic	Amica Mutual Insurance Company
.amsterdam	generic	Gemeente Amsterdam
.an	country-code	Not assigned
.analytics	generic	Campus IP LLC
.android	generic	Charleston Road Registry Inc.
.anquan	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.anz	generic	Australia and New Zealand Banking Group Limited
.ao	country-code	Ministry of Telecommunications and Information Technologies (MTTI)
.aol	generic	Yahoo Inc.
.apartments	generic	Binky Moon, LLC
.app	generic	Charleston Road Registry Inc.
.apple	generic	Apple Inc.
.aq	country-code	Antarctica Network Information Centre Limited
.aquarelle	generic	Aquarelle.com
.ar	country-code	Presidencia de la Nación , Secretaría Legal y Técnica
.arab	generic	League of Arab States
.aramco	generic	Aramco Services Company
.archi	generic	Identity Digital Limited
.army	generic	Dog Beach, LLC
.arpa	infrastructure	Internet Architecture Board (IAB)
.art	generic	UK Creative Ideas Limited
.arte	generic	Association Relative à la Télévision Européenne G.E.I.E.
.as	country-code	AS Domain Registry
.asda	generic	Asda Stores Limited
.asia	sponsored	DotAsia Organisation Ltd.
.associates	generic	Binky Moon, LLC
.at	country-code	nic.at GmbH
.athleta	generic	The Gap, Inc.
.attorney	generic	Dog Beach, LLC
.au	country-code	.au Domain Administration (auDA)
.auction	generic	Dog Beach, LLC
.audi	generic	AUDI Aktiengesellschaft
.audible	generic	Amazon Registry Services, Inc.
.audio	generic	XYZ.COM LLC
.auspost	generic	Australian Postal Corporation
.author	generic	Amazon Registry Services, Inc.
.auto	generic	XYZ.COM LLC
.autos	generic	XYZ.COM LLC
.avianca	generic	Not assigned
.aw	country-code	SETAR
.aws	generic	AWS Registry LLC
.ax	country-code	Ålands landskapsregering
.axa	generic	AXA Group Operations SAS
.az	country-code	IntraNS
.azure	generic	Microsoft Corporation
.ba	country-code	Universtiy Telinformatic Centre (UTIC)
.baby	generic	XYZ.COM LLC
.baidu	generic	Baidu, Inc.
.banamex	generic	Citigroup Inc.
.bananarepublic	generic	Not assigned
.band	generic	Dog Beach, LLC
.bank	generic	fTLD Registry Services, LLC
.bar	generic	Punto 2012 Sociedad Anonima Promotora de Inversion de Capital Variable
.barcelona	generic	Municipi de Barcelona
.barclaycard	generic	Barclays Bank PLC
.barclays	generic	Barclays Bank PLC
.barefoot	generic	Gallo Vineyards, Inc.
.bargains	generic	Binky Moon, LLC
.baseball	generic	MLB Advanced Media DH, LLC
.basketball	generic	Fédération Internationale de Basketball (FIBA)
.bauhaus	generic	Werkhaus GmbH
.bayern	generic	Bayern Connect GmbH
.bb	country-code	Ministry of Innovation, Science and Smart Technology
.bbc	generic	British Broadcasting Corporation
.bbt	generic	BB&T Corporation
.bbva	generic	BANCO BILBAO VIZCAYA ARGENTARIA, S.A.
.bcg	generic	The Boston Consulting Group, Inc.
.bcn	generic	Municipi de Barcelona
.bd	country-code	Posts and Telecommunications Division
.be	country-code	DNS Belgium vzw/asbl
.beats	generic	Beats Electronics, LLC
.beauty	generic	XYZ.COM LLC
.beer	generic	Registry Services, LLC
.bentley	generic	Bentley Motors Limited
.berlin	generic	dotBERLIN GmbH & Co. KG
.best	generic	BestTLD Pty Ltd
.bestbuy	generic	BBY Solutions, Inc.
.bet	generic	Identity Digital Limited
.bf	country-code	Autorité de Régulation des Communications Electroniques et des Postes (ARCEP)
.bg	country-code	Register.BG
.bh	country-code	Telecommunications Regulatory Authority (TRA)
.bharti	generic	Bharti Enterprises (Holding) Private Limited
.bi	country-code	Centre National de l'Informatique
.bible	generic	American Bible Society
.bid	generic	dot Bid Limited
.bike	generic	Binky Moon, LLC
.bing	generic	Microsoft Corporation
.bingo	generic	Binky Moon, LLC
.bio	generic	Identity Digital Limited
.biz	generic-restricted	Registry Services, LLC
.bj	country-code	Autorité de Régulation des Communications Electroniques et de la Poste du Bénin (ARCEP BENIN)
.bl	country-code	Not assigned
.black	generic	Identity Digital Limited
.blackfriday	generic	Registry Services, LLC
.blanco	generic	Not assigned
.blockbuster	generic	Dish DBS Corporation
.blog	generic	Knock Knock WHOIS There, LLC
.bloomberg	generic	Bloomberg IP Holdings LLC
.blue	generic	Identity Digital Limited
.bm	country-code	Registry General Department, Ministry of Home Affairs
.bms	generic	Bristol-Myers Squibb Company
.bmw	generic	Bayerische Motoren Werke Aktiengesellschaft
.bn	country-code	Authority for Info-communications Technology Industry of Brunei Darussalam (AITI)
.bnl	generic	Not assigned
.bnpparibas	generic	BNP Paribas
.bo	country-code	Agencia para el Desarrollo de la Información de la Sociedad en Bolivia
.boats	generic	XYZ.COM LLC
.boehringer	generic	Boehringer Ingelheim International GmbH
.bofa	generic	Bank of America Corporation
.bom	generic	Núcleo de Informação e Coordenação do Ponto BR - NIC.br
.bond	generic	Shortdot SA
.boo	generic	Charleston Road Registry Inc.
.book	generic	Amazon Registry Services, Inc.
.booking	generic	Booking.com B.V.
.boots	generic	Not assigned
.bosch	generic	Robert Bosch GMBH
.bostik	generic	Bostik SA
.boston	generic	Registry Services, LLC
.bot	generic	Amazon Registry Services, Inc.
.boutique	generic	Binky Moon, LLC
.box	generic	Intercap Registry Inc.
.bq	country-code	Not assigned
.br	country-code	Comite Gestor da Internet no Brasil
.bradesco	generic	Banco Bradesco S.A.
.bridgestone	generic	Bridgestone Corporation
.broadway	generic	Celebrate Broadway, Inc.
.broker	generic	Dog Beach, LLC
.brother	generic	Brother Industries, Ltd.
.brussels	generic	DNS.be vzw
.bs	country-code	University of The Bahamas
.bt	country-code	Ministry of Information and Communications
.budapest	generic	Not assigned
.bugatti	generic	Not assigned
.build	generic	Plan Bee LLC
.builders	generic	Binky Moon, LLC
.business	generic	Binky Moon, LLC
.buy	generic	Amazon Registry Services, INC
.buzz	generic	DOTSTRATEGY CO.
.bv	country-code	Norid A/S
.bw	country-code	Botswana Communications Regulatory Authority (BOCRA)
.by	country-code	Belarusian Cloud Technologies LLC
.bz	country-code	University of Belize
.bzh	generic	Association www.bzh
.ca	country-code	Canadian Internet Registration Authority (CIRA) Autorité Canadienne pour les enregistrements Internet (ACEI)
.cab	generic	Binky Moon, LLC
.cafe	generic	Binky Moon, LLC
.cal	generic	Charleston Road Registry Inc.
.call	generic	Amazon Registry Services, Inc.
.calvinklein	generic	PVH gTLD Holdings LLC
.cam	generic	CAM Connecting SARL
.camera	generic	Binky Moon, LLC
.camp	generic	Binky Moon, LLC
.cancerresearch	generic	Not assigned
.canon	generic	Canon Inc.
.capetown	generic	ZA Central Registry NPC trading as ZA Central Registry
.capital	generic	Binky Moon, LLC
.capitalone	generic	Capital One Financial Corporation
.car	generic	XYZ.COM LLC
.caravan	generic	Caravan International, Inc.
.cards	generic	Binky Moon, LLC
.care	generic	Binky Moon, LLC
.career	generic	dotCareer LLC
.careers	generic	Binky Moon, LLC
.cars	generic	XYZ.COM LLC
.cartier	generic	Not assigned
.casa	generic	Registry Services, LLC
.case	generic	Digity, LLC
.caseih	generic	Not assigned
.cash	generic	Binky Moon, LLC
.casino	generic	Binky Moon, LLC
.cat	sponsored	Fundacio puntCAT
.catering	generic	Binky Moon, LLC
.catholic	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
.cba	generic	COMMONWEALTH BANK OF AUSTRALIA
.cbn	generic	The Christian Broadcasting Network, Inc.
.cbre	generic	CBRE, Inc.
.cbs	generic	Not assigned
.cc	country-code	eNIC Cocos (Keeling) Islands Pty. Ltd. d/b/a Island Internet Services
.cd	country-code	Office Congolais des Postes et Télécommunications - OCPT
.ceb	generic	Not assigned
.center	generic	Binky Moon, LLC
.ceo	generic	XYZ.COM LLC
.cern	generic	European Organization for Nuclear Research ("CERN")
.cf	country-code	Societe Centrafricaine de Telecommunications (SOCATEL)
.cfa	generic	CFA Institute
.cfd	generic	Shortdot SA
.cg	country-code	Interpoint Switzerland
.ch	country-code	SWITCH The Swiss Education & Research Network
.chanel	generic	Chanel International B.V.
.channel	generic	Charleston Road Registry Inc.
.charity	generic	Public Interest Registry (PIR)
.chase	generic	JPMorgan Chase Bank, National Association
.chat	generic	Binky Moon, LLC
.cheap	generic	Binky Moon, LLC
.chintai	generic	CHINTAI Corporation
.chloe	generic	Not assigned
.christmas	generic	XYZ.COM LLC
.chrome	generic	Charleston Road Registry Inc.
.chrysler	generic	Not assigned
.church	generic	Binky Moon, LLC
.ci	country-code	Autorité de Régulation des Télécommunications/TIC de Côte d’lvoire (ARTCI)
.cipriani	generic	Hotel Cipriani Srl
.circle	generic	Amazon Registry Services, Inc.
.cisco	generic	Cisco Technology, Inc.
.citadel	generic	Citadel Domain LLC
.citi	generic	Citigroup Inc.
.citic	generic	CITIC Group Corporation
.city	generic	Binky Moon, LLC
.cityeats	generic	Not assigned
.ck	country-code	Telecom Cook Islands Ltd.
.cl	country-code	NIC Chile (University of Chile)
.claims	generic	Binky Moon, LLC
.cleaning	generic	Binky Moon, LLC
.click	generic	Internet Naming Co.
.clinic	generic	Binky Moon, LLC
.clinique	generic	The Estée Lauder Companies Inc.
.clothing	generic	Binky Moon, LLC
.cloud	generic	ARUBA PEC S.p.A.
.club	generic	Registry Services, LLC
.clubmed	generic	Club Méditerranée S.A.
.cm	country-code	Agence Nationale des Technologies de l'Information et de la Communication (ANTIC)
.cn	country-code	China Internet Network Information Center (CNNIC)
.co	country-code	Ministry of Information and Communications Technologies (MinTIC)
.coach	generic	Binky Moon, LLC
.codes	generic	Binky Moon, LLC
.coffee	generic	Binky Moon, LLC
.college	generic	XYZ.COM LLC
.cologne	generic	dotKoeln GmbH
.com	generic	VeriSign Global Registry Services
.comcast	generic	Not assigned
.commbank	generic	COMMONWEALTH BANK OF AUSTRALIA
.community	generic	Binky Moon, LLC
.company	generic	Binky Moon, LLC
.compare	generic	Registry Services, LLC
.computer	generic	Binky Moon, LLC
.comsec	generic	VeriSign, Inc.
.condos	generic	Binky Moon, LLC
.construction	generic	Binky Moon, LLC
.consulting	generic	Dog Beach, LLC
.contact	generic	Dog Beach, LLC
.contractors	generic	Binky Moon, LLC
.cooking	generic	Registry Services, LLC
.cookingchannel	generic	Not assigned
.cool	generic	Binky Moon, LLC
.coop	sponsored	DotCooperation LLC
.corsica	generic	Collectivité de Corse
.country	generic	Internet Naming Co.
.coupon	generic	Amazon Registry Services, Inc.
.coupons	generic	Binky Moon, LLC
.courses	generic	Registry Services, LLC
.cpa	generic	American Institute of Certified Public Accountants
.cr	country-code	National Academy of Sciences Academia Nacional de Ciencias
.credit	generic	Binky Moon, LLC
.creditcard	generic	Binky Moon, LLC
.creditunion	generic	DotCooperation, LLC
.cricket	generic	dot Cricket Limited
.crown	generic	Crown Equipment Corporation
.crs	generic	Federated Co-operatives Limited
.cruise	generic	Viking River Cruises (Bermuda) Ltd.
.cruises	generic	Binky Moon, LLC
.csc	generic	Not assigned
.cu	country-code	CENIAInternet Industria y San Jose Capitolio Nacional
.cuisinella	generic	SCHMIDT GROUPE S.A.S.
.cv	country-code	Agência Reguladora Multissectorial da Economia (ARME)
.cw	country-code	University of Curacao
.cx	country-code	Christmas Island Domain Administration Limited
.cy	country-code	University of Cyprus
.cymru	generic	Nominet UK
.cyou	generic	Shortdot SA
.cz	country-code	CZ.NIC, z.s.p.o
.dabur	generic	Not assigned
.dad	generic	Charleston Road Registry Inc.
.dance	generic	Dog Beach, LLC
.data	generic	Dish DBS Corporation
.date	generic	dot Date Limited
.dating	generic	Binky Moon, LLC
.datsun	generic	NISSAN MOTOR CO., LTD.
.day	generic	Charleston Road Registry Inc.
.dclk	generic	Charleston Road Registry Inc.
.dds	generic	Registry Services, LLC
.de	country-code	DENIC eG
.deal	generic	Amazon Registry Services, Inc.
.dealer	generic	Intercap Registry Inc.
.deals	generic	Binky Moon, LLC
.degree	generic	Dog Beach, LLC
.delivery	generic	Binky Moon, LLC
.dell	generic	Dell Inc.
.deloitte	generic	Deloitte Touche Tohmatsu
.delta	generic	Delta Air Lines, Inc.
.democrat	generic	Dog Beach, LLC
.dental	generic	Binky Moon, LLC
.dentist	generic	Dog Beach, LLC
.desi	generic	Emergency Back-End Registry Operator Program - ICANN
.design	generic	Registry Services, LLC
.dev	generic	Charleston Road Registry Inc.
.dhl	generic	Deutsche Post AG
.diamonds	generic	Binky Moon, LLC
.diet	generic	XYZ.COM LLC
.digital	generic	Binky Moon, LLC
.direct	generic	Binky Moon, LLC
.directory	generic	Binky Moon, LLC
.discount	generic	Binky Moon, LLC
.discover	generic	Discover Financial Services
.dish	generic	Dish DBS Corporation
.diy	generic	Internet Naming Co.
.dj	country-code	Djibouti Telecom S.A
.dk	country-code	Dansk Internet Forum
.dm	country-code	DotDM Corporation
.dnp	generic	Dai Nippon Printing Co., Ltd.
.do	country-code	Pontificia Universidad Catolica Madre y Maestra Recinto Santo Tomas de Aquino
.docs	generic	Charleston Road Registry Inc.
.doctor	generic	Binky Moon, LLC
.dodge	generic	Not assigned
.dog	generic	Binky Moon, LLC
.doha	generic	Not assigned
.domains	generic	Binky Moon, LLC
.doosan	generic	Not assigned
.dot	generic	Dish DBS Corporation
.download	generic	dot Support Limited
.drive	generic	Charleston Road Registry Inc.
.dtv	generic	Dish DBS Corporation
.dubai	generic	Dubai Smart Government Department
.duck	generic	Not assigned
.dunlop	generic	The Goodyear Tire & Rubber Company
.duns	generic	Not assigned
.dupont	generic	DuPont Specialty Products USA, LLC
.durban	generic	ZA Central Registry NPC trading as ZA Central Registry
.dvag	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.dvr	generic	DISH Technologies L.L.C.
.dz	country-code	CERIST
.earth	generic	Interlink Systems Innovation Institute K.K.
.eat	generic	Charleston Road Registry Inc.
.ec	country-code	ECUADORDOMAIN S.A.
.eco	generic	Big Room Inc.
.edeka	generic	EDEKA Verband kaufmännischer Genossenschaften e.V.
.edu	sponsored	EDUCAUSE
.education	generic	Binky Moon, LLC
.ee	country-code	Eesti Interneti Sihtasutus (EIS)
.eg	country-code	Egyptian Universities Network (EUN) Supreme Council of Universities
.eh	country-code	Not assigned
.email	generic	Binky Moon, LLC
.emerck	generic	Merck KGaA
.energy	generic	Binky Moon, LLC
.engineer	generic	Dog Beach, LLC
.engineering	generic	Binky Moon, LLC
.enterprises	generic	Binky Moon, LLC
.epost	generic	Not assigned
.epson	generic	Seiko Epson Corporation
.equipment	generic	Binky Moon, LLC
.er	country-code	Eritrea Telecommunication Services Corporation (EriTel)
.ericsson	generic	Telefonaktiebolaget L M Ericsson
.erni	generic	ERNI Group Holding AG
.es	country-code	Red.es
.esq	generic	Charleston Road Registry Inc.
.estate	generic	Binky Moon, LLC
.esurance	generic	Not assigned
.et	country-code	Ethio telecom
.etisalat	generic	Not assigned
.eu	country-code	EURid vzw/asbl
.eurovision	generic	European Broadcasting Union (EBU)
.eus	generic	Puntueus Fundazioa
.events	generic	Binky Moon, LLC
.everbank	generic	Not assigned
.exchange	generic	Binky Moon, LLC
.expert	generic	Binky Moon, LLC
.exposed	generic	Binky Moon, LLC
.express	generic	Binky Moon, LLC
.extraspace	generic	Extra Space Storage LLC
.fage	generic	Fage International S.A.
.fail	generic	Binky Moon, LLC
.fairwinds	generic	FairWinds Partners, LLC
.faith	generic	dot Faith Limited
.family	generic	Dog Beach, LLC
.fan	generic	Dog Beach, LLC
.fans	generic	ZDNS International Limited
.farm	generic	Binky Moon, LLC
.farmers	generic	Farmers Insurance Exchange
.fashion	generic	Registry Services, LLC
.fast	generic	Amazon Registry Services, Inc.
.fedex	generic	Federal Express Corporation
.feedback	generic	Top Level Spectrum, Inc.
.ferrari	generic	Fiat Chrysler Automobiles N.V.
.ferrero	generic	Ferrero Trading Lux S.A.
.fi	country-code	Finnish Transport and Communications Agency Traficom
.fiat	generic	Not assigned
.fidelity	generic	Fidelity Brokerage Services LLC
.fido	generic	Rogers Communications Canada Inc.
.film	generic	Motion Picture Domain Registry Pty Ltd
.final	generic	Núcleo de Informação e Coordenação do Ponto BR - NIC.br
.finance	generic	Binky Moon, LLC
.financial	generic	Binky Moon, LLC
.fire	generic	Amazon Registry Services, Inc.
.firestone	generic	Bridgestone Licensing Services, Inc.
.firmdale	generic	Firmdale Holdings Limited
.fish	generic	Binky Moon, LLC
.fishing	generic	Registry Services, LLC
.fit	generic	Registry Services, LLC
.fitness	generic	Binky Moon, LLC
.fj	country-code	The University of the South Pacific IT Services
.fk	country-code	Falkland Islands Government
.flickr	generic	Flickr, Inc.
.flights	generic	Binky Moon, LLC
.flir	generic	FLIR Systems, Inc.
.florist	generic	Binky Moon, LLC
.flowers	generic	XYZ.COM LLC
.flsmidth	generic	Not assigned
.fly	generic	Charleston Road Registry Inc.
.fm	country-code	FSM Telecommunications Corporation
.fo	country-code	FO Council
.foo	generic	Charleston Road Registry Inc.
.food	generic	Internet Naming Co.
.foodnetwork	generic	Not assigned
.football	generic	Binky Moon, LLC
.ford	generic	Ford Motor Company
.forex	generic	Dog Beach, LLC
.forsale	generic	Dog Beach, LLC
.forum	generic	Fegistry, LLC
.foundation	generic	Public Interest Registry (PIR)
.fox	generic	FOX Registry, LLC
.fr	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.free	generic	Amazon Registry Services, Inc.
.fresenius	generic	Fresenius Immobilien-Verwaltungs-GmbH
.frl	generic	FRLregistry B.V.
.frogans	generic	OP3FT
.frontdoor	generic	Not assigned
.frontier	generic	Frontier Communications Corporation
.ftr	generic	Frontier Communications Corporation
.fujitsu	generic	Fujitsu Limited
.fujixerox	generic	Not assigned
.fun	generic	Radix Technologies Inc.
.fund	generic	Binky Moon, LLC
.furniture	generic	Binky Moon, LLC
.futbol	generic	Dog Beach, LLC
.fyi	generic	Binky Moon, LLC
.ga	country-code	Agence Nationale des Infrastructures Numériques et des Fréquences (ANINF)
.gal	generic	Asociación puntoGAL
.gallery	generic	Binky Moon, LLC
.gallo	generic	Gallo Vineyards, Inc.
.gallup	generic	Gallup, Inc.
.game	generic	XYZ.COM LLC
.games	generic	Dog Beach, LLC
.gap	generic	The Gap, Inc.
.garden	generic	Registry Services, LLC
.gay	generic	Registry Services, LLC
.gb	country-code	Reserved Domain - IANA
.gbiz	generic	Charleston Road Registry Inc.
.gd	country-code	The National Telecommunications Regulatory Commission (NTRC)
.gdn	generic	Joint Stock Company "Navigation-information systems"
.ge	country-code	Caucasus Online LLC
.gea	generic	GEA Group Aktiengesellschaft
.gent	generic	Combell nv
.genting	generic	Resorts World Inc. Pte. Ltd.
.george	generic	Wal-Mart Stores, Inc.
.gf	country-code	CANAL+ TELECOM
.gg	country-code	Island Networks Ltd.
.ggee	generic	GMO Internet, Inc.
.gh	country-code	Network Computer Systems Limited
.gi	country-code	Sapphire Networks
.gift	generic	Uniregistry, Corp.
.gifts	generic	Binky Moon, LLC
.gives	generic	Public Interest Registry (PIR)
.giving	generic	Public Interest Registry (PIR)
.gl	country-code	TELE Greenland A/S
.glade	generic	Not assigned
.glass	generic	Binky Moon, LLC
.gle	generic	Charleston Road Registry Inc.
.global	generic	Identity Digital Limited
.globo	generic	Globo Comunicação e Participações S.A
.gm	country-code	GM-NIC
.gmail	generic	Charleston Road Registry Inc.
.gmbh	generic	Binky Moon, LLC
.gmo	generic	GMO Internet, Inc.
.gmx	generic	1&1 Mail & Media GmbH
.gn	country-code	Centre National des Sciences Halieutiques de Boussoura
.godaddy	generic	Go Daddy East, LLC
.gold	generic	Binky Moon, LLC
.goldpoint	generic	YODOBASHI CAMERA CO.,LTD.
.golf	generic	Binky Moon, LLC
.goo	generic	NTT Resonant Inc.
.goodhands	generic	Not assigned
.goodyear	generic	The Goodyear Tire & Rubber Company
.goog	generic	Charleston Road Registry Inc.
.google	generic	Charleston Road Registry Inc.
.gop	generic	Republican State Leadership Committee, Inc.
.got	generic	Amazon Registry Services, Inc.
.gov	sponsored	Cybersecurity and Infrastructure Security Agency
.gp	country-code	Networking Technologies Group
.gq	country-code	GETESA
.gr	country-code	ICS-FORTH GR
.grainger	generic	Grainger Registry Services, LLC
.graphics	generic	Binky Moon, LLC
.gratis	generic	Binky Moon, LLC
.green	generic	Identity Digital Limited
.gripe	generic	Binky Moon, LLC
.grocery	generic	Wal-Mart Stores, Inc.
.group	generic	Binky Moon, LLC
.gs	country-code	Government of South Georgia and South Sandwich Islands (GSGSSI)
.gt	country-code	Universidad del Valle de Guatemala
.gu	country-code	University of Guam
.guardian	generic	Not assigned
.gucci	generic	Guccio Gucci S.p.a.
.guge	generic	Charleston Road Registry Inc.
.guide	generic	Binky Moon, LLC
.guitars	generic	XYZ.COM LLC
.guru	generic	Binky Moon, LLC
.gw	country-code	Autoridade Reguladora Nacional - Tecnologias de Informação e Comunicação da Guiné-Bissau
.gy	country-code	University of Guyana
.hair	generic	XYZ.COM LLC
.hamburg	generic	Hamburg Top-Level-Domain GmbH
.hangout	generic	Charleston Road Registry Inc.
.haus	generic	Dog Beach, LLC
.hbo	generic	HBO Registry Services, Inc.
.hdfc	generic	HOUSING DEVELOPMENT FINANCE CORPORATION LIMITED
.hdfcbank	generic	HDFC Bank Limited
.health	generic	Registry Services, LLC
.healthcare	generic	Binky Moon, LLC
.help	generic	Innovation Service Ltd
.helsinki	generic	City of Helsinki
.here	generic	Charleston Road Registry Inc.
.hermes	generic	Hermes International
.hgtv	generic	Not assigned
.hiphop	generic	Dot Hip Hop, LLC
.hisamitsu	generic	Hisamitsu Pharmaceutical Co.,Inc.
.hitachi	generic	Hitachi, Ltd.
.hiv	generic	Internet Naming Co.
.hk	country-code	Hong Kong Internet Registration Corporation Ltd.
.hkt	generic	PCCW-HKT DataCom Services Limited
.hm	country-code	HM Domain Registry
.hn	country-code	Red de Desarrollo Sostenible Honduras
.hockey	generic	Binky Moon, LLC
.holdings	generic	Binky Moon, LLC
.holiday	generic	Binky Moon, LLC
.homedepot	generic	Home Depot Product Authority, LLC
.homegoods	generic	The TJX Companies, Inc.
.homes	generic	XYZ.COM LLC
.homesense	generic	The TJX Companies, Inc.
.honda	generic	Honda Motor Co., Ltd.
.honeywell	generic	Not assigned
.horse	generic	Registry Services, LLC
.hospital	generic	Binky Moon, LLC
.host	generic	Radix Technologies Inc.
.hosting	generic	XYZ.COM LLC
.hot	generic	Amazon Registry Services, Inc.
.hoteles	generic	Not assigned
.hotels	generic	Booking.com B.V.
.hotmail	generic	Microsoft Corporation
.house	generic	Binky Moon, LLC
.how	generic	Charleston Road Registry Inc.
.hr	country-code	CARNet - Croatian Academic and Research Network
.hsbc	generic	HSBC Global Services (UK) Limited
.ht	country-code	Consortium FDS/RDDH
.htc	generic	Not assigned
.hu	country-code	Council of Hungarian Internet Providers (CHIP)
.hughes	generic	Hughes Satellite Systems Corporation
.hyatt	generic	Hyatt GTLD, L.L.C.
.hyundai	generic	Hyundai Motor Company
.ibm	generic	International Business Machines Corporation
.icbc	generic	Industrial and Commercial Bank of China Limited
.ice	generic	IntercontinentalExchange, Inc.
.icu	generic	Shortdot SA
.id	country-code	Perkumpulan Pengelola Nama Domain Internet Indonesia (PANDI)
.ie	country-code	University College Dublin Computing Services Computer Centre
.ieee	generic	IEEE Global LLC
.ifm	generic	ifm electronic gmbh
.iinet	generic	Not assigned
.ikano	generic	Ikano S.A.
.il	country-code	The Israel Internet Association (RA)
.im	country-code	Isle of Man Government
.imamat	generic	Fondation Aga Khan (Aga Khan Foundation)
.imdb	generic	Amazon Registry Services, Inc.
.immo	generic	Binky Moon, LLC
.immobilien	generic	Dog Beach, LLC
.in	country-code	National Internet Exchange of India
.inc	generic	Intercap Registry Inc.
.industries	generic	Binky Moon, LLC
.infiniti	generic	NISSAN MOTOR CO., LTD.
.info	generic	Identity Digital Limited
.ing	generic	Charleston Road Registry Inc.
.ink	generic	Registry Services, LLC
.institute	generic	Binky Moon, LLC
.insurance	generic	fTLD Registry Services LLC
.insure	generic	Binky Moon, LLC
.int	sponsored	Internet Assigned Numbers Authority
.intel	generic	Not assigned
.international	generic	Binky Moon, LLC
.intuit	generic	Intuit Administrative Services, Inc.
.investments	generic	Binky Moon, LLC
.io	country-code	Internet Computer Bureau Limited
.ipiranga	generic	Ipiranga Produtos de Petroleo S.A.
.iq	country-code	Communications and Media Commission (CMC)
.ir	country-code	Institute for Research in Fundamental Sciences
.irish	generic	Binky Moon, LLC
.is	country-code	ISNIC - Internet Iceland ltd.
.iselect	generic	Not assigned
.ismaili	generic	Fondation Aga Khan (Aga Khan Foundation)
.ist	generic	Istanbul Metropolitan Municipality
.istanbul	generic	Istanbul Metropolitan Municipality
.it	country-code	IIT - CNR
.itau	generic	Itau Unibanco Holding S.A.
.itv	generic	ITV Services Limited
.iveco	generic	Not assigned
.iwc	generic	Not assigned
.jaguar	generic	Jaguar Land Rover Ltd
.java	generic	Oracle Corporation
.jcb	generic	JCB Co., Ltd.
.jcp	generic	Not assigned
.je	country-code	Island Networks (Jersey) Ltd.
.jeep	generic	FCA US LLC.
.jetzt	generic	Binky Moon, LLC
.jewelry	generic	Binky Moon, LLC
.jio	generic	Reliance Industries Limited
.jlc	generic	Not assigned
.jll	generic	Jones Lang LaSalle Incorporated
.jm	country-code	University of West Indies
.jmp	generic	Matrix IP LLC
.jnj	generic	Johnson & Johnson Services, Inc.
.jo	country-code	Ministry of Digital Economy and Entrepreneurship (MoDEE)
.jobs	sponsored	Employ Media LLC
.joburg	generic	ZA Central Registry NPC trading as ZA Central Registry
.jot	generic	Amazon Registry Services, Inc.
.joy	generic	Amazon Registry Services, Inc.
.jp	country-code	Japan Registry Services Co., Ltd.
.jpmorgan	generic	JPMorgan Chase Bank, National Association
.jprs	generic	Japan Registry Services Co., Ltd.
.juegos	generic	Dog Beach, LLC
.juniper	generic	JUNIPER NETWORKS, INC.
.kaufen	generic	Dog Beach, LLC
.kddi	generic	KDDI CORPORATION
.ke	country-code	Kenya Network Information Center (KeNIC)
.kerryhotels	generic	Kerry Trading Co. Limited
.kerrylogistics	generic	Kerry Trading Co. Limited
.kerryproperties	generic	Kerry Trading Co. Limited
.kfh	generic	Kuwait Finance House
.kg	country-code	AsiaInfo Telecommunication Enterprise
.kh	country-code	Telecommunication Regulator of Cambodia (TRC)
.ki	country-code	Ministry of Information, Communications and Transport (MICT)
.kia	generic	KIA MOTORS CORPORATION
.kids	generic	DotKids Foundation Limited
.kim	generic	Identity Digital Limited
.kinder	generic	Not assigned
.kindle	generic	Amazon Registry Services, Inc.
.kitchen	generic	Binky Moon, LLC
.kiwi	generic	DOT KIWI LIMITED
.km	country-code	Comores Telecom
.kn	country-code	Ministry of Finance, Sustainable Development Information & Technology
.koeln	generic	dotKoeln GmbH
.komatsu	generic	Komatsu Ltd.
.kosher	generic	Kosher Marketing Assets LLC
.kp	country-code	Star Joint Venture Company
.kpmg	generic	KPMG International Cooperative (KPMG International Genossenschaft)
.kpn	generic	Koninklijke KPN N.V.
.kr	country-code	Korea Internet & Security Agency (KISA)
.krd	generic	KRG Department of Information Technology
.kred	generic	KredTLD Pty Ltd
.kuokgroup	generic	Kerry Trading Co. Limited
.kw	country-code	Communications and Information Technology Regulatory Authority
.ky	country-code	Utility Regulation and Competition Office (OfReg)
.kyoto	generic	Academic Institution: Kyoto Jyoho Gakuen
.kz	country-code	Association of IT Companies of Kazakhstan
.la	country-code	Lao National Internet Center (LANIC), Ministry of Technology and Communications
.lacaixa	generic	Fundación Bancaria Caixa d'Estalvis i Pensions de Barcelona, "la Caixa"
.ladbrokes	generic	Not assigned
.lamborghini	generic	Automobili Lamborghini S.p.A.
.lamer	generic	The Estée Lauder Companies Inc.
.lancaster	generic	LANCASTER
.lancia	generic	Not assigned
.lancome	generic	Not assigned
.land	generic	Binky Moon, LLC
.landrover	generic	Jaguar Land Rover Ltd
.lanxess	generic	LANXESS Corporation
.lasalle	generic	Jones Lang LaSalle Incorporated
.lat	generic	XYZ.COM LLC
.latino	generic	Dish DBS Corporation
.latrobe	generic	La Trobe University
.law	generic	Registry Services, LLC
.lawyer	generic	Dog Beach, LLC
.lb	country-code	Internet Society Lebanon
.lc	country-code	University of Puerto Rico
.lds	generic	IRI Domain Management, LLC
.lease	generic	Binky Moon, LLC
.leclerc	generic	A.C.D. LEC Association des Centres Distributeurs Edouard Leclerc
.lefrak	generic	LeFrak Organization, Inc.
.legal	generic	Binky Moon, LLC
.lego	generic	LEGO Juris A/S
.lexus	generic	TOYOTA MOTOR CORPORATION
.lgbt	generic	Identity Digital Limited
.li	country-code	SWITCH The Swiss Education & Research Network
.liaison	generic	Not assigned
.lidl	generic	Schwarz Domains und Services GmbH & Co. KG
.life	generic	Binky Moon, LLC
.lifeinsurance	generic	American Council of Life Insurers
.lifestyle	generic	Internet Naming Co.
.lighting	generic	Binky Moon, LLC
.like	generic	Amazon Registry Services, Inc.
.lilly	generic	Eli Lilly and Company
.limited	generic	Binky Moon, LLC
.limo	generic	Binky Moon, LLC
.lincoln	generic	Ford Motor Company
.linde	generic	Not assigned
.link	generic	Nova Registry Ltd.
.lipsy	generic	Lipsy Ltd
.live	generic	Dog Beach, LLC
.living	generic	Internet Naming Co.
.lixil	generic	Not assigned
.lk	country-code	Council for Information Technology LK Domain Registrar
.llc	generic	Identity Digital Limited
.llp	generic	Intercap Registry Inc.
.loan	generic	dot Loan Limited
.loans	generic	Binky Moon, LLC
.locker	generic	Orange Domains LLC
.locus	generic	Locus Analytics LLC
.loft	generic	Not assigned
.lol	generic	XYZ.COM LLC
.london	generic	Dot London Domains Limited
.lotte	generic	Lotte Holdings Co., Ltd.
.lotto	generic	Identity Digital Limited
.love	generic	Waterford Limited
.lpl	generic	LPL Holdings, Inc.
.lplfinancial	generic	LPL Holdings, Inc.
.lr	country-code	Data Technology Solutions, Inc.
.ls	country-code	Lesotho Network Information Centre Proprietary (LSNIC)
.lt	country-code	Kaunas University of Technology
.ltd	generic	Binky Moon, LLC
.ltda	generic	InterNetX Corp.
.lu	country-code	RESTENA
.lundbeck	generic	H. Lundbeck A/S
.lupin	generic	Not assigned
.luxe	generic	Registry Services, LLC
.luxury	generic	Luxury Partners LLC
.lv	country-code	University of Latvia Institute of Mathematics and Computer Science Department of Network Solutions (DNS)
.ly	country-code	General Post and Telecommunication Company
.ma	country-code	Agence Nationale de Réglementation des Télécommunications (ANRT)
.macys	generic	Not assigned
.madrid	generic	Comunidad de Madrid
.maif	generic	Mutuelle Assurance Instituteur France (MAIF)
.maison	generic	Binky Moon, LLC
.makeup	generic	XYZ.COM LLC
.man	generic	MAN Truck & Bus SE
.management	generic	Binky Moon, LLC
.mango	generic	PUNTO FA S.L.
.map	generic	Charleston Road Registry Inc.
.market	generic	Dog Beach, LLC
.marketing	generic	Binky Moon, LLC
.markets	generic	Dog Beach, LLC
.marriott	generic	Marriott Worldwide Corporation
.marshalls	generic	The TJX Companies, Inc.
.maserati	generic	Not assigned
.mattel	generic	Mattel Sites, Inc.
.mba	generic	Binky Moon, LLC
.mc	country-code	Direction des Plateformes et des Ressources Numériques
.mcd	generic	Not assigned
.mcdonalds	generic	Not assigned
.mckinsey	generic	McKinsey Holdings, Inc.
.md	country-code	IP Serviciul Tehnologia Informatiei si Securitate Cibernetica
.me	country-code	Government of Montenegro
.med	generic	Medistry LLC
.media	generic	Binky Moon, LLC
.meet	generic	Charleston Road Registry Inc.
.melbourne	generic	The Crown in right of the State of Victoria, represented by its Department of State Development, Business and Innovation
.meme	generic	Charleston Road Registry Inc.
.memorial	generic	Dog Beach, LLC
.men	generic	Exclusive Registry Limited
.menu	generic	Dot Menu Registry LLC
.meo	generic	Not assigned
.merckmsd	generic	MSD Registry Holdings, Inc.
.metlife	generic	Not assigned
.mf	country-code	Not assigned
.mg	country-code	NIC-MG (Network Information Center Madagascar)
.mh	country-code	Office of the Cabinet
.miami	generic	Registry Services, LLC
.microsoft	generic	Microsoft Corporation
.mil	sponsored	DoD Network Information Center
.mini	generic	Bayerische Motoren Werke Aktiengesellschaft
.mint	generic	Intuit Administrative Services, Inc.
.mit	generic	Massachusetts Institute of Technology
.mitsubishi	generic	Mitsubishi Corporation
.mk	country-code	Macedonian Academic Research Network Skopje
.ml	country-code	Agence des Technologies de l’Information et de la Communication
.mlb	generic	MLB Advanced Media DH, LLC
.mls	generic	The Canadian Real Estate Association
.mm	country-code	Ministry of Transport and Communications
.mma	generic	MMA IARD
.mn	country-code	Datacom Co., Ltd.
.mo	country-code	Macao Post and Telecommunications Bureau (CTT)
.mobi	generic	Identity Digital Limited
.mobile	generic	Dish DBS Corporation
.mobily	generic	Not assigned
.moda	generic	Dog Beach, LLC
.moe	generic	Interlink Systems Innovation Institute K.K.
.moi	generic	Amazon Registry Services, Inc.
.mom	generic	XYZ.COM LLC
.monash	generic	Monash University
.money	generic	Binky Moon, LLC
.monster	generic	XYZ.COM LLC
.montblanc	generic	Not assigned
.mopar	generic	Not assigned
.mormon	generic	IRI Domain Management, LLC ("Applicant")
.mortgage	generic	Dog Beach, LLC
.moscow	generic	Foundation for Assistance for Internet Technologies and Infrastructure Development (FAITID)
.moto	generic	Motorola Trademark Holdings, LLC
.motorcycles	generic	XYZ.COM LLC
.mov	generic	Charleston Road Registry Inc.
.movie	generic	Binky Moon, LLC
.movistar	generic	Not assigned
.mp	country-code	Saipan Datacom, Inc.
.mq	country-code	CANAL+ TELECOM
.mr	country-code	Université de Nouakchott Al Aasriya
.ms	country-code	MNI Networks Ltd.
.msd	generic	MSD Registry Holdings, Inc.
.mt	country-code	NIC (Malta)
.mtn	generic	MTN Dubai Limited
.mtpc	generic	Not assigned
.mtr	generic	MTR Corporation Limited
.mu	country-code	Internet Direct Ltd
.museum	sponsored	Museum Domain Management Association
.music	generic	DotMusic Limited
.mutual	generic	Not assigned
.mutuelle	generic	Not assigned
.mv	country-code	Dhivehi Raajjeyge Gulhun PLC
.mw	country-code	Malawi Sustainable Development Network Programme (Malawi SDNP)
.mx	country-code	NIC-Mexico ITESM - Campus Monterrey
.my	country-code	MYNIC Berhad
.mz	country-code	Centro de Informatica de Universidade Eduardo Mondlane
.na	country-code	Namibian Network Information Center
.nab	generic	National Australia Bank Limited
.nadex	generic	Not assigned
.nagoya	generic	GMO Registry, Inc.
.name	generic-restricted	VeriSign Information Services, Inc.
.nationwide	generic	Not assigned
.natura	generic	Not assigned
.navy	generic	Dog Beach, LLC
.nba	generic	NBA REGISTRY, LLC
.nc	country-code	Office des Postes et Telecommunications
.ne	country-code	SONITEL
.nec	generic	NEC Corporation
.net	generic	VeriSign Global Registry Services
.netbank	generic	COMMONWEALTH BANK OF AUSTRALIA
.netflix	generic	Netflix, Inc.
.network	generic	Binky Moon, LLC
.neustar	generic	NeuStar, Inc.
.new	generic	Charleston Road Registry Inc.
.newholland	generic	Not assigned
.news	generic	Dog Beach, LLC
.next	generic	Next plc
.nextdirect	generic	Next plc
.nexus	generic	Charleston Road Registry Inc.
.nf	country-code	Norfolk Island Data Services
.nfl	generic	NFL Reg Ops LLC
.ng	country-code	Nigeria Internet Registration Association
.ngo	generic	Public Interest Registry
.nhk	generic	Japan Broadcasting Corporation (NHK)
.ni	country-code	Universidad Nacional del Ingernieria. Division de Tecnologias de la Informacion.
.nico	generic	DWANGO Co., Ltd.
.nike	generic	NIKE, Inc.
.nikon	generic	NIKON CORPORATION
.ninja	generic	Dog Beach, LLC
.nissan	generic	NISSAN MOTOR CO., LTD.
.nissay	generic	Nippon Life Insurance Company
.nl	country-code	SIDN (Stichting Internet Domeinregistratie Nederland)
.no	country-code	Norid A/S
.nokia	generic	Nokia Corporation
.northwesternmutual	generic	Not assigned
.norton	generic	Gen Digital Inc.
.now	generic	Amazon Registry Services, Inc.
.nowruz	generic	Emergency Back-End Registry Operator Program - ICANN
.nowtv	generic	Starbucks (HK) Limited
.np	country-code	Mercantile Communications Pvt. Ltd.
.nr	country-code	CENPAC NET
.nra	generic	NRA Holdings Company, INC.
.nrw	generic	Minds + Machines GmbH
.ntt	generic	NIPPON TELEGRAPH AND TELEPHONE CORPORATION
.nu	country-code	The IUSN Foundation
.nyc	generic	The City of New York by and through the New York City Department of Information Technology & Telecommunications
.nz	country-code	InternetNZ
.obi	generic	OBI Group Holding SE & Co. KGaA
.observer	generic	Fegistry, LLC
.off	generic	Not assigned
.office	generic	Microsoft Corporation
.okinawa	generic	BRregistry, Inc.
.olayan	generic	Competrol (Luxembourg) Sarl
.olayangroup	generic	Competrol (Luxembourg) Sarl
.oldnavy	generic	Not assigned
.ollo	generic	Dish DBS Corporation
.om	country-code	Telecommunications Regulatory Authority (TRA)
.omega	generic	The Swatch Group Ltd
.one	generic	One.com A/S
.ong	generic	Public Interest Registry
.onl	generic	iRegistry GmbH
.online	generic	Radix Technologies Inc.
.onyourside	generic	Not assigned
.ooo	generic	INFIBEAM AVENUES LIMITED
.open	generic	American Express Travel Related Services Company, Inc.
.oracle	generic	Oracle Corporation
.orange	generic	Orange Brand Services Limited
.org	generic	Public Interest Registry (PIR)
.organic	generic	Identity Digital Limited
.orientexpress	generic	Not assigned
.origins	generic	The Estée Lauder Companies Inc.
.osaka	generic	Osaka Registry Co., Ltd.
.otsuka	generic	Otsuka Holdings Co., Ltd.
.ott	generic	Dish DBS Corporation
.ovh	generic	OVH SAS
.pa	country-code	Universidad Tecnologica de Panama
.page	generic	Charleston Road Registry Inc.
.pamperedchef	generic	Not assigned
.panasonic	generic	Panasonic Corporation
.panerai	generic	Not assigned
.paris	generic	City of Paris
.pars	generic	Emergency Back-End Registry Operator Program - ICANN
.partners	generic	Binky Moon, LLC
.parts	generic	Binky Moon, LLC
.party	generic	Blue Sky Registry Limited
.passagens	generic	Not assigned
.pay	generic	Amazon Registry Services, Inc.
.pccw	generic	PCCW Enterprises Limited
.pe	country-code	Red Cientifica Peruana
.pet	generic	Identity Digital Limited
.pf	country-code	Gouvernement de la Polynésie française
.pfizer	generic	Pfizer Inc.
.pg	country-code	PNG DNS Administration Vice Chancellors Office The Papua New Guinea University of Technology
.ph	country-code	PH Domain Foundation
.pharmacy	generic	National Association of Boards of Pharmacy
.phd	generic	Charleston Road Registry Inc.
.philips	generic	Koninklijke Philips N.V.
.phone	generic	Dish DBS Corporation
.photo	generic	Registry Services, LLC
.photography	generic	Binky Moon, LLC
.photos	generic	Binky Moon, LLC
.physio	generic	PhysBiz Pty Ltd
.piaget	generic	Not assigned
.pics	generic	XYZ.COM LLC
.pictet	generic	Pictet Europe S.A.
.pictures	generic	Binky Moon, LLC
.pid	generic	Top Level Spectrum, Inc.
.pin	generic	Amazon Registry Services, Inc.
.ping	generic	Ping Registry Provider, Inc.
.pink	generic	Identity Digital Limited
.pioneer	generic	Pioneer Corporation
.pizza	generic	Binky Moon, LLC
.pk	country-code	PKNIC
.pl	country-code	Research and Academic Computer Network
.place	generic	Binky Moon, LLC
.play	generic	Charleston Road Registry Inc.
.playstation	generic	Sony Computer Entertainment Inc.
.plumbing	generic	Binky Moon, LLC
.plus	generic	Binky Moon, LLC
.pm	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.pn	country-code	Pitcairn Island Administration
.pnc	generic	PNC Domain Co., LLC
.pohl	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.poker	generic	Identity Digital Limited
.politie	generic	Politie Nederland
.porn	generic	ICM Registry PN LLC
.post	sponsored	Universal Postal Union
.pr	country-code	Gauss Research Laboratory Inc.
.pramerica	generic	Prudential Financial, Inc.
.praxi	generic	Praxi S.p.A.
.press	generic	Radix Technologies Inc.
.prime	generic	Amazon Registry Services, Inc.
.pro	generic-restricted	Identity Digital Limited
.prod	generic	Charleston Road Registry Inc.
.productions	generic	Binky Moon, LLC
.prof	generic	Charleston Road Registry Inc.
.progressive	generic	Progressive Casualty Insurance Company
.promo	generic	Identity Digital Limited
.properties	generic	Binky Moon, LLC
.property	generic	Digital Property Infrastructure Limited
.protection	generic	XYZ.COM LLC
.pru	generic	Prudential Financial, Inc.
.prudential	generic	Prudential Financial, Inc.
.ps	country-code	Ministry Of Telecommunications & Information Technology, Government Computer Center.
.pt	country-code	Associação DNS.PT
.pub	generic	Dog Beach, LLC
.pw	country-code	Micronesia Investment and Development Corporation
.pwc	generic	PricewaterhouseCoopers LLP
.py	country-code	NIC-PY
.qa	country-code	Communications Regulatory Authority
.qpon	generic	DOTQPON LLC.
.quebec	generic	PointQuébec Inc
.quest	generic	XYZ.COM LLC
.qvc	generic	Not assigned
.racing	generic	Premier Registry Limited
.radio	generic	European Broadcasting Union (EBU)
.raid	generic	Not assigned
.re	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.read	generic	Amazon Registry Services, Inc.
.realestate	generic	dotRealEstate LLC
.realtor	generic	Real Estate Domains LLC
.realty	generic	Internet Naming Co.
.recipes	generic	Binky Moon, LLC
.red	generic	Identity Digital Limited
.redstone	generic	Redstone Haute Couture Co., Ltd.
.redumbrella	generic	Travelers TLD, LLC
.rehab	generic	Dog Beach, LLC
.reise	generic	Binky Moon, LLC
.reisen	generic	Binky Moon, LLC
.reit	generic	National Association of Real Estate Investment Trusts, Inc.
.reliance	generic	Reliance Industries Limited
.ren	generic	ZDNS International Limited
.rent	generic	XYZ.COM LLC
.rentals	generic	Binky Moon, LLC
.repair	generic	Binky Moon, LLC
.report	generic	Binky Moon, LLC
.republican	generic	Dog Beach, LLC
.rest	generic	Punto 2012 Sociedad Anonima Promotora de Inversion de Capital Variable
.restaurant	generic	Binky Moon, LLC
.review	generic	dot Review Limited
.reviews	generic	Dog Beach, LLC
.rexroth	generic	Robert Bosch GMBH
.rich	generic	iRegistry GmbH
.richardli	generic	Pacific Century Asset Management (HK) Limited
.ricoh	generic	Ricoh Company, Ltd.
.rightathome	generic	Not assigned
.ril	generic	Reliance Industries Limited
.rio	generic	Empresa Municipal de Informática SA - IPLANRIO
.rip	generic	Dog Beach, LLC
.rmit	generic	Not assigned
.ro	country-code	National Institute for R&D in Informatics
.rocher	generic	Not assigned
.rocks	generic	Dog Beach, LLC
.rodeo	generic	Registry Services, LLC
.rogers	generic	Rogers Communications Canada Inc.
.room	generic	Amazon Registry Services, Inc.
.rs	country-code	Serbian National Internet Domain Registry (RNIDS)
.rsvp	generic	Charleston Road Registry Inc.
.ru	country-code	Coordination Center for TLD RU
.rugby	generic	World Rugby Strategic Developments Limited
.ruhr	generic	dotSaarland GmbH
.run	generic	Binky Moon, LLC
.rw	country-code	Rwanda Internet Community and Technology Alliance (RICTA) Ltd
.rwe	generic	RWE AG
.ryukyu	generic	BRregistry, Inc.
.sa	country-code	Communications, Space and Technology Commission
.saarland	generic	dotSaarland GmbH
.safe	generic	Amazon Registry Services, Inc.
.safety	generic	Safety Registry Services, LLC.
.sakura	generic	SAKURA internet Inc.
.sale	generic	Dog Beach, LLC
.salon	generic	Binky Moon, LLC
.samsclub	generic	Wal-Mart Stores, Inc.
.samsung	generic	SAMSUNG SDS CO., LTD
.sandvik	generic	Sandvik AB
.sandvikcoromant	generic	Sandvik AB
.sanofi	generic	Sanofi
.sap	generic	SAP AG
.sapo	generic	Not assigned
.sarl	generic	Binky Moon, LLC
.sas	generic	Research IP LLC
.save	generic	Amazon Registry Services, Inc.
.saxo	generic	Saxo Bank A/S
.sb	country-code	Solomon Telekom Company Limited
.sbi	generic	STATE BANK OF INDIA
.sbs	generic	Shortdot SA
.sc	country-code	VCS Pty Ltd
.sca	generic	Not assigned
.scb	generic	The Siam Commercial Bank Public Company Limited ("SCB")
.schaeffler	generic	Schaeffler Technologies AG & Co. KG
.schmidt	generic	SCHMIDT GROUPE S.A.S.
.scholarships	generic	Scholarships.com, LLC
.school	generic	Binky Moon, LLC
.schule	generic	Binky Moon, LLC
.schwarz	generic	Schwarz Domains und Services GmbH & Co. KG
.science	generic	dot Science Limited
.scjohnson	generic	Not assigned
.scor	generic	Not assigned
.scot	generic	Dot Scot Registry Limited
.sd	country-code	Sudan Internet Society
.se	country-code	The Internet Infrastructure Foundation
.search	generic	Charleston Road Registry Inc.
.seat	generic	SEAT, S.A. (Sociedad Unipersonal)
.secure	generic	Amazon Registry Services, Inc.
.security	generic	XYZ.COM LLC
.seek	generic	Seek Limited
.select	generic	Registry Services, LLC
.sener	generic	Sener Ingeniería y Sistemas, S.A.
.services	generic	Binky Moon, LLC
.ses	generic	Not assigned
.seven	generic	Seven West Media Ltd
.sew	generic	SEW-EURODRIVE GmbH & Co KG
.sex	generic	ICM Registry SX LLC
.sexy	generic	Internet Naming Co.
.sfr	generic	Societe Francaise du Radiotelephone - SFR
.sg	country-code	Singapore Network Information Centre (SGNIC) Pte Ltd
.sh	country-code	Government of St. Helena
.shangrila	generic	Shangri-La International Hotel Management Limited
.sharp	generic	Sharp Corporation
.shaw	generic	Not assigned
.shell	generic	Shell Information Technology International Inc
.shia	generic	Emergency Back-End Registry Operator Program - ICANN
.shiksha	generic	Identity Digital Limited
.shoes	generic	Binky Moon, LLC
.shop	generic	GMO Registry, Inc.
.shopping	generic	Binky Moon, LLC
.shouji	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.show	generic	Binky Moon, LLC
.showtime	generic	Not assigned
.shriram	generic	Not assigned
.si	country-code	Academic and Research Network of Slovenia (ARNES)
.silk	generic	Amazon Registry Services, Inc.
.sina	generic	Sina Corporation
.singles	generic	Binky Moon, LLC
.site	generic	Radix Technologies Inc.
.sj	country-code	Norid A/S
.sk	country-code	SK-NIC, a.s.
.ski	generic	Identity Digital Limited
.skin	generic	XYZ.COM LLC
.sky	generic	Sky UK Limited
.skype	generic	Microsoft Corporation
.sl	country-code	Sierratel
.sling	generic	DISH Technologies L.L.C.
.sm	country-code	Telecom Italia San Marino S.p.A.
.smart	generic	Smart Communications, Inc. (SMART)
.smile	generic	Amazon Registry Services, Inc.
.sn	country-code	Universite Cheikh Anta Diop
.sncf	generic	Société Nationale SNCF
.so	country-code	Ministry of Post and Telecommunications
.soccer	generic	Binky Moon, LLC
.social	generic	Dog Beach, LLC
.softbank	generic	SoftBank Group Corp.
.software	generic	Dog Beach, LLC
.sohu	generic	Sohu.com Limited
.solar	generic	Binky Moon, LLC
.solutions	generic	Binky Moon, LLC
.song	generic	Amazon Registry Services, Inc.
.sony	generic	Sony Corporation
.soy	generic	Charleston Road Registry Inc.
.spa	generic	Asia Spa and Wellness Promotion Council Limited
.space	generic	Radix Technologies Inc.
.spiegel	generic	Not assigned
.sport	generic	SportAccord
.spot	generic	Amazon Registry Services, Inc.
.spreadbetting	generic	Not assigned
.sr	country-code	Telesur
.srl	generic	InterNetX Corp.
.srt	generic	Not assigned
.ss	country-code	National Communication Authority (NCA)
.st	country-code	Tecnisys
.stada	generic	STADA Arzneimittel AG
.staples	generic	Staples, Inc.
.star	generic	Star India Private Limited
.starhub	generic	Not assigned
.statebank	generic	STATE BANK OF INDIA
.statefarm	generic	State Farm Mutual Automobile Insurance Company
.statoil	generic	Not assigned
.stc	generic	Saudi Telecom Company
.stcgroup	generic	Saudi Telecom Company
.stockholm	generic	Stockholms kommun
.storage	generic	XYZ.COM LLC
.store	generic	Radix Technologies Inc.
.stream	generic	dot Stream Limited
.studio	generic	Dog Beach, LLC
.study	generic	Registry Services, LLC
.style	generic	Binky Moon, LLC
.su	country-code	Russian Institute for Development of Public Networks (ROSNIIROS)
.sucks	generic	Vox Populi Registry Ltd.
.supplies	generic	Binky Moon, LLC
.supply	generic	Binky Moon, LLC
.support	generic	Binky Moon, LLC
.surf	generic	Registry Services, LLC
.surgery	generic	Binky Moon, LLC
.suzuki	generic	SUZUKI MOTOR CORPORATION
.sv	country-code	SVNet
.swatch	generic	The Swatch Group Ltd
.swiftcover	generic	Not assigned
.swiss	generic	Swiss Confederation
.sx	country-code	SX Registry SA B.V.
.sy	country-code	National Agency for Network Services (NANS)
.sydney	generic	State of New South Wales, Department of Premier and Cabinet
.symantec	generic	Not assigned
.systems	generic	Binky Moon, LLC
.sz	country-code	University of Swaziland Department of Computer Science
.tab	generic	Tabcorp Holdings Limited
.taipei	generic	Taipei City Government
.talk	generic	Amazon Registry Services, Inc.
.taobao	generic	Alibaba Group Holding Limited
.target	generic	Target Domain Holdings, LLC
.tatamotors	generic	Tata Motors Ltd
.tatar	generic	Limited Liability Company "Coordination Center of Regional Domain of Tatarstan Republic"
.tattoo	generic	Registry Services, LLC
.tax	generic	Binky Moon, LLC
.taxi	generic	Binky Moon, LLC
.tc	country-code	Melrex TC
.tci	generic	Emergency Back-End Registry Operator Program - ICANN
.td	country-code	l'Agence de Développement des Technologies de l'Information et de la Communication (ADETIC)
.tdk	generic	TDK Corporation
.team	generic	Binky Moon, LLC
.tech	generic	Radix Technologies Inc.
.technology	generic	Binky Moon, LLC
.tel	sponsored	Telnames Ltd.
.telecity	generic	Not assigned
.telefonica	generic	Not assigned
.temasek	generic	Temasek Holdings (Private) Limited
.tennis	generic	Binky Moon, LLC
.teva	generic	Teva Pharmaceutical Industries Limited
.tf	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.tg	country-code	Autorité de Régulation des Communications Electroniques et des Postes (ARCEP)
.th	country-code	Thai Network Information Center Foundation
.thd	generic	Home Depot Product Authority, LLC
.theater	generic	Binky Moon, LLC
.theatre	generic	XYZ.COM LLC
.tiaa	generic	Teachers Insurance and Annuity Association of America
.tickets	generic	XYZ.COM LLC
.tienda	generic	Binky Moon, LLC
.tiffany	generic	Not assigned
.tips	generic	Binky Moon, LLC
.tires	generic	Binky Moon, LLC
.tirol	generic	punkt Tirol GmbH
.tj	country-code	Information Technology Center
.tjmaxx	generic	The TJX Companies, Inc.
.tjx	generic	The TJX Companies, Inc.
.tk	country-code	Telecommunication Tokelau Corporation (Teletok)
.tkmaxx	generic	The TJX Companies, Inc.
.tl	country-code	Autoridade Nacional de Comunicações
.tm	country-code	TM Domain Registry Ltd
.tmall	generic	Alibaba Group Holding Limited
.tn	country-code	Agence Tunisienne d'Internet
.to	country-code	Government of the Kingdom of Tonga H.R.H. Crown Prince Tupouto'a c/o Consulate of Tonga
.today	generic	Binky Moon, LLC
.tokyo	generic	GMO Registry, Inc.
.tools	generic	Binky Moon, LLC
.top	generic	.TOP Registry
.toray	generic	Toray Industries, Inc.
.toshiba	generic	TOSHIBA Corporation
.total	generic	TotalEnergies SE
.tours	generic	Binky Moon, LLC
.town	generic	Binky Moon, LLC
.toyota	generic	TOYOTA MOTOR CORPORATION
.toys	generic	Binky Moon, LLC
.tp	country-code	Not assigned
.tr	country-code	Bilgi Teknolojileri ve İletişim Kurumu (BTK)
.trade	generic	Elite Registry Limited
.trading	generic	Dog Beach, LLC
.training	generic	Binky Moon, LLC
.travel	sponsored	Dog Beach, LLC
.travelchannel	generic	Not assigned
.travelers	generic	Travelers TLD, LLC
.travelersinsurance	generic	Travelers TLD, LLC
.trust	generic	Internet Naming Co.
.trv	generic	Travelers TLD, LLC
.tt	country-code	University of the West Indies Faculty of Engineering
.tube	generic	Latin American Telecom LLC
.tui	generic	TUI AG
.tunes	generic	Amazon Registry Services, Inc.
.tushu	generic	Amazon Registry Services, Inc.
.tv	country-code	Ministry of Justice, Communications and Foreign Affairs
.tvs	generic	T V SUNDRAM IYENGAR & SONS PRIVATE LIMITED
.tw	country-code	Taiwan Network Information Center (TWNIC)
.tz	country-code	Tanzania Communications Regulatory Authority
.ua	country-code	Hostmaster Ltd.
.ubank	generic	National Australia Bank Limited
.ubs	generic	UBS AG
.uconnect	generic	Not assigned
.ug	country-code	Uganda Online Ltd.
.uk	country-code	Nominet UK
.um	country-code	Not assigned
.unicom	generic	China United Network Communications Corporation Limited
.university	generic	Binky Moon, LLC
.uno	generic	Radix Technologies Inc.
.uol	generic	UBN INTERNET LTDA.
.ups	generic	UPS Market Driver, Inc.
.us	country-code	Registry Services, LLC
.uy	country-code	SeCIU - Universidad de la Republica
.uz	country-code	Single Integrator for Creation and Support of State Information Systems UZINFOCOM
.va	country-code	Holy See - Vatican City State
.vacations	generic	Binky Moon, LLC
.vana	generic	D3 Registry LLC
.vanguard	generic	The Vanguard Group, Inc.
.vc	country-code	Ministry of Telecommunications, Science, Technology and Industry
.ve	country-code	Comisión Nacional de Telecomunicaciones (CONATEL)
.vegas	generic	Dot Vegas, Inc.
.ventures	generic	Binky Moon, LLC
.verisign	generic	VeriSign, Inc.
.versicherung	generic	tldbox GmbH
.vet	generic	Dog Beach, LLC
.vg	country-code	Telecommunications Regulatory Commission of the Virgin Islands
.vi	country-code	Virgin Islands Public Telecommunications System, Inc.
.viajes	generic	Binky Moon, LLC
.video	generic	Dog Beach, LLC
.vig	generic	VIENNA INSURANCE GROUP AG Wiener Versicherung Gruppe
.viking	generic	Viking River Cruises (Bermuda) Ltd.
.villas	generic	Binky Moon, LLC
.vin	generic	Binky Moon, LLC
.vip	generic	Registry Services, LLC
.virgin	generic	Virgin Enterprises Limited
.visa	generic	Visa Worldwide Pte. Limited
.vision	generic	Binky Moon, LLC
.vista	generic	Not assigned
.vistaprint	generic	Not assigned
.viva	generic	Saudi Telecom Company
.vivo	generic	Telefonica Brasil S.A.
.vlaanderen	generic	DNS.be vzw
.vn	country-code	Viet Nam Internet Network Information Center (VNNIC)
.vodka	generic	Registry Services, LLC
.volkswagen	generic	Not assigned
.volvo	generic	Volvo Holding Sverige Aktiebolag
.vote	generic	Monolith Registry LLC
.voting	generic	Valuetainment Corp.
.voto	generic	Monolith Registry LLC
.voyage	generic	Binky Moon, LLC
.vu	country-code	Telecommunications Radiocommunications and Broadcasting Regulator (TRBR)
.vuelos	generic	Not assigned
.wales	generic	Nominet UK
.walmart	generic	Wal-Mart Stores, Inc.
.walter	generic	Sandvik AB
.wang	generic	Zodiac Wang Limited
.wanggou	generic	Amazon Registry Services, Inc.
.warman	generic	Not assigned
.watch	generic	Binky Moon, LLC
.watches	generic	Identity Digital Limited
.weather	generic	International Business Machines Corporation
.weatherchannel	generic	International Business Machines Corporation
.webcam	generic	dot Webcam Limited
.weber	generic	Saint-Gobain Weber SA
.website	generic	Radix Technologies Inc.
.wed	generic	Emergency Back-End Registry Operator Program - ICANN
.wedding	generic	Registry Services, LLC
.weibo	generic	Sina Corporation
.weir	generic	Weir Group IP Limited
.wf	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.whoswho	generic	Who's Who Registry
.wien	generic	punkt.wien GmbH
.wiki	generic	Registry Services, LLC
.williamhill	generic	William Hill Organization Limited
.win	generic	First Registry Limited
.windows	generic	Microsoft Corporation
.wine	generic	Binky Moon, LLC
.winners	generic	The TJX Companies, Inc.
.wme	generic	William Morris Endeavor Entertainment, LLC
.wolterskluwer	generic	Wolters Kluwer N.V.
.woodside	generic	Woodside Petroleum Limited
.work	generic	Registry Services, LLC
.works	generic	Binky Moon, LLC
.world	generic	Binky Moon, LLC
.wow	generic	Amazon Registry Services, Inc.
.ws	country-code	Government of Samoa Ministry of Foreign Affairs & Trade
.wtc	generic	World Trade Centers Association, Inc.
.wtf	generic	Binky Moon, LLC
.xbox	generic	Microsoft Corporation
.xerox	generic	Xerox DNHC LLC
.xfinity	generic	Not assigned
.xihuan	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.xin	generic	Elegant Leader Limited
.测试	test	Not assigned
.कॉम	generic	VeriSign Sarl
.परीक्षा	test	Not assigned
.セール	generic	Amazon Registry Services, Inc.
.佛山	generic	Guangzhou YU Wei Information Technology Co., Ltd.
.ಭಾರತ	country-code	National Internet eXchange of India
.慈善	generic	Excellent First Limited
.集团	generic	Eagle Horizon Limited
.在线	generic	Beijing Tld Registry Technology Limited
.한국	country-code	KISA (Korea Internet & Security Agency)
.ଭାରତ	country-code	National Internet eXchange of India
.大众汽车	generic	Not assigned
.点看	generic	VeriSign Sarl
.คอม	generic	VeriSign Sarl
.ভাৰত	country-code	National Internet eXchange of India
.ভারত	country-code	National Internet Exchange of India
.八卦	generic	Zodiac Gemini Ltd
‏.ישראל‎	country-code	The Israel Internet Association (RA)
‏.موقع‎	generic	Helium TLDs Ltd
.বাংলা	country-code	Posts and Telecommunications Division
.公益	generic	China Organizational Name Administration Center
.公司	generic	China Internet Network Information Center (CNNIC)
.香格里拉	generic	Shangri-La International Hotel Management Limited
.网站	generic	Global Website TLD Asia Limited
.移动	generic	Identity Digital Limited
.我爱你	generic	Tycoon Treasure Limited
.москва	generic	Foundation for Assistance for Internet Technologies and Infrastructure Development (FAITID)
.испытание	test	Not assigned
.қаз	country-code	Association of IT Companies of Kazakhstan
.католик	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
.онлайн	generic	CORE Association
.сайт	generic	CORE Association
.联通	generic	China United Network Communications Corporation Limited
.срб	country-code	Serbian National Internet Domain Registry (RNIDS)
.бг	country-code	Imena.BG AD
.бел	country-code	Belarusian Cloud Technologies LLC
‏.קום‎	generic	VeriSign Sarl
.时尚	generic	RISE VICTORY LIMITED
.微博	generic	Sina Corporation
.테스트	test	Not assigned
.淡马锡	generic	Temasek Holdings (Private) Limited
.ファッション	generic	Amazon Registry Services, Inc.
.орг	generic	Public Interest Registry
.नेट	generic	VeriSign Sarl
.ストア	generic	Amazon Registry Services, Inc.
.アマゾン	generic	Amazon Registry Services, Inc.
.삼성	generic	SAMSUNG SDS CO., LTD
.சிங்கப்பூர்	country-code	Singapore Network Information Centre (SGNIC) Pte Ltd
.商标	generic	Internet DotTrademark Organisation Limited
.商店	generic	Binky Moon, LLC
.商城	generic	Zodiac Aquarius Limited
.дети	generic	The Foundation for Network Initiatives “The Smart Internet”
.мкд	country-code	Macedonian Academic Research Network Skopje
‏.טעסט‎	test	Not assigned
.ею	country-code	EURid vzw
.ポイント	generic	Amazon Registry Services, Inc.
.新闻	generic	Guangzhou YU Wei Information and Technology Co.,Ltd
.工行	generic	Not assigned
.家電	generic	Amazon Registry Services, Inc.
‏.كوم‎	generic	VeriSign Sarl
.中文网	generic	TLD REGISTRY LIMITED
.中信	generic	CITIC Group Corporation
.中国	country-code	China Internet Network Information Center (CNNIC)
.中國	country-code	China Internet Network Information Center (CNNIC)
.娱乐	generic	Binky Moon, LLC
.谷歌	generic	Charleston Road Registry Inc.
.భారత్	country-code	National Internet Exchange of India
.ලංකා	country-code	LK Domain Registry
.電訊盈科	generic	PCCW Enterprises Limited
.购物	generic	Nawang Heli(Xiamen) Network Service Co., LTD.
.測試	test	Not assigned
.クラウド	generic	Amazon Registry Services, Inc.
.ભારત	country-code	National Internet Exchange of India
.通販	generic	Amazon Registry Services, Inc.
.भारतम्	country-code	National Internet eXchange of India
.भारत	country-code	National Internet Exchange of India
.भारोत	country-code	National Internet eXchange of India
‏.آزمایشی‎	test	Not assigned
.பரிட்சை	test	Not assigned
.网店	generic	Zodiac Taurus Ltd.
.संगठन	generic	Public Interest Registry
.餐厅	generic	Internet DotTrademark Organisation Limited
.网络	generic	China Internet Network Information Center (CNNIC)
.ком	generic	VeriSign Sarl
.укр	country-code	Ukrainian Network Information Centre (UANIC), Inc.
.香港	country-code	Hong Kong Internet Registration Corporation Ltd.
.亚马逊	generic	Amazon Registry Services, Inc.
.诺基亚	generic	Not assigned
.食品	generic	Amazon Registry Services, Inc.
.δοκιμή	test	Not assigned
.飞利浦	generic	Koninklijke Philips N.V.
‏.إختبار‎	test	Not assigned
.台湾	country-code	Taiwan Network Information Center (TWNIC)
.台灣	country-code	Taiwan Network Information Center (TWNIC)
.手表	generic	Not assigned
.手机	generic	Beijing RITT-Net Technology Development Co., Ltd
.мон	country-code	Datacom Co.,Ltd
‏.الجزائر‎	country-code	CERIST
‏.عمان‎	country-code	Telecommunications Regulatory Authority (TRA)
‏.ارامكو‎	generic	Aramco Services Company
‏.ایران‎	country-code	Institute for Research in Fundamental Sciences (IPM)
‏.العليان‎	generic	Competrol (Luxembourg) Sarl
‏.اتصالات‎	generic	Not assigned
‏.امارات‎	country-code	Telecommunications and Digital Government Regulatory Authority (TDRA)
‏.بازار‎	generic	CORE Association
‏.موريتانيا‎	country-code	Université de Nouakchott Al Aasriya
‏.پاکستان‎	country-code	National Telecommunication Corporation
‏.الاردن‎	country-code	Ministry of Digital Economy and Entrepreneurship (MoDEE)
‏.موبايلي‎	generic	Not assigned
‏.بارت‎	country-code	National Internet eXchange of India
‏.بھارت‎	country-code	National Internet Exchange of India
‏.المغرب‎	country-code	Agence Nationale de Réglementation des Télécommunications (ANRT)
‏.ابوظبي‎	generic	Abu Dhabi Systems and Information Centre
‏.البحرين‎	country-code	Telecommunications Regulatory Authority (TRA)
‏.السعودية‎	country-code	Communications, Space and Technology Commission
‏.ڀارت‎	country-code	National Internet eXchange of India
‏.كاثوليك‎	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
‏.سودان‎	country-code	Sudan Internet Society
‏.همراه‎	generic	Emergency Back-End Registry Operator Program - ICANN
‏.عراق‎	country-code	Communications and Media Commission (CMC)
‏.مليسيا‎	country-code	MYNIC Berhad
.澳門	country-code	Macao Post and Telecommunications Bureau (CTT)
.닷컴	generic	VeriSign Sarl
.政府	generic	Net-Chinese Co., Ltd.
‏.شبكة‎	generic	International Domain Registry Pty. Ltd.
‏.بيتك‎	generic	Kuwait Finance House
‏.عرب‎	generic	League of Arab States
.გე	country-code	Information Technologies Development Center (ITDC)
.机构	generic	Public Interest Registry
.组织机构	generic	Public Interest Registry
.健康	generic	Stable Tone Limited
.ไทย	country-code	Thai Network Information Center Foundation
‏.سورية‎	country-code	National Agency for Network Services (NANS)
.招聘	generic	Jiang Yu Liang Cai Technology Company Limited
.рус	generic	Rusnames Limited
.рф	country-code	Coordination Center for TLD RU
.珠宝	generic	Not assigned
‏.تونس‎	country-code	Agence Tunisienne d'Internet
.大拿	generic	VeriSign Sarl
.ລາວ	country-code	Lao National Internet Center (LANIC), Ministry of Technology and Communications
.みんな	generic	Charleston Road Registry Inc.
.グーグル	generic	Charleston Road Registry Inc.
.ευ	country-code	EURid vzw
.ελ	country-code	ICS-FORTH GR
.世界	generic	Stable Tone Limited
.書籍	generic	Amazon Registry Services, Inc.
.ഭാരതം	country-code	National Internet eXchange of India
.ਭਾਰਤ	country-code	National Internet Exchange of India
.网址	generic	KNET Co., Ltd
.닷넷	generic	VeriSign Sarl
.コム	generic	VeriSign Sarl
.天主教	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
.游戏	generic	Binky Moon, LLC
.vermögensberater	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.vermögensberatung	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.企业	generic	Binky Moon, LLC
.信息	generic	Beijing Tele-info Technology Co., Ltd.
.嘉里大酒店	generic	Kerry Trading Co. Limited
.嘉里	generic	Kerry Trading Co. Limited
‏.مصر‎	country-code	National Telecommunication Regulatory Authority - NTRA
‏.قطر‎	country-code	Communications Regulatory Authority
.广东	generic	Guangzhou YU Wei Information Technology Co., Ltd.
.இலங்கை	country-code	LK Domain Registry
.இந்தியா	country-code	National Internet Exchange of India
.հայ	country-code	"Internet Society" Non-governmental Organization
.新加坡	country-code	Singapore Network Information Centre (SGNIC) Pte Ltd
‏.فلسطين‎	country-code	Ministry of Telecom & Information Technology (MTIT)
.テスト	test	Not assigned
.政务	generic	China Organizational Name Administration Center
.xperia	generic	Not assigned
.xxx	sponsored	ICM Registry LLC
.xyz	generic	XYZ.COM LLC
.yachts	generic	XYZ.COM LLC
.yahoo	generic	Yahoo Inc.
.yamaxun	generic	Amazon Registry Services, Inc.
.yandex	generic	Yandex Europe B.V.
.ye	country-code	TeleYemen
.yodobashi	generic	YODOBASHI CAMERA CO.,LTD.
.yoga	generic	Registry Services, LLC
.yokohama	generic	GMO Registry, Inc.
.you	generic	Amazon Registry Services, Inc.
.youtube	generic	Charleston Road Registry Inc.
.yt	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.yun	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.za	country-code	ZA Domain Name Authority
.zappos	generic	Amazon Registry Services, Inc.
.zara	generic	Industria de Diseño Textil, S.A. (INDITEX, S.A.)
.zero	generic	Amazon Registry Services, Inc.
.zip	generic	Charleston Road Registry Inc.
.zippo	generic	Not assigned
.zm	country-code	Zambia Information and Communications Technology Authority (ZICTA)
.zone	generic	Binky Moon, LLC
.zuerich	generic	Kanton Zürich (Canton of Zurich)
.zw	country-code	Postal and Telecommunications Regulatory Authority of Zimbabwe (POTRAZ)

__ICCTLD__
# https://en.wikipedia.org/wiki/Country_code_top-level_domain#Internationalized_ccTLDs
# https://en.wikipedia.org/wiki/Internationalized_country_code_top-level_domain#List
# https://www.icann.org/resources/pages/string-evaluation-completion-2014-02-19-en
# (update 2025-01-16)
# DNS name	IDN ccTLD	Country/Region	Language	Script	Transliteration	Comments	Other ccTLD	DNSSEC
xn--lgbbat1ad8j	.الجزائر	Algeria	Arabic	Arabic (Arabic)	al-Jazā'ir		.dz	No
xn--y9a3aq	.հայ	Armenia	Armenian	Armenian	hay		.am	Yes
xn--mgbcpq6gpa1a	.البحرين	Bahrain	Arabic	Arabic	al-Baḥrain	Not in use	.bh	Yes
xn--54b7fta0cc	.বাংলা	Bangladesh	Bengali	Bengali	Bangla		.bd	No
xn--90ais	.бел	Belarus	Belarusian	Cyrillic	bel		.by	Yes
xn--90ae	.бг[16]	Bulgaria	Bulgarian	Cyrillic	bg		.bg	Yes
xn--fiqs8s	.中国	China	Chinese	Chinese (Simplified)	Zhōngguó		.cn	Yes
xn--fiqz9s	.中國	China	Chinese	Chinese (Traditional)	Zhōngguó		.cn	Yes
xn--wgbh1c	.مصر	Egypt	Arabic	Arabic (Arabic)	Miṣr / Maṣr[17]		.eg	Yes
xn--e1a4c	.ею	European Union	Bulgarian	Cyrillic	eyu		.eu	Yes
xn--qxa6a	.ευ	European Union	Greek	Greek	ey	In use since 2022	.eu	Yes
xn--node	.გე	Georgia	Georgian	Georgian (Mkhedruli)	GE		.ge	No
xn--qxam	.ελ[16]	Greece	Greek	Greek	el	In use since July 2018	.gr	Yes
xn--j6w193g	.香港	Hong Kong	Chinese	Chinese (Simplified and Traditional)	Hoeng1 gong2 / Xiānggǎng		.hk	Yes
xn--h2brj9c	.भारत	India	Hindi	Devanagari	Bhārat	Became available 27 August 2014[18]	.in	Yes
xn--mgbbh1a71e	.بھارت	India	Urdu	Arabic (Urdu)	Bhārat	Became available 2017	.in	Yes
xn--fpcrj9c3d	.భారత్	India	Telugu	Telugu	Bhārat	Became available 2017	.in	Yes
xn--gecrj9c	.ભારત	India	Gujarati	Gujarati	Bhārat	Became available 2017	.in	Yes
xn--s9brj9c	.ਭਾਰਤ	India	Punjabi	Gurmukhī	Bhārat	Became available 2017	.in	Yes
xn--xkc2dl3a5ee0h	.இந்தியா	India	Tamil	Tamil	Intiyā	Became available 2015	.in	Yes
xn--45brj9c	.ভারত	India	Bengali	Bengali	Bharôt	Became available 2017	.in	Yes
xn--2scrj9c	.ಭಾರತ	India	Kannada	Kannada	Bhārata	Became available 2020	.in	Yes
xn--rvc1e0am3e	.ഭാരതം	India	Malayalam	Malayalam	Bhāratam	Became available 2020	.in	Yes
xn--45br5cyl	.ভাৰত	India	Assamese	Bengali	Bharatam	Became available 2022	.in	Yes
xn--3hcrj9c	.ଭାରତ	India	Oriya	Oriya	Bhārat	Became available 2021	.in	Yes
xn--mgbbh1a	.بارت	India	Kashmiri	Arabic (Kashmiri)	Bārat	Became available 2022	.in	Yes
xn--h2breg3eve	.भारतम्	India	Sanskrit	Devanagari	Bhāratam	Became available 2022	.in	Yes
xn--h2brj9c8c	.भारोत	India	Santali	Devanagari	Bharot	Became available 2022	.in	Yes
xn--mgbgu82a	.ڀارت	India	Sindhi	Arabic (Sindhi)	Bhārat	Became available 2022	.in	Yes
xn--mgba3a4f16a	.ایران	Iran	Persian	Arabic (Persian)	Īrān		.ir	No
xn--mgbtx2b	.عراق	Iraq	Arabic	Arabic (Arabic)	ʿIrāq	Not in use	.iq	No
xn--4dbrk0ce	.ישראל	Israel	Hebrew	Hebrew	Israel	Became available 2022	.il	Yes
xn--mgbayh7gpa	.الاردن	Jordan	Arabic	Arabic (Arabic)	al-Urdun		.jo	No
xn--80ao21a	.қаз	Kazakhstan	Kazakh	Cyrillic (Kazakh)	qaz		.kz	No
xn--q7ce6a	.ລາວ	Laos	Lao	Lao	Lao	Became available 2020	.la	Yes
xn--mix082f	.澳门	Macao	Chinese	Chinese (Simplified)	Ou3 mun4 / Àomén	Not in use	.mo	No
xn--mix891f	.澳門	Macao	Chinese	Chinese (Traditional)	Ou3 mun4 / Àomén	Became available 2020	.mo	No
xn--mgbx4cd0ab	.مليسيا	Malaysia	Malay	Arabic (Jawi)	Malaysīyā		.my	Yes
xn--mgbah1a3hjkrd	.موريتانيا	Mauritania	Arabic	Arabic (Arabic)	Mūrītāniyā		.mr	Yes
xn--l1acc	.мон	Mongolia	Mongolian	Cyrillic (Mongolian)	mon		.mn	Yes
xn--mgbc0a9azcg	.المغرب	Morocco	Arabic	Arabic (Arabic)	al-Maġrib		.ma	No
xn--d1alf	.мкд	North Macedonia	Macedonian	Cyrillic (Macedonian)	mkd		.mk	No
xn--mgb9awbf	.عمان	Oman	Arabic	Arabic (Arabic)	ʿUmān		.om	No
xn--mgbai9azgqp6j	.پاکستان	Pakistan	Urdu	Arabic (Urdu)	Pākistān		.pk	Yes
xn--ygbi2ammx	.فلسطين	Palestinian Authority	Arabic	Arabic (Arabic)	Filasṭīn		.ps	No
xn--wgbl6a	.قطر	Qatar	Arabic	Arabic (Arabic)	Qaṭar		.qa	No
xn--p1ai	.рф	Russia	Russian	Cyrillic (Russian)	rf		.ru	Yes
xn--mgberp4a5d4ar	.السعودية	Saudi Arabia	Arabic	Arabic (Arabic)	as-Suʿūdīya		.sa	Yes
xn--90a3ac	.срб	Serbia	Serbian	Cyrillic (Serbian)	srb		.rs	Yes
xn--yfro4i67o	.新加坡	Singapore	Chinese	Chinese (Simplified and Traditional)	Xīnjiāpō		.sg	Yes
xn--clchc0ea0b2g2a9gcd	.சிங்கப்பூர்	Singapore	Tamil	Tamil	Cinkappūr		.sg	Yes
xn--3e0b707e	.한국	South Korea	Korean	Hangul	Hanguk		.kr	Yes
xn--fzc2c9e2c	.ලංකා	Sri Lanka	Sinhala	Sinhala	Lanka		.lk	No
xn--xkc2al3hye2a	.இலங்கை	Sri Lanka	Tamil	Tamil	Ilaṅkai		.lk	No
xn--mgbpl2fh	.سودان	Sudan	Arabic	Arabic (Arabic)	Sūdān		.sd	No
xn--ogbpf8fl	.سورية	Syria	Arabic	Arabic (Arabic)	Sūriyya		.sy	No
xn--kprw13d	.台湾	Taiwan	Chinese	Chinese (Simplified)	Táiwān		.tw	Yes
xn--kpry57d	.台灣	Taiwan	Chinese	Chinese (Traditional)	Táiwān		.tw	Yes
xn--o3cw4h	.ไทย	Thailand	Thai	Thai	Thai		.th	Yes
xn--pgbs0dh	.تونس	Tunisia	Arabic	Arabic (Arabic)	Tūnis		.tn	Yes
xn--j1amh	.укр	Ukraine	Ukrainian	Cyrillic (Ukrainian)	ukr		.ua	No
xn--mgbaam7a8h	.امارات	United Arab Emirates	Arabic	Arabic (Arabic)	Imārāt		.ae	No
xn--mgb2ddes	.اليمن	Yemen	Arabic	Arabic (Arabic)	al-Yaman	Not delegated	.ye	No
__INTERNATIONALIZED_GEOGRAPHIC_TLD__
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Internationalized_geographic_top-level_domains
# (update 2025-01-16)
# DNS name	Display name	Entity	Language	Script	Transliteration	Notes	Other TLD	IDN	DNSSEC
xn--1qqw23a[100]	.佛山	Foshan, China	Chinese	Chinese (Simplified)	fat6 saan1	[160]		Yes	Yes
xn--xhq521b[100]	.广东	Guangdong, China	Chinese	Chinese (Simplified)	gwong2 dung1	[11]			
xn--80adxhks[100]	.москва [ru]	Moscow, Russia	Russian	Cyrillic (Russian)	moskva	[161]	.moscow	Russian[12]	Yes
xn--p1acf[100]	.рус	Russian language, post-Soviet states	Russian	Cyrillic (Russian)	rus	[11]	.su		
xn--mgbca7dzdo[100]	.ابوظبي	Abu Dhabi	Arabic	Arabic	Abū Ẓabī	[11]	.abudhabi		
xn--ngbrx[100]	.عرب	Arab	Arabic	Arabic	‘Arab	[11]			    
__INTERNATIONALIZED_BRAND_TLD__
# Internationalized brand top-level domains
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Internationalized_brand_top-level_domains
# (update 2025-01-16)
# DNS name	IDN TLD	Entity	Script	Transliteration	Comments	DNSSEC
xn--jlq480n2rg	.亚马逊	Amazon	Chinese (Simplified)	Yàmǎxùn	[236]	Yes
xn—cckwcxetd	.アマゾン	Amazon	Katakana	amazon	[237]	Yes
xn--mgba3a3ejt	.ارامكو	Aramco Services Company	Arabic		[11]	
xn--mgbaakc7dvf	.اتصالات	Emirates Telecommunications Corporation (trading as Etisalat)	Arabic		[11]	
xn--8y0a063a	.联通	China United Network Communications Corporation Limited	Chinese (Simplified)	Liántōng	[11]	
xn--6frz82g	.移动	China Mobile Communications Corporation	Chinese (Simplified)	Yídòng		
xn--fiq64b	.中信	CITIC Group	Chinese	zhōngxìn	[238]	Yes
xn--5su34j936bgsg	.香格里拉	Shangri‐La International Hotel Management Limited	Chinese	Xiānggélǐlā	[11]	
xn--b4w605ferd	.淡马锡	Temasek Holdings (Private) Limited	Chinese (Simplified)	Dànmǎxī	[11]	
xn--3oq18vl8pn36a	.大众汽车	Volkswagen (China) Investment Co., Ltd.	Chinese (Simplified)	Dàzhòngqìchē	[11]	
xn--vermgensberater-ctb	.vermögensberater	Deutsche Vermögensberatung Aktiengesellschaft	Latin		[239]	Yes
xn--vermgensberatung-pwb	.vermögensberatung	Deutsche Vermögensberatung Aktiengesellschaft	Latin		[240]	Yes
xn--qcka1pmc	.グーグル	Google	Katakana	gūguru	[241]	Yes
xn--flw351e	.谷歌	Google	Chinese	gǔgē	[242]	Yes
xn--estv75g	.工行	Industrial and Commercial Bank of China Limited	Chinese	Gōngháng	[11]	
xn--w4rs40l	.嘉里	Kerry Trading Co. Limited	Chinese	Jiālǐ	[11]	
xn--w4r85el8fhu5dnra	.嘉里大酒店	Kerry Trading Co. Limited	Chinese	Jiālǐdàjiǔdiàn	[11]	
xn--kcrx77d1x4a	.飞利浦	Koninklijke Philips N.V.	Chinese (Simplified)	Fēilìpǔ	[11]	
xn--jlq61u9w7b	.诺基亚	Nokia Corporation	Chinese (Simplified)	Nuòjīyà	[11][243]	
xn--fzys8d69uvgm	.電訊盈科	PCCW Enterprises Limited	Chinese (Traditional)	din6 soen3 jing4 fo1	[11]	
xn--cg4bki	.삼성	Samsung	Hangul	samseong	[244]	Yes
__INTERNATIONALIZED_TEST_TLD__
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Test_TLDs
xn--kgbechtv	إختبار.	ik͡htibār	Arabic	Arabic	http://مثال.إختبار
xn--hgbk6aj7f53bba	آزمایشی.	ậzmạy̰sẖy	Persian	Perso-Arabic	http://مثال.آزمایشی
xn--0zwm56d	.测试	cèshì	Chinese Simplified	Chinese	http://例子.测试
xn--g6w251d	.測試	cèshì	Chinese Traditional	Chinese	http://例子.測試
xn--80akhbyknj4f	.испытание	ispytánije	Russian	Cyrillic	http://пример.испытание
xn--11b5bs3a9aj6g	.परीक्षा	parīkṣā	Hindi	Devanagari	http://उदाहरण.परीक्षा
xn--jxalpdlp	.δοκιμή	dokimé	Greek	Greek	http://παράδειγμα.δοκιμή
xn--9t4b11yi5a	.테스트	teseuteu	Korean	Hangul	http://실례.테스트
xn--deba0ad	טעסט.	test	Yiddish	Hebrew	http://בײַשפּיל.טעסט
xn--zckzah	.テスト	tesuto	Japanese	Katakana[229]	http://例え.テスト
xn--hlcj6aya9esc7a	.பரிட்சை	pariṭcai	Tamil	Tamil	http://உதாரணம்.பரிட்சை
'''


TopLevelDomain._read_data()


if __name__ == '__main__':
    for line in fileinput.input():
        line = line.replace('\n', '')
        (cc, freq) = line.split('\t')
        tld = TopLevelDomain(cc)
        # print(tld)
        sub_type = ""
        if tld.sub_type is not None:
            sub_type = tld.sub_type
        print('\t'.join([cc, tld.tld_type, tld.first_level, sub_type, freq]))
