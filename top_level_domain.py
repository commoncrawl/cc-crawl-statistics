import fileinput
import idna
import re


class TopLevelDomain:
    """Classify top-level domains (TLDs) to provide the following information:
- type: generic, country-code, ...
- """

    tld_ccs = {}
    tld_types = {}

    def __init__(self, tld):
        self.tld = tld = tld.lower()
        self.first_level = self.tld
        self.tld_type = None
        self.sub_type = None
        if tld in TopLevelDomain.tld_ccs:
            self.first_level = TopLevelDomain.tld_ccs[tld]
        elif tld.find('.'):
            self.first_level = re.sub('^.+\.', '', tld)
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
                TopLevelDomain.tld_types[tld] = tld_type
                idn = idna.encode(tld).decode('utf-8')
                if idn != tld:
                    TopLevelDomain.tld_types[idn] = tld_type
            elif state == 'ICCTLD':
                (dns, idn, _country, _lang, _script,
                 _translit, _comment, cctld, _dnssec) = line.split('\t')
                dns = dns.lstrip('.')
                cctld = cctld.lstrip('.')
                idn = idn.lstrip('.')
                for tld in (dns, idn):
                    TopLevelDomain.tld_types[tld] = 'internationalized CC TLD'
                    TopLevelDomain.tld_ccs[tld] = cctld
            elif state == 'INTERNATIONAL_BRAND_TLD':
                (dns, idn, _entity, _script, _translit,
                 _comments, _dnssec) = line.split('\t')
                dns = dns.lstrip('.')
                idn = idn.lstrip('.')
                TopLevelDomain.tld_types[dns] = 'internationalized brand TLD'
                TopLevelDomain.tld_types[idn] = 'internationalized brand TLD'
            elif state == 'INTERNATIONAL_TEST_TLD':
                (dns, idn, _translit, _lang, _script, _test) = line.split('\t')
                dns = dns.lstrip('.')
                idn = idn.lstrip('.')
                TopLevelDomain.tld_types[dns] = 'internationalized test TLD'
                TopLevelDomain.tld_types[idn] = 'internationalized test TLD'

    __DATA__ = '''\
__IANA__
# http://www.iana.org/domains/root/db
# (update 2016-12-14)
# Domain	Type	Sponsoring Organisation
.aaa	generic	American Automobile Association, Inc.
.aarp	generic	AARP
.abarth	generic	Fiat Chrysler Automobiles N.V.
.abb	generic	ABB Ltd
.abbott	generic	Abbott Laboratories, Inc.
.abbvie	generic	AbbVie Inc.
.abc	generic	Disney Enterprises, Inc.
.able	generic	Able Inc.
.abogado	generic	Top Level Domain Holdings Limited
.abudhabi	generic	Abu Dhabi Systems and Information Centre
.ac	country-code	"Network Information Center (AC Domain Registry) c/o Cable and Wireless (Ascension Island)"
.academy	generic	Half Oaks, LLC
.accenture	generic	Accenture plc
.accountant	generic	dot Accountant Limited
.accountants	generic	Knob Town, LLC
.aco	generic	ACO Severin Ahlmann GmbH & Co. KG
.active	generic	The Active Network, Inc
.actor	generic	United TLD Holdco Ltd.
.ad	country-code	Andorra Telecom
.adac	generic	Allgemeiner Deutscher Automobil-Club e.V. (ADAC)
.ads	generic	Charleston Road Registry Inc.
.adult	generic	ICM Registry AD LLC
.ae	country-code	Telecommunication Regulatory Authority (TRA)
.aeg	generic	Aktiebolaget Electrolux
.aero	sponsored	Societe Internationale de Telecommunications Aeronautique (SITA INC USA)
.aetna	generic	Aetna Life Insurance Company
.af	country-code	Ministry of Communications and IT
.afamilycompany	generic	Johnson Shareholdings, Inc.
.afl	generic	Australian Football League
.ag	country-code	UHSA School of Medicine
.agakhan	generic	Fondation Aga Khan (Aga Khan Foundation)
.agency	generic	Steel Falls, LLC
.ai	country-code	Government of Anguilla
.aig	generic	American International Group, Inc.
.aigo	generic	aigo Digital Technology Co,Ltd.
.airbus	generic	Airbus S.A.S.
.airforce	generic	United TLD Holdco Ltd.
.airtel	generic	Bharti Airtel Limited
.akdn	generic	Fondation Aga Khan (Aga Khan Foundation)
.al	country-code	Electronic and Postal Communications Authority - AKEP
.alfaromeo	generic	Fiat Chrysler Automobiles N.V.
.alibaba	generic	Alibaba Group Holding Limited
.alipay	generic	Alibaba Group Holding Limited
.allfinanz	generic	Allfinanz Deutsche Vermögensberatung Aktiengesellschaft
.allstate	generic	Allstate Fire and Casualty Insurance Company
.ally	generic	Ally Financial Inc.
.alsace	generic	REGION D ALSACE
.alstom	generic	ALSTOM
.am	country-code	"Internet Society" Non-governmental Organization
.americanexpress	generic	American Express Travel Related Services Company, Inc.
.americanfamily	generic	AmFam, Inc.
.amex	generic	American Express Travel Related Services Company, Inc.
.amfam	generic	AmFam, Inc.
.amica	generic	Amica Mutual Insurance Company
.amsterdam	generic	Gemeente Amsterdam
.an	country-code	Retired
.analytics	generic	Campus IP LLC
.android	generic	Charleston Road Registry Inc.
.anquan	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.anz	generic	Australia and New Zealand Banking Group Limited
.ao	country-code	Faculdade de Engenharia da Universidade Agostinho Neto
.aol	generic	AOL Inc.
.apartments	generic	June Maple, LLC
.app	generic	Charleston Road Registry Inc.
.apple	generic	Apple Inc.
.aq	country-code	Antarctica Network Information Centre Limited
.aquarelle	generic	Aquarelle.com
.ar	country-code	Presidencia de la Nación – Secretaría Legal y Técnica
.aramco	generic	Aramco Services Company
.archi	generic	STARTING DOT LIMITED
.army	generic	United TLD Holdco Ltd.
.arpa	infrastructure	Internet Architecture Board (IAB)
.art	generic	UK Creative Ideas Limited
.arte	generic	Association Relative à la Télévision Européenne G.E.I.E.
.as	country-code	AS Domain Registry
.asda	generic	Wal-Mart Stores, Inc.
.asia	sponsored	DotAsia Organisation Ltd.
.associates	generic	Baxter Hill, LLC
.at	country-code	nic.at GmbH
.athleta	generic	The Gap, Inc.
.attorney	generic	United TLD Holdco, Ltd
.au	country-code	.au Domain Administration (auDA)
.auction	generic	United TLD HoldCo, Ltd.
.audi	generic	AUDI Aktiengesellschaft
.audible	generic	Amazon Registry Services, Inc.
.audio	generic	Uniregistry, Corp.
.auspost	generic	Australian Postal Corporation
.author	generic	Amazon Registry Services, Inc.
.auto	generic	Cars Registry Limited
.autos	generic	DERAutos, LLC
.avianca	generic	Aerovias del Continente Americano S.A. Avianca
.aw	country-code	SETAR
.aws	generic	Amazon Registry Services, Inc.
.ax	country-code	Ålands landskapsregering
.axa	generic	AXA SA
.az	country-code	IntraNS
.azure	generic	Microsoft Corporation
.ba	country-code	Universtiy Telinformatic Centre (UTIC)
.baby	generic	Johnson & Johnson Services, Inc.
.baidu	generic	Baidu, Inc.
.banamex	generic	Citigroup Inc.
.bananarepublic	generic	The Gap, Inc.
.band	generic	United TLD Holdco, Ltd
.bank	generic	fTLD Registry Services, LLC
.bar	generic	Punto 2012 Sociedad Anonima Promotora de Inversion de Capital Variable
.barcelona	generic	Municipi de Barcelona
.barclaycard	generic	Barclays Bank PLC
.barclays	generic	Barclays Bank PLC
.barefoot	generic	Gallo Vineyards, Inc.
.bargains	generic	Half Hallow, LLC
.baseball	generic	MLB Advanced Media DH, LLC
.basketball	generic	Fédération Internationale de Basketball (FIBA)
.bauhaus	generic	Werkhaus GmbH
.bayern	generic	Bayern Connect GmbH
.bb	country-code	"Government of Barbados Ministry of Economic Affairs and Development Telecommunications Unit"
.bbc	generic	British Broadcasting Corporation
.bbt	generic	BB&T Corporation
.bbva	generic	BANCO BILBAO VIZCAYA ARGENTARIA, S.A.
.bcg	generic	The Boston Consulting Group, Inc.
.bcn	generic	Municipi de Barcelona
.bd	country-code	"Ministry of Post & Telecommunications Bangladesh Secretariat"
.be	country-code	DNS Belgium vzw/asbl
.beats	generic	Beats Electronics, LLC
.beauty	generic	L'Oréal
.beer	generic	Top Level Domain Holdings Limited
.bentley	generic	Bentley Motors Limited
.berlin	generic	dotBERLIN GmbH & Co. KG
.best	generic	BestTLD Pty Ltd
.bestbuy	generic	BBY Solutions, Inc.
.bet	generic	Afilias plc
.bf	country-code	ARCE-AutoritÈ de RÈgulation des Communications Electroniques
.bg	country-code	Register.BG
.bh	country-code	Telecommunications Regulatory Authority (TRA)
.bharti	generic	Bharti Enterprises (Holding) Private Limited
.bi	country-code	Centre National de l'Informatique
.bible	generic	American Bible Society
.bid	generic	dot Bid Limited
.bike	generic	Grand Hollow, LLC
.bing	generic	Microsoft Corporation
.bingo	generic	Sand Cedar, LLC
.bio	generic	STARTING DOT LIMITED
.biz	generic-restricted	Neustar, Inc.
.bj	country-code	Benin Telecoms S.A.
.bl	country-code	Not assigned
.black	generic	Afilias plc
.blackfriday	generic	Uniregistry, Corp.
.blanco	generic	BLANCO GmbH + Co KG
.blockbuster	generic	Dish DBS Corporation
.blog	generic	Knock Knock WHOIS There, LLC
.bloomberg	generic	Bloomberg IP Holdings LLC
.blue	generic	Afilias plc
.bm	country-code	Registry General Department, Ministry of Home Affairs
.bms	generic	Bristol-Myers Squibb Company
.bmw	generic	Bayerische Motoren Werke Aktiengesellschaft
.bn	country-code	Brunei Darussalam Network Information Centre Sdn Bhd (BNNIC)
.bnl	generic	Banca Nazionale del Lavoro
.bnpparibas	generic	BNP Paribas
.bo	country-code	Agencia para el Desarrollo de la Información de la Sociedad en Bolivia
.boats	generic	DERBoats, LLC
.boehringer	generic	Boehringer Ingelheim International GmbH
.bofa	generic	NMS Services, Inc.
.bom	generic	Núcleo de Informação e Coordenação do Ponto BR - NIC.br
.bond	generic	Bond University Limited
.boo	generic	Charleston Road Registry Inc.
.book	generic	Amazon Registry Services, Inc.
.booking	generic	Booking.com B.V.
.boots	generic	THE BOOTS COMPANY PLC
.bosch	generic	Robert Bosch GMBH
.bostik	generic	Bostik SA
.boston	generic	Boston TLD Management, LLC
.bot	generic	Amazon Registry Services, Inc.
.boutique	generic	Over Galley, LLC
.box	generic	NS1 Limited
.bq	country-code	Not assigned
.br	country-code	Comite Gestor da Internet no Brasil
.bradesco	generic	Banco Bradesco S.A.
.bridgestone	generic	Bridgestone Corporation
.broadway	generic	Celebrate Broadway, Inc.
.broker	generic	DOTBROKER REGISTRY LTD
.brother	generic	Brother Industries, Ltd.
.brussels	generic	DNS.be vzw
.bs	country-code	The College of the Bahamas
.bt	country-code	Ministry of Information and Communications
.budapest	generic	Top Level Domain Holdings Limited
.bugatti	generic	Bugatti International SA
.build	generic	Plan Bee LLC
.builders	generic	Atomic Madison, LLC
.business	generic	Spring Cross, LLC
.buy	generic	Amazon Registry Services, INC
.buzz	generic	DOTSTRATEGY CO.
.bv	country-code	UNINETT Norid A/S
.bw	country-code	Botswana Communications Regulatory Authority (BOCRA)
.by	country-code	Reliable Software, Ltd.
.bz	country-code	University of Belize
.bzh	generic	Association www.bzh
.ca	country-code	Canadian Internet Registration Authority (CIRA) Autorité Canadienne pour les enregistrements Internet (ACEI)
.cab	generic	Half Sunset, LLC
.cafe	generic	Pioneer Canyon, LLC
.cal	generic	Charleston Road Registry Inc.
.call	generic	Amazon Registry Services, Inc.
.calvinklein	generic	PVH gTLD Holdings LLC
.cam	generic	AC Webconnecting Holding B.V.
.camera	generic	Atomic Maple, LLC
.camp	generic	Delta Dynamite, LLC
.cancerresearch	generic	Australian Cancer Research Foundation
.canon	generic	Canon Inc.
.capetown	generic	ZA Central Registry NPC trading as ZA Central Registry
.capital	generic	Delta Mill, LLC
.capitalone	generic	Capital One Financial Corporation
.car	generic	Cars Registry Limited
.caravan	generic	Caravan International, Inc.
.cards	generic	Foggy Hollow, LLC
.care	generic	Goose Cross, LLC
.career	generic	dotCareer LLC
.careers	generic	Wild Corner, LLC
.cars	generic	Cars Registry Limited
.cartier	generic	Richemont DNS Inc.
.casa	generic	Top Level Domain Holdings Limited
.case	generic	CNH Industrial N.V.
.caseih	generic	CNH Industrial N.V.
.cash	generic	Delta Lake, LLC
.casino	generic	Binky Sky, LLC
.cat	sponsored	Fundacio puntCAT
.catering	generic	New Falls. LLC
.catholic	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
.cba	generic	COMMONWEALTH BANK OF AUSTRALIA
.cbn	generic	The Christian Broadcasting Network, Inc.
.cbre	generic	CBRE, Inc.
.cbs	generic	CBS Domains Inc.
.cc	country-code	"eNIC Cocos (Keeling) Islands Pty. Ltd. d/b/a Island Internet Services"
.cd	country-code	Office Congolais des Postes et Télécommunications - OCPT
.ceb	generic	The Corporate Executive Board Company
.center	generic	Tin Mill, LLC
.ceo	generic	CEOTLD Pty Ltd
.cern	generic	European Organization for Nuclear Research ("CERN")
.cf	country-code	Societe Centrafricaine de Telecommunications (SOCATEL)
.cfa	generic	CFA Institute
.cfd	generic	DOTCFD REGISTRY LTD
.cg	country-code	ONPT Congo and Interpoint Switzerland
.ch	country-code	SWITCH The Swiss Education & Research Network
.chanel	generic	Chanel International B.V.
.channel	generic	Charleston Road Registry Inc.
.chase	generic	JPMorgan Chase Bank, National Association
.chat	generic	Sand Fields, LLC
.cheap	generic	Sand Cover, LLC
.chintai	generic	CHINTAI Corporation
.chloe	generic	Richemont DNS Inc.
.christmas	generic	Uniregistry, Corp.
.chrome	generic	Charleston Road Registry Inc.
.chrysler	generic	FCA US LLC.
.church	generic	Holly Fileds, LLC
.ci	country-code	INP-HB Institut National Polytechnique Felix Houphouet Boigny
.cipriani	generic	Hotel Cipriani Srl
.circle	generic	Amazon Registry Services, Inc.
.cisco	generic	Cisco Technology, Inc.
.citadel	generic	Citadel Domain LLC
.citi	generic	Citigroup Inc.
.citic	generic	CITIC Group Corporation
.city	generic	Snow Sky, LLC
.cityeats	generic	Lifestyle Domain Holdings, Inc.
.ck	country-code	Telecom Cook Islands Ltd.
.cl	country-code	NIC Chile (University of Chile)
.claims	generic	Black Corner, LLC
.cleaning	generic	Fox Shadow, LLC
.click	generic	Uniregistry, Corp.
.clinic	generic	Goose Park, LLC
.clinique	generic	The Estée Lauder Companies Inc.
.clothing	generic	Steel Lake, LLC
.cloud	generic	ARUBA PEC S.p.A.
.club	generic	.CLUB DOMAINS, LLC
.clubmed	generic	Club Méditerranée S.A.
.cm	country-code	Cameroon Telecommunications (CAMTEL)
.cn	country-code	China Internet Network Information Center (CNNIC)
.co	country-code	.CO Internet S.A.S.
.coach	generic	Koko Island, LLC
.codes	generic	Puff Willow, LLC
.coffee	generic	Trixy Cover, LLC
.college	generic	XYZ.COM LLC
.cologne	generic	NetCologne Gesellschaft für Telekommunikation mbH
.com	generic	VeriSign Global Registry Services
.comcast	generic	Comcast IP Holdings I, LLC
.commbank	generic	COMMONWEALTH BANK OF AUSTRALIA
.community	generic	Fox Orchard, LLC
.company	generic	Silver Avenue, LLC
.compare	generic	iSelect Ltd
.computer	generic	Pine Mill, LLC
.comsec	generic	VeriSign, Inc.
.condos	generic	Pine House, LLC
.construction	generic	Fox Dynamite, LLC
.consulting	generic	United TLD Holdco, LTD.
.contact	generic	Top Level Spectrum, Inc.
.contractors	generic	Magic Woods, LLC
.cooking	generic	Top Level Domain Holdings Limited
.cookingchannel	generic	Lifestyle Domain Holdings, Inc.
.cool	generic	Koko Lake, LLC
.coop	sponsored	DotCooperation LLC
.corsica	generic	Collectivité Territoriale de Corse
.country	generic	Top Level Domain Holdings Limited
.coupon	generic	Amazon Registry Services, Inc.
.coupons	generic	Black Island, LLC
.courses	generic	OPEN UNIVERSITIES AUSTRALIA PTY LTD
.cr	country-code	"National Academy of Sciences Academia Nacional de Ciencias"
.credit	generic	Snow Shadow, LLC
.creditcard	generic	Binky Frostbite, LLC
.creditunion	generic	CUNA Performance Resources, LLC
.cricket	generic	dot Cricket Limited
.crown	generic	Crown Equipment Corporation
.crs	generic	Federated Co-operatives Limited
.cruise	generic	Viking River Cruises (Bermuda) Ltd.
.cruises	generic	Spring Way, LLC
.csc	generic	Alliance-One Services, Inc.
.cu	country-code	"CENIAInternet Industria y San Jose Capitolio Nacional"
.cuisinella	generic	SALM S.A.S.
.cv	country-code	Agência Nacional das Comunicações (ANAC)
.cw	country-code	University of Curacao
.cx	country-code	Christmas Island Domain Administration Limited
.cy	country-code	University of Cyprus
.cymru	generic	Nominet UK
.cyou	generic	Beijing Gamease Age Digital Technology Co., Ltd.
.cz	country-code	CZ.NIC, z.s.p.o
.dabur	generic	Dabur India Limited
.dad	generic	Charleston Road Registry Inc.
.dance	generic	United TLD Holdco Ltd.
.date	generic	dot Date Limited
.dating	generic	Pine Fest, LLC
.datsun	generic	NISSAN MOTOR CO., LTD.
.day	generic	Charleston Road Registry Inc.
.dclk	generic	Charleston Road Registry Inc.
.dds	generic	Minds + Machines Group Limited
.de	country-code	DENIC eG
.deal	generic	Amazon Registry Services, Inc.
.dealer	generic	Dealer Dot Com, Inc.
.deals	generic	Sand Sunset, LLC
.degree	generic	United TLD Holdco, Ltd
.delivery	generic	Steel Station, LLC
.dell	generic	Dell Inc.
.deloitte	generic	Deloitte Touche Tohmatsu
.delta	generic	Delta Air Lines, Inc.
.democrat	generic	United TLD Holdco Ltd.
.dental	generic	Tin Birch, LLC
.dentist	generic	United TLD Holdco, Ltd
.desi	generic	Desi Networks LLC
.design	generic	Top Level Design, LLC
.dev	generic	Charleston Road Registry Inc.
.dhl	generic	Deutsche Post AG
.diamonds	generic	John Edge, LLC
.diet	generic	Uniregistry, Corp.
.digital	generic	Dash Park, LLC
.direct	generic	Half Trail, LLC
.directory	generic	Extra Madison, LLC
.discount	generic	Holly Hill, LLC
.discover	generic	Discover Financial Services
.dish	generic	Dish DBS Corporation
.diy	generic	Lifestyle Domain Holdings, Inc.
.dj	country-code	Djibouti Telecom S.A
.dk	country-code	Dansk Internet Forum
.dm	country-code	DotDM Corporation
.dnp	generic	Dai Nippon Printing Co., Ltd.
.do	country-code	"Pontificia Universidad Catolica Madre y Maestra Recinto Santo Tomas de Aquino"
.docs	generic	Charleston Road Registry Inc.
.doctor	generic	Brice Trail, LLC
.dodge	generic	FCA US LLC.
.dog	generic	Koko Mill, LLC
.doha	generic	Communications Regulatory Authority (CRA)
.domains	generic	Sugar Cross, LLC
.doosan	generic	Retired
.dot	generic	Dish DBS Corporation
.download	generic	dot Support Limited
.drive	generic	Charleston Road Registry Inc.
.dtv	generic	Dish DBS Corporation
.dubai	generic	Dubai Smart Government Department
.duck	generic	Johnson Shareholdings, Inc.
.dunlop	generic	The Goodyear Tire & Rubber Company
.duns	generic	The Dun & Bradstreet Corporation
.dupont	generic	E. I. du Pont de Nemours and Company
.durban	generic	ZA Central Registry NPC trading as ZA Central Registry
.dvag	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.dvr	generic	Hughes Satellite Systems Corporation
.dz	country-code	CERIST
.earth	generic	Interlink Co., Ltd.
.eat	generic	Charleston Road Registry Inc.
.ec	country-code	NIC.EC (NICEC) S.A.
.eco	generic	Big Room Inc.
.edeka	generic	EDEKA Verband kaufmännischer Genossenschaften e.V.
.edu	sponsored	EDUCAUSE
.education	generic	Brice Way, LLC
.ee	country-code	Eesti Interneti Sihtasutus (EIS)
.eg	country-code	"Egyptian Universities Network (EUN) Supreme Council of Universities"
.eh	country-code	Not assigned
.email	generic	Spring Madison, LLC
.emerck	generic	Merck KGaA
.energy	generic	Binky Birch, LLC
.engineer	generic	United TLD Holdco Ltd.
.engineering	generic	Romeo Canyon
.enterprises	generic	Snow Oaks, LLC
.epost	generic	Deutsche Post AG
.epson	generic	Seiko Epson Corporation
.equipment	generic	Corn Station, LLC
.er	country-code	Eritrea Telecommunication Services Corporation (EriTel)
.ericsson	generic	Telefonaktiebolaget L M Ericsson
.erni	generic	ERNI Group Holding AG
.es	country-code	Red.es
.esq	generic	Charleston Road Registry Inc.
.estate	generic	Trixy Park, LLC
.esurance	generic	Esurance Insurance Company
.et	country-code	Ethio telecom
.eu	country-code	EURid vzw/asbl
.eurovision	generic	European Broadcasting Union (EBU)
.eus	generic	Puntueus Fundazioa
.events	generic	Pioneer Maple, LLC
.everbank	generic	EverBank
.exchange	generic	Spring Falls, LLC
.expert	generic	Magic Pass, LLC
.exposed	generic	Victor Beach, LLC
.express	generic	Sea Sunset, LLC
.extraspace	generic	Extra Space Storage LLC
.fage	generic	Fage International S.A.
.fail	generic	Atomic Pipe, LLC
.fairwinds	generic	FairWinds Partners, LLC
.faith	generic	dot Faith Limited
.family	generic	United TLD Holdco Ltd.
.fan	generic	Asiamix Digital Ltd
.fans	generic	Asiamix Digital Limited
.farm	generic	Just Maple, LLC
.farmers	generic	Farmers Insurance Exchange
.fashion	generic	Top Level Domain Holdings Limited
.fast	generic	Amazon Registry Services, Inc.
.fedex	generic	Federal Express Corporation
.feedback	generic	Top Level Spectrum, Inc.
.ferrari	generic	Fiat Chrysler Automobiles N.V.
.ferrero	generic	Ferrero Trading Lux S.A.
.fi	country-code	Finnish Communications Regulatory Authority
.fiat	generic	Fiat Chrysler Automobiles N.V.
.fidelity	generic	Fidelity Brokerage Services LLC
.fido	generic	Rogers Communications Canada Inc.
.film	generic	Motion Picture Domain Registry Pty Ltd
.final	generic	Núcleo de Informação e Coordenação do Ponto BR - NIC.br
.finance	generic	Cotton Cypress, LLC
.financial	generic	Just Cover, LLC
.fire	generic	Amazon Registry Services, Inc.
.firestone	generic	Bridgestone Licensing Services, Inc.
.firmdale	generic	Firmdale Holdings Limited
.fish	generic	Fox Woods, LLC
.fishing	generic	Top Level Domain Holdings Limited
.fit	generic	Minds + Machines Group Limited
.fitness	generic	Brice Orchard, LLC
.fj	country-code	"The University of the South Pacific IT Services"
.fk	country-code	Falkland Islands Government
.flickr	generic	Yahoo! Domain Services Inc.
.flights	generic	Fox Station, LLC
.flir	generic	FLIR Systems, Inc.
.florist	generic	Half Cypress, LLC
.flowers	generic	Uniregistry, Corp.
.flsmidth	generic	Retired
.fly	generic	Charleston Road Registry Inc.
.fm	country-code	FSM Telecommunications Corporation
.fo	country-code	FO Council
.foo	generic	Charleston Road Registry Inc.
.food	generic	Lifestyle Domain Holdings, Inc.
.foodnetwork	generic	Lifestyle Domain Holdings, Inc.
.football	generic	Foggy Farms, LLC
.ford	generic	Ford Motor Company
.forex	generic	DOTFOREX REGISTRY LTD
.forsale	generic	United TLD Holdco, LLC
.forum	generic	Fegistry, LLC
.foundation	generic	John Dale, LLC
.fox	generic	FOX Registry, LLC
.fr	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.free	generic	Amazon Registry Services, Inc.
.fresenius	generic	Fresenius Immobilien-Verwaltungs-GmbH
.frl	generic	FRLregistry B.V.
.frogans	generic	OP3FT
.frontdoor	generic	Lifestyle Domain Holdings, Inc.
.frontier	generic	Frontier Communications Corporation
.ftr	generic	Frontier Communications Corporation
.fujitsu	generic	Fujitsu Limited
.fujixerox	generic	Xerox DNHC LLC
.fund	generic	John Castle, LLC
.furniture	generic	Lone Fields, LLC
.futbol	generic	United TLD Holdco, Ltd.
.fyi	generic	Silver Tigers, LLC
.ga	country-code	Agence Nationale des Infrastructures Numériques et des Fréquences (ANINF)
.gal	generic	Asociación puntoGAL
.gallery	generic	Sugar House, LLC
.gallo	generic	Gallo Vineyards, Inc.
.gallup	generic	Gallup, Inc.
.game	generic	Uniregistry, Corp.
.games	generic	United TLD Holdco Ltd.
.gap	generic	The Gap, Inc.
.garden	generic	Top Level Domain Holdings Limited
.gb	country-code	Reserved Domain - IANA
.gbiz	generic	Charleston Road Registry Inc.
.gd	country-code	The National Telecommunications Regulatory Commission (NTRC)
.gdn	generic	Joint Stock Company "Navigation-information systems"
.ge	country-code	Caucasus Online
.gea	generic	GEA Group Aktiengesellschaft
.gent	generic	Combell nv
.genting	generic	Resorts World Inc. Pte. Ltd.
.george	generic	Wal-Mart Stores, Inc.
.gf	country-code	Net Plus
.gg	country-code	Island Networks Ltd.
.ggee	generic	GMO Internet, Inc.
.gh	country-code	Network Computer Systems Limited
.gi	country-code	Sapphire Networks
.gift	generic	Uniregistry, Corp.
.gifts	generic	Goose Sky, LLC
.gives	generic	United TLD Holdco Ltd.
.giving	generic	Giving Limited
.gl	country-code	TELE Greenland A/S
.glade	generic	Johnson Shareholdings, Inc.
.glass	generic	Black Cover, LLC
.gle	generic	Charleston Road Registry Inc.
.global	generic	Dot Global Domain Registry Limited
.globo	generic	Globo Comunicação e Participações S.A
.gm	country-code	GM-NIC
.gmail	generic	Charleston Road Registry Inc.
.gmbh	generic	Extra Dynamite, LLC
.gmo	generic	GMO Internet, Inc.
.gmx	generic	1&1 Mail & Media GmbH
.gn	country-code	Centre National des Sciences Halieutiques de Boussoura
.godaddy	generic	Go Daddy East, LLC
.gold	generic	June Edge, LLC
.goldpoint	generic	YODOBASHI CAMERA CO.,LTD.
.golf	generic	Lone Falls, LLC
.goo	generic	NTT Resonant Inc.
.goodhands	generic	Allstate Fire and Casualty Insurance Company
.goodyear	generic	The Goodyear Tire & Rubber Company
.goog	generic	Charleston Road Registry Inc.
.google	generic	Charleston Road Registry Inc.
.gop	generic	Republican State Leadership Committee, Inc.
.got	generic	Amazon Registry Services, Inc.
.gov	sponsored	"General Services Administration Attn: QTDC, 2E08 (.gov Domain Registration)"
.gp	country-code	Networking Technologies Group
.gq	country-code	GETESA
.gr	country-code	ICS-FORTH GR
.grainger	generic	Grainger Registry Services, LLC
.graphics	generic	Over Madison, LLC
.gratis	generic	Pioneer Tigers, LLC
.green	generic	DotGreen Registry Limited
.gripe	generic	Corn Sunset, LLC
.group	generic	Romeo Town, LLC
.gs	country-code	Government of South Georgia and South Sandwich Islands (GSGSSI)
.gt	country-code	Universidad del Valle de Guatemala
.gu	country-code	"University of Guam Computer Center"
.guardian	generic	The Guardian Life Insurance Company of America
.gucci	generic	Guccio Gucci S.p.a.
.guge	generic	Charleston Road Registry Inc.
.guide	generic	Snow Moon, LLC
.guitars	generic	Uniregistry, Corp.
.guru	generic	Pioneer Cypress, LLC
.gw	country-code	Autoridade Reguladora Nacional - Tecnologias de Informação e Comunicação da Guiné-Bissau
.gy	country-code	University of Guyana
.hair	generic	L'Oreal
.hamburg	generic	Hamburg Top-Level-Domain GmbH
.hangout	generic	Charleston Road Registry Inc.
.haus	generic	United TLD Holdco, LTD.
.hbo	generic	HBO Registry Services, Inc.
.hdfc	generic	HOUSING DEVELOPMENT FINANCE CORPORATION LIMITED
.hdfcbank	generic	HDFC Bank Limited
.health	generic	DotHealth, LLC
.healthcare	generic	Silver Glen, LLC
.help	generic	Uniregistry, Corp.
.helsinki	generic	City of Helsinki
.here	generic	Charleston Road Registry Inc.
.hermes	generic	Hermes International
.hgtv	generic	Lifestyle Domain Holdings, Inc.
.hiphop	generic	Uniregistry, Corp.
.hisamitsu	generic	Hisamitsu Pharmaceutical Co.,Inc.
.hitachi	generic	Hitachi, Ltd.
.hiv	generic	Uniregistry, Corp.
.hk	country-code	Hong Kong Internet Registration Corporation Ltd.
.hkt	generic	PCCW-HKT DataCom Services Limited
.hm	country-code	HM Domain Registry
.hn	country-code	Red de Desarrollo Sostenible Honduras
.hockey	generic	Half Willow, LLC
.holdings	generic	John Madison, LLC
.holiday	generic	Goose Woods, LLC
.homedepot	generic	Homer TLC, Inc.
.homegoods	generic	The TJX Companies, Inc.
.homes	generic	DERHomes, LLC
.homesense	generic	The TJX Companies, Inc.
.honda	generic	Honda Motor Co., Ltd.
.honeywell	generic	Honeywell GTLD LLC
.horse	generic	Top Level Domain Holdings Limited
.hospital	generic	Ruby Pike, LLC
.host	generic	DotHost Inc.
.hosting	generic	Uniregistry, Corp.
.hot	generic	Amazon Registry Services, Inc.
.hoteles	generic	Travel Reservations SRL
.hotmail	generic	Microsoft Corporation
.house	generic	Sugar Park, LLC
.how	generic	Charleston Road Registry Inc.
.hr	country-code	CARNet - Croatian Academic and Research Network
.hsbc	generic	HSBC Holdings PLC
.ht	country-code	Consortium FDS/RDDH
.htc	generic	HTC corporation
.hu	country-code	Council of Hungarian Internet Providers (CHIP)
.hughes	generic	Hughes Satellite Systems Corporation
.hyatt	generic	Hyatt GTLD, L.L.C.
.hyundai	generic	Hyundai Motor Company
.ibm	generic	International Business Machines Corporation
.icbc	generic	Industrial and Commercial Bank of China Limited
.ice	generic	IntercontinentalExchange, Inc.
.icu	generic	One.com A/S
.id	country-code	Perkumpulan Pengelola Nama Domain Internet Indonesia (PANDI)
.ie	country-code	"University College Dublin Computing Services Computer Centre"
.ieee	generic	IEEE Global LLC
.ifm	generic	ifm electronic gmbh
.iinet	generic	Connect West Pty. Ltd.
.ikano	generic	Ikano S.A.
.il	country-code	Internet Society of Israel
.im	country-code	Isle of Man Government
.imamat	generic	Fondation Aga Khan (Aga Khan Foundation)
.imdb	generic	Amazon Registry Services, Inc.
.immo	generic	Auburn Bloom, LLC
.immobilien	generic	United TLD Holdco Ltd.
.in	country-code	National Internet Exchange of India
.industries	generic	Outer House, LLC
.infiniti	generic	NISSAN MOTOR CO., LTD.
.info	generic	Afilias Limited
.ing	generic	Charleston Road Registry Inc.
.ink	generic	Top Level Design, LLC
.institute	generic	Outer Maple, LLC
.insurance	generic	fTLD Registry Services LLC
.insure	generic	Pioneer Willow, LLC
.int	sponsored	Internet Assigned Numbers Authority
.intel	generic	Intel Corporation
.international	generic	Wild Way, LLC
.intuit	generic	Intuit Administrative Services, Inc.
.investments	generic	Holly Glen, LLC
.io	country-code	"IO Top Level Domain Registry Cable and Wireless"
.ipiranga	generic	Ipiranga Produtos de Petroleo S.A.
.iq	country-code	Communications and Media Commission (CMC)
.ir	country-code	Institute for Research in Fundamental Sciences
.irish	generic	Dot-Irish LLC
.is	country-code	ISNIC - Internet Iceland ltd.
.iselect	generic	iSelect Ltd
.ismaili	generic	Fondation Aga Khan (Aga Khan Foundation)
.ist	generic	Istanbul Metropolitan Municipality
.istanbul	generic	Istanbul Metropolitan Municipality
.it	country-code	IIT - CNR
.itau	generic	Itau Unibanco Holding S.A.
.itv	generic	ITV Services Limited
.iveco	generic	CNH Industrial N.V.
.iwc	generic	Richemont DNS Inc.
.jaguar	generic	Jaguar Land Rover Ltd
.java	generic	Oracle Corporation
.jcb	generic	JCB Co., Ltd.
.jcp	generic	JCP Media, Inc.
.je	country-code	Island Networks (Jersey) Ltd.
.jeep	generic	FCA US LLC.
.jetzt	generic	Wild Frostbite, LLC
.jewelry	generic	Wild Bloom, LLC
.jio	generic	Affinity Names, Inc.
.jlc	generic	Richemont DNS Inc.
.jll	generic	Jones Lang LaSalle Incorporated
.jm	country-code	University of West Indies
.jmp	generic	Matrix IP LLC
.jnj	generic	Johnson & Johnson Services, Inc.
.jo	country-code	National Information Technology Center (NITC)
.jobs	sponsored	Employ Media LLC
.joburg	generic	ZA Central Registry NPC trading as ZA Central Registry
.jot	generic	Amazon Registry Services, Inc.
.joy	generic	Amazon Registry Services, Inc.
.jp	country-code	Japan Registry Services Co., Ltd.
.jpmorgan	generic	JPMorgan Chase Bank, National Association
.jprs	generic	Japan Registry Services Co., Ltd.
.juegos	generic	Uniregistry, Corp.
.juniper	generic	JUNIPER NETWORKS, INC.
.kaufen	generic	United TLD Holdco Ltd.
.kddi	generic	KDDI CORPORATION
.ke	country-code	Kenya Network Information Center (KeNIC)
.kerryhotels	generic	Kerry Trading Co. Limited
.kerrylogistics	generic	Kerry Trading Co. Limited
.kerryproperties	generic	Kerry Trading Co. Limited
.kfh	generic	Kuwait Finance House
.kg	country-code	AsiaInfo Telecommunication Enterprise
.kh	country-code	Telecommunication Regulator of Cambodia (TRC)
.ki	country-code	Ministry of Communications, Transport, and Tourism Development
.kia	generic	KIA MOTORS CORPORATION
.kim	generic	Afilias plc
.kinder	generic	Ferrero Trading Lux S.A.
.kindle	generic	Amazon Registry Services, Inc.
.kitchen	generic	Just Goodbye, LLC
.kiwi	generic	DOT KIWI LIMITED
.km	country-code	Comores Telecom
.kn	country-code	Ministry of Finance, Sustainable Development Information & Technology
.koeln	generic	NetCologne Gesellschaft für Telekommunikation mbH
.komatsu	generic	Komatsu Ltd.
.kosher	generic	Kosher Marketing Assets LLC
.kp	country-code	Star Joint Venture Company
.kpmg	generic	KPMG International Cooperative (KPMG International Genossenschaft)
.kpn	generic	Koninklijke KPN N.V.
.kr	country-code	Korea Internet & Security Agency (KISA)
.krd	generic	KRG Department of Information Technology
.kred	generic	KredTLD Pty Ltd
.kuokgroup	generic	Kerry Trading Co. Limited
.kw	country-code	Ministry of Communications
.ky	country-code	The Information and Communications Technology Authority
.kyoto	generic	Academic Institution: Kyoto Jyoho Gakuen
.kz	country-code	Association of IT Companies of Kazakhstan
.la	country-code	Lao National Internet Committee (LANIC), Ministry of Posts and Telecommunications
.lacaixa	generic	CAIXA D'ESTALVIS I PENSIONS DE BARCELONA
.ladbrokes	generic	LADBROKES INTERNATIONAL PLC
.lamborghini	generic	Automobili Lamborghini S.p.A.
.lamer	generic	The Estée Lauder Companies Inc.
.lancaster	generic	LANCASTER
.lancia	generic	Fiat Chrysler Automobiles N.V.
.lancome	generic	L'Oréal
.land	generic	Pine Moon, LLC
.landrover	generic	Jaguar Land Rover Ltd
.lanxess	generic	LANXESS Corporation
.lasalle	generic	Jones Lang LaSalle Incorporated
.lat	generic	ECOM-LAC Federación de Latinoamérica y el Caribe para Internet y el Comercio Electrónico
.latino	generic	Dish DBS Corporation
.latrobe	generic	La Trobe University
.law	generic	Minds + Machines Group Limited
.lawyer	generic	United TLD Holdco, Ltd
.lb	country-code	"American University of Beirut Computing and Networking Services"
.lc	country-code	University of Puerto Rico
.lds	generic	IRI Domain Management, LLC
.lease	generic	Victor Trail, LLC
.leclerc	generic	A.C.D. LEC Association des Centres Distributeurs Edouard Leclerc
.lefrak	generic	LeFrak Organization, Inc.
.legal	generic	Blue Falls, LLC
.lego	generic	LEGO Juris A/S
.lexus	generic	TOYOTA MOTOR CORPORATION
.lgbt	generic	Afilias plc
.li	country-code	Universitaet Liechtenstein
.liaison	generic	Liaison Technologies, Incorporated
.lidl	generic	Schwarz Domains und Services GmbH & Co. KG
.life	generic	Trixy Oaks, LLC
.lifeinsurance	generic	American Council of Life Insurers
.lifestyle	generic	Lifestyle Domain Holdings, Inc.
.lighting	generic	John McCook, LLC
.like	generic	Amazon Registry Services, Inc.
.lilly	generic	Eli Lilly and Company
.limited	generic	Big Fest, LLC
.limo	generic	Hidden Frostbite, LLC
.lincoln	generic	Ford Motor Company
.linde	generic	Linde Aktiengesellschaft
.link	generic	Uniregistry, Corp.
.lipsy	generic	Lipsy Ltd
.live	generic	United TLD Holdco Ltd.
.living	generic	Lifestyle Domain Holdings, Inc.
.lixil	generic	LIXIL Group Corporation
.lk	country-code	"Council for Information Technology LK Domain Registrar"
.loan	generic	dot Loan Limited
.loans	generic	June Woods, LLC
.locker	generic	Dish DBS Corporation
.locus	generic	Locus Analytics LLC
.loft	generic	Annco, Inc.
.lol	generic	Uniregistry, Corp.
.london	generic	Dot London Domains Limited
.lotte	generic	Lotte Holdings Co., Ltd.
.lotto	generic	Afilias plc
.love	generic	Merchant Law Group LLP
.lpl	generic	LPL Holdings, Inc.
.lplfinancial	generic	LPL Holdings, Inc.
.lr	country-code	Data Technology Solutions, Inc.
.ls	country-code	National University of Lesotho
.lt	country-code	Kaunas University of Technology
.ltd	generic	Over Corner, LLC
.ltda	generic	InterNetX Corp.
.lu	country-code	RESTENA
.lundbeck	generic	H. Lundbeck A/S
.lupin	generic	LUPIN LIMITED
.luxe	generic	Top Level Domain Holdings Limited
.luxury	generic	Luxury Partners LLC
.lv	country-code	"University of Latvia Institute of Mathematics and Computer Science Department of Network Solutions (DNS)"
.ly	country-code	General Post and Telecommunication Company
.ma	country-code	Agence Nationale de Réglementation des Télécommunications (ANRT)
.macys	generic	Macys, Inc.
.madrid	generic	Comunidad de Madrid
.maif	generic	Mutuelle Assurance Instituteur France (MAIF)
.maison	generic	Victor Frostbite, LLC
.makeup	generic	L'Oréal
.man	generic	MAN SE
.management	generic	John Goodbye, LLC
.mango	generic	PUNTO FA S.L.
.market	generic	United TLD Holdco, Ltd
.marketing	generic	Fern Pass, LLC
.markets	generic	DOTMARKETS REGISTRY LTD
.marriott	generic	Marriott Worldwide Corporation
.marshalls	generic	The TJX Companies, Inc.
.maserati	generic	Fiat Chrysler Automobiles N.V.
.mattel	generic	Mattel Sites, Inc.
.mba	generic	Lone Hollow, LLC
.mc	country-code	"Gouvernement de Monaco Direction des Communications Electroniques"
.mcd	generic	McDonald’s Corporation
.mcdonalds	generic	McDonald’s Corporation
.mckinsey	generic	McKinsey Holdings, Inc.
.md	country-code	MoldData S.E.
.me	country-code	Government of Montenegro
.med	generic	Medistry LLC
.media	generic	Grand Glen, LLC
.meet	generic	Charleston Road Registry Inc.
.melbourne	generic	The Crown in right of the State of Victoria, represented by its Department of State Development, Business and Innovation
.meme	generic	Charleston Road Registry Inc.
.memorial	generic	Dog Beach, LLC
.men	generic	Exclusive Registry Limited
.menu	generic	Wedding TLD2, LLC
.meo	generic	MEO Serviços de Comunicações e Multimédia, S.A.
.metlife	generic	MetLife Services and Solutions, LLC
.mf	country-code	Not assigned
.mg	country-code	NIC-MG (Network Information Center Madagascar)
.mh	country-code	Office of the Cabinet
.miami	generic	Top Level Domain Holdings Limited
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
.mm	country-code	Ministry of Communications, Posts & Telegraphs
.mma	generic	MMA IARD
.mn	country-code	Datacom Co., Ltd.
.mo	country-code	Bureau of Telecommunications Regulation (DSRT)
.mobi	sponsored	Afilias Technologies Limited dba dotMobi
.mobily	generic	GreenTech Consultancy Company W.L.L.
.moda	generic	United TLD Holdco Ltd.
.moe	generic	Interlink Co., Ltd.
.moi	generic	Amazon Registry Services, Inc.
.mom	generic	Uniregistry, Corp.
.monash	generic	Monash University
.money	generic	Outer McCook, LLC
.monster	generic	Monster Worldwide, Inc.
.montblanc	generic	Richemont DNS Inc.
.mopar	generic	FCA US LLC.
.mormon	generic	IRI Domain Management, LLC ("Applicant")
.mortgage	generic	United TLD Holdco, Ltd
.moscow	generic	Foundation for Assistance for Internet Technologies and Infrastructure Development (FAITID)
.moto	generic	Motorola Trademark Holdings, LLC
.motorcycles	generic	DERMotorcycles, LLC
.mov	generic	Charleston Road Registry Inc.
.movie	generic	New Frostbite, LLC
.movistar	generic	Telefónica S.A.
.mp	country-code	Saipan Datacom, Inc.
.mq	country-code	MEDIASERV
.mr	country-code	Université des Sciences, de Technologie et de Médecine
.ms	country-code	MNI Networks Ltd.
.msd	generic	MSD Registry Holdings, Inc.
.mt	country-code	NIC (Malta)
.mtn	generic	MTN Dubai Limited
.mtpc	generic	Mitsubishi Tanabe Pharma Corporation
.mtr	generic	MTR Corporation Limited
.mu	country-code	Internet Direct Ltd
.museum	sponsored	Museum Domain Management Association
.mutual	generic	Northwestern Mutual MU TLD Registry, LLC
.mutuelle	generic	Fédération Nationale de la Mutualité Française
.mv	country-code	Dhiraagu Pvt. Ltd. (DHIVEHINET)
.mw	country-code	"Malawi Sustainable Development Network Programme (Malawi SDNP)"
.mx	country-code	"NIC-Mexico ITESM - Campus Monterrey"
.my	country-code	MYNIC Berhad
.mz	country-code	Centro de Informatica de Universidade Eduardo Mondlane
.na	country-code	Namibian Network Information Center
.nab	generic	National Australia Bank Limited
.nadex	generic	Nadex Domains, Inc
.nagoya	generic	GMO Registry, Inc.
.name	generic-restricted	VeriSign Information Services, Inc.
.nationwide	generic	Nationwide Mutual Insurance Company
.natura	generic	NATURA COSMÉTICOS S.A.
.navy	generic	United TLD Holdco Ltd.
.nba	generic	NBA REGISTRY, LLC
.nc	country-code	Office des Postes et Telecommunications
.ne	country-code	SONITEL
.nec	generic	NEC Corporation
.net	generic	VeriSign Global Registry Services
.netbank	generic	COMMONWEALTH BANK OF AUSTRALIA
.netflix	generic	Netflix, Inc.
.network	generic	Trixy Manor, LLC
.neustar	generic	NeuStar, Inc.
.new	generic	Charleston Road Registry Inc.
.newholland	generic	CNH Industrial N.V.
.news	generic	United TLD Holdco Ltd.
.next	generic	Next plc
.nextdirect	generic	Next plc
.nexus	generic	Charleston Road Registry Inc.
.nf	country-code	Norfolk Island Data Services
.nfl	generic	NFL Reg Ops LLC
.ng	country-code	Nigeria Internet Registration Association
.ngo	generic	Public Interest Registry
.nhk	generic	Japan Broadcasting Corporation (NHK)
.ni	country-code	"Universidad Nacional del Ingernieria Centro de Computo"
.nico	generic	DWANGO Co., Ltd.
.nike	generic	NIKE, Inc.
.nikon	generic	NIKON CORPORATION
.ninja	generic	United TLD Holdco Ltd.
.nissan	generic	NISSAN MOTOR CO., LTD.
.nissay	generic	Nippon Life Insurance Company
.nl	country-code	SIDN (Stichting Internet  Domeinregistratie Nederland)
.no	country-code	UNINETT Norid A/S
.nokia	generic	Nokia Corporation
.northwesternmutual	generic	Northwestern Mutual Registry, LLC
.norton	generic	Symantec Corporation
.now	generic	Amazon Registry Services, Inc.
.nowruz	generic	Asia Green IT System Bilgisayar San. ve Tic. Ltd. Sti.
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
.observer	generic	Top Level Spectrum, Inc.
.off	generic	Johnson Shareholdings, Inc.
.office	generic	Microsoft Corporation
.okinawa	generic	BRregistry, Inc.
.olayan	generic	Crescent Holding GmbH
.olayangroup	generic	Crescent Holding GmbH
.oldnavy	generic	The Gap, Inc.
.ollo	generic	Dish DBS Corporation
.om	country-code	Telecommunications Regulatory Authority (TRA)
.omega	generic	The Swatch Group Ltd
.one	generic	One.com A/S
.ong	generic	Public Interest Registry
.onl	generic	I-REGISTRY Ltd., Niederlassung Deutschland
.online	generic	DotOnline Inc.
.onyourside	generic	Nationwide Mutual Insurance Company
.ooo	generic	INFIBEAM INCORPORATION LIMITED
.open	generic	American Express Travel Related Services Company, Inc.
.oracle	generic	Oracle Corporation
.orange	generic	Orange Brand Services Limited
.org	generic	Public Interest Registry (PIR)
.organic	generic	Afilias plc
.orientexpress	generic	Orient Express
.origins	generic	The Estée Lauder Companies Inc.
.osaka	generic	Interlink Co., Ltd.
.otsuka	generic	Otsuka Holdings Co., Ltd.
.ott	generic	Dish DBS Corporation
.ovh	generic	OVH SAS
.pa	country-code	Universidad Tecnologica de Panama
.page	generic	Charleston Road Registry Inc.
.pamperedchef	generic	The Pampered Chef, Ltd.
.panasonic	generic	Panasonic Corporation
.panerai	generic	Richemont DNS Inc.
.paris	generic	City of Paris
.pars	generic	Asia Green IT System Bilgisayar San. ve Tic. Ltd. Sti.
.partners	generic	Magic Glen, LLC
.parts	generic	Sea Goodbye, LLC
.party	generic	Blue Sky Registry Limited
.passagens	generic	Travel Reservations SRL
.pay	generic	Amazon Registry Services, Inc.
.pccw	generic	PCCW Enterprises Limited
.pe	country-code	Red Cientifica Peruana
.pet	generic	Afilias plc
.pf	country-code	Gouvernement de la Polynésie française
.pfizer	generic	Pfizer Inc.
.pg	country-code	"PNG DNS Administration Vice Chancellors Office The Papua New Guinea University of Technology"
.ph	country-code	PH Domain Foundation
.pharmacy	generic	National Association of Boards of Pharmacy
.philips	generic	Koninklijke Philips N.V.
.photo	generic	Uniregistry, Corp.
.photography	generic	Sugar Glen, LLC
.photos	generic	Sea Corner, LLC
.physio	generic	PhysBiz Pty Ltd
.piaget	generic	Richemont DNS Inc.
.pics	generic	Uniregistry, Corp.
.pictet	generic	Pictet Europe S.A.
.pictures	generic	Foggy Sky, LLC
.pid	generic	Top Level Spectrum, Inc.
.pin	generic	Amazon Registry Services, Inc.
.ping	generic	Ping Registry Provider, Inc.
.pink	generic	Afilias plc
.pioneer	generic	Pioneer Corporation
.pizza	generic	Foggy Moon, LLC
.pk	country-code	PKNIC
.pl	country-code	Research and Academic Computer Network
.place	generic	Snow Galley, LLC
.play	generic	Charleston Road Registry Inc.
.playstation	generic	Sony Computer Entertainment Inc.
.plumbing	generic	Spring Tigers, LLC
.plus	generic	Sugar Mill, LLC
.pm	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.pn	country-code	Pitcairn Island Administration
.pnc	generic	PNC Domain Co., LLC
.pohl	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.poker	generic	Afilias plc
.politie	generic	Politie Nederland
.porn	generic	ICM Registry PN LLC
.post	sponsored	Universal Postal Union
.pr	country-code	Gauss Research Laboratory Inc.
.pramerica	generic	Prudential Financial, Inc.
.praxi	generic	Praxi S.p.A.
.press	generic	DotPress Inc.
.prime	generic	Amazon Registry Services, Inc.
.pro	generic-restricted	"Registry Services Corporation dba RegistryPro"
.prod	generic	Charleston Road Registry Inc.
.productions	generic	Magic Birch, LLC
.prof	generic	Charleston Road Registry Inc.
.progressive	generic	Progressive Casualty Insurance Company
.promo	generic	Afilias plc
.properties	generic	Big Pass, LLC
.property	generic	Uniregistry, Corp.
.protection	generic	XYZ.COM LLC
.pru	generic	Prudential Financial, Inc.
.prudential	generic	Prudential Financial, Inc.
.ps	country-code	"Ministry Of Telecommunications & Information Technology, Government Computer Center."
.pt	country-code	Associação DNS.PT
.pub	generic	United TLD Holdco Ltd.
.pw	country-code	Micronesia Investment and Development Corporation
.pwc	generic	PricewaterhouseCoopers LLP
.py	country-code	NIC-PY
.qa	country-code	Communications Regulatory Authority
.qpon	generic	dotCOOL, Inc.
.quebec	generic	PointQuébec Inc
.quest	generic	Quest ION Limited
.qvc	generic	QVC, Inc.
.racing	generic	Premier Registry Limited
.radio	generic	European Broadcasting Union (EBU)
.raid	generic	Johnson Shareholdings, Inc.
.re	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.read	generic	Amazon Registry Services, Inc.
.realestate	generic	dotRealEstate LLC
.realtor	generic	Real Estate Domains LLC
.realty	generic	Fegistry, LLC
.recipes	generic	Grand Island, LLC
.red	generic	Afilias plc
.redstone	generic	Redstone Haute Couture Co., Ltd.
.redumbrella	generic	Travelers TLD, LLC
.rehab	generic	United TLD Holdco Ltd.
.reise	generic	Foggy Way, LLC
.reisen	generic	New Cypress, LLC
.reit	generic	National Association of Real Estate Investment Trusts, Inc.
.reliance	generic	Reliance Industries Limited
.ren	generic	Beijing Qianxiang Wangjing Technology Development Co., Ltd.
.rent	generic	XYZ.COM LLC
.rentals	generic	Big Hollow,LLC
.repair	generic	Lone Sunset, LLC
.report	generic	Binky Glen, LLC
.republican	generic	United TLD Holdco Ltd.
.rest	generic	Punto 2012 Sociedad Anonima Promotora de Inversion de Capital Variable
.restaurant	generic	Snow Avenue, LLC
.review	generic	dot Review Limited
.reviews	generic	United TLD Holdco, Ltd.
.rexroth	generic	Robert Bosch GMBH
.rich	generic	I-REGISTRY Ltd., Niederlassung Deutschland
.richardli	generic	Pacific Century Asset Management (HK) Limited
.ricoh	generic	Ricoh Company, Ltd.
.rightathome	generic	Johnson Shareholdings, Inc.
.ril	generic	Reliance Industries Limited
.rio	generic	Empresa Municipal de Informática SA - IPLANRIO
.rip	generic	United TLD Holdco Ltd.
.rmit	generic	Royal Melbourne Institute of Technology
.ro	country-code	National Institute for R&D in Informatics
.rocher	generic	Ferrero Trading Lux S.A.
.rocks	generic	United TLD Holdco, LTD.
.rodeo	generic	Top Level Domain Holdings Limited
.rogers	generic	Rogers Communications Canada Inc.
.room	generic	Amazon Registry Services, Inc.
.rs	country-code	Serbian National Internet Domain Registry (RNIDS)
.rsvp	generic	Charleston Road Registry Inc.
.ru	country-code	Coordination Center for TLD RU
.ruhr	generic	regiodot GmbH & Co. KG
.run	generic	Snow Park, LLC
.rw	country-code	Rwanda Information Communication and Technology Association (RICTA)
.rwe	generic	RWE AG
.ryukyu	generic	BRregistry, Inc.
.sa	country-code	Communications and Information Technology Commission
.saarland	generic	dotSaarland GmbH
.safe	generic	Amazon Registry Services, Inc.
.safety	generic	Safety Registry Services, LLC.
.sakura	generic	SAKURA Internet Inc.
.sale	generic	United TLD Holdco, Ltd
.salon	generic	Outer Orchard, LLC
.samsclub	generic	Wal-Mart Stores, Inc.
.samsung	generic	SAMSUNG SDS CO., LTD
.sandvik	generic	Sandvik AB
.sandvikcoromant	generic	Sandvik AB
.sanofi	generic	Sanofi
.sap	generic	SAP AG
.sapo	generic	MEO Serviços de Comunicações e Multimédia, S.A.
.sarl	generic	Delta Orchard, LLC
.sas	generic	Research IP LLC
.save	generic	Amazon Registry Services, Inc.
.saxo	generic	Saxo Bank A/S
.sb	country-code	Solomon Telekom Company Limited
.sbi	generic	STATE BANK OF INDIA
.sbs	generic	SPECIAL BROADCASTING SERVICE CORPORATION
.sc	country-code	VCS Pty Ltd
.sca	generic	SVENSKA CELLULOSA AKTIEBOLAGET SCA (publ)
.scb	generic	The Siam Commercial Bank Public Company Limited ("SCB")
.schaeffler	generic	Schaeffler Technologies AG & Co. KG
.schmidt	generic	SALM S.A.S.
.scholarships	generic	Scholarships.com, LLC
.school	generic	Little Galley, LLC
.schule	generic	Outer Moon, LLC
.schwarz	generic	Schwarz Domains und Services GmbH & Co. KG
.science	generic	dot Science Limited
.scjohnson	generic	Johnson Shareholdings, Inc.
.scor	generic	SCOR SE
.scot	generic	Dot Scot Registry Limited
.sd	country-code	Sudan Internet Society
.se	country-code	The Internet Infrastructure Foundation
.seat	generic	SEAT, S.A. (Sociedad Unipersonal)
.secure	generic	Amazon Registry Services, Inc.
.security	generic	XYZ.COM LLC
.seek	generic	Seek Limited
.select	generic	iSelect Ltd
.sener	generic	Sener Ingeniería y Sistemas, S.A.
.services	generic	Fox Castle, LLC
.ses	generic	SES
.seven	generic	Seven West Media Ltd
.sew	generic	SEW-EURODRIVE GmbH & Co KG
.sex	generic	ICM Registry SX LLC
.sexy	generic	Uniregistry, Corp.
.sfr	generic	Societe Francaise du Radiotelephone - SFR
.sg	country-code	Singapore Network Information Centre (SGNIC) Pte Ltd
.sh	country-code	Government of St. Helena
.shangrila	generic	Shangri‐La International Hotel Management Limited
.sharp	generic	Sharp Corporation
.shaw	generic	Shaw Cablesystems G.P.
.shell	generic	Shell Information Technology International Inc
.shia	generic	Asia Green IT System Bilgisayar San. ve Tic. Ltd. Sti.
.shiksha	generic	Afilias plc
.shoes	generic	Binky Galley, LLC
.shop	generic	GMO Registry, Inc.
.shopping	generic	Over Keep, LLC
.shouji	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.show	generic	Snow Beach, LLC
.showtime	generic	CBS Domains Inc.
.shriram	generic	Shriram Capital Ltd.
.si	country-code	Academic and Research Network of Slovenia (ARNES)
.silk	generic	Amazon Registry Services, Inc.
.sina	generic	Sina Corporation
.singles	generic	Fern Madison, LLC
.site	generic	DotSite Inc.
.sj	country-code	UNINETT Norid A/S
.sk	country-code	SK-NIC, a.s.
.ski	generic	STARTING DOT LIMITED
.skin	generic	L'Oréal
.sky	generic	Sky International AG
.skype	generic	Microsoft Corporation
.sl	country-code	Sierratel
.sling	generic	Hughes Satellite Systems Corporation
.sm	country-code	Telecom Italia San Marino S.p.A.
.smart	generic	Smart Communications, Inc. (SMART)
.smile	generic	Amazon Registry Services, Inc.
.sn	country-code	"Universite Cheikh Anta Diop NIC Senegal"
.sncf	generic	SNCF (Société Nationale des Chemins de fer Francais)
.so	country-code	Ministry of Post and Telecommunications
.soccer	generic	Foggy Shadow, LLC
.social	generic	United TLD Holdco Ltd.
.softbank	generic	SoftBank Group Corp.
.software	generic	United TLD Holdco, Ltd
.sohu	generic	Sohu.com Limited
.solar	generic	Ruby Town, LLC
.solutions	generic	Silver Cover, LLC
.song	generic	Amazon Registry Services, Inc.
.sony	generic	Sony Corporation
.soy	generic	Charleston Road Registry Inc.
.space	generic	DotSpace Inc.
.spiegel	generic	SPIEGEL-Verlag Rudolf Augstein GmbH & Co. KG
.spot	generic	Amazon Registry Services, Inc.
.spreadbetting	generic	DOTSPREADBETTING REGISTRY LTD
.sr	country-code	Telesur
.srl	generic	InterNetX Corp.
.srt	generic	FCA US LLC.
.ss	country-code	Not assigned
.st	country-code	Tecnisys
.stada	generic	STADA Arzneimittel AG
.staples	generic	Staples, Inc.
.star	generic	Star India Private Limited
.starhub	generic	StarHub Limited
.statebank	generic	STATE BANK OF INDIA
.statefarm	generic	State Farm Mutual Automobile Insurance Company
.statoil	generic	Statoil ASA
.stc	generic	Saudi Telecom Company
.stcgroup	generic	Saudi Telecom Company
.stockholm	generic	Stockholms kommun
.storage	generic	Self Storage Company LLC
.store	generic	DotStore Inc.
.stream	generic	dot Stream Limited
.studio	generic	United TLD Holdco Ltd.
.study	generic	OPEN UNIVERSITIES AUSTRALIA PTY LTD
.style	generic	Binky Moon, LLC
.su	country-code	"Russian Institute for Development of Public Networks (ROSNIIROS)"
.sucks	generic	Vox Populi Registry Ltd.
.supplies	generic	Atomic Fields, LLC
.supply	generic	Half Falls, LLC
.support	generic	Grand Orchard, LLC
.surf	generic	Top Level Domain Holdings Limited
.surgery	generic	Tin Avenue, LLC
.suzuki	generic	SUZUKI MOTOR CORPORATION
.sv	country-code	SVNet
.swatch	generic	The Swatch Group Ltd
.swiftcover	generic	Swiftcover Insurance Services Limited
.swiss	generic	Swiss Confederation
.sx	country-code	SX Registry SA B.V.
.sy	country-code	National Agency for Network Services (NANS)
.sydney	generic	State of New South Wales, Department of Premier and Cabinet
.symantec	generic	Symantec Corporation
.systems	generic	Dash Cypress, LLC
.sz	country-code	"University of Swaziland Department of Computer Science"
.tab	generic	Tabcorp Holdings Limited
.taipei	generic	Taipei City Government
.talk	generic	Amazon Registry Services, Inc.
.taobao	generic	Alibaba Group Holding Limited
.target	generic	Target Domain Holdings, LLC
.tatamotors	generic	Tata Motors Ltd
.tatar	generic	Limited Liability Company "Coordination Center of Regional Domain of Tatarstan Republic"
.tattoo	generic	Uniregistry, Corp.
.tax	generic	Storm Orchard, LLC
.taxi	generic	Pine Falls, LLC
.tc	country-code	Melrex TC
.tci	generic	Asia Green IT System Bilgisayar San. ve Tic. Ltd. Sti.
.td	country-code	Société des télécommunications du Tchad (SOTEL TCHAD)
.tdk	generic	TDK Corporation
.team	generic	Atomic Lake, LLC
.tech	generic	Dot Tech LLC
.technology	generic	Auburn Falls, LLC
.tel	sponsored	Telnic Ltd.
.telecity	generic	TelecityGroup International Limited
.telefonica	generic	Telefónica S.A.
.temasek	generic	Temasek Holdings (Private) Limited
.tennis	generic	Cotton Bloom, LLC
.teva	generic	Teva Pharmaceutical Industries Limited
.tf	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.tg	country-code	Autorite de Reglementation des secteurs de Postes et de Telecommunications (ART&P)
.th	country-code	Thai Network Information Center Foundation
.thd	generic	Homer TLC, Inc.
.theater	generic	Blue Tigers, LLC
.theatre	generic	XYZ.COM LLC
.tiaa	generic	Teachers Insurance and Annuity Association of America
.tickets	generic	Accent Media Limited
.tienda	generic	Victor Manor, LLC
.tiffany	generic	Tiffany and Company
.tips	generic	Corn Willow, LLC
.tires	generic	Dog Edge, LLC
.tirol	generic	punkt Tirol GmbH
.tj	country-code	Information Technology Center
.tjmaxx	generic	The TJX Companies, Inc.
.tjx	generic	The TJX Companies, Inc.
.tk	country-code	Telecommunication Tokelau Corporation (Teletok)
.tkmaxx	generic	The TJX Companies, Inc.
.tl	country-code	Ministry of Transport and  Communications; National Division of  Information and Technology
.tm	country-code	TM Domain Registry Ltd
.tmall	generic	Alibaba Group Holding Limited
.tn	country-code	Agence Tunisienne d'Internet
.to	country-code	"Government of the Kingdom of Tonga H.R.H. Crown Prince Tupouto'a c/o Consulate of Tonga"
.today	generic	Pearl Woods, LLC
.tokyo	generic	GMO Registry, Inc.
.tools	generic	Pioneer North, LLC
.top	generic	Jiangsu Bangning Science & Technology Co.,Ltd.
.toray	generic	Toray Industries, Inc.
.toshiba	generic	TOSHIBA Corporation
.total	generic	Total SA
.tours	generic	Sugar Station, LLC
.town	generic	Koko Moon, LLC
.toyota	generic	TOYOTA MOTOR CORPORATION
.toys	generic	Pioneer Orchard, LLC
.tp	country-code	Retired
.tr	country-code	"Middle East Technical University Department of Computer Engineering"
.trade	generic	Elite Registry Limited
.trading	generic	DOTTRADING REGISTRY LTD
.training	generic	Wild Willow, LLC
.travel	sponsored	Tralliance Registry Management Company, LLC.
.travelchannel	generic	Lifestyle Domain Holdings, Inc.
.travelers	generic	Travelers TLD, LLC
.travelersinsurance	generic	Travelers TLD, LLC
.trust	generic	Artemis Internet Inc
.trv	generic	Travelers TLD, LLC
.tt	country-code	"University of the West Indies Faculty of Engineering"
.tube	generic	Latin American Telecom LLC
.tui	generic	TUI AG
.tunes	generic	Amazon Registry Services, Inc.
.tushu	generic	Amazon Registry Services, Inc.
.tv	country-code	Ministry of Finance and Tourism
.tvs	generic	T V SUNDRAM IYENGAR  & SONS PRIVATE LIMITED
.tw	country-code	Taiwan Network Information Center (TWNIC)
.tz	country-code	Tanzania Network Information Centre (tzNIC)
.ua	country-code	Hostmaster Ltd.
.ubank	generic	National Australia Bank Limited
.ubs	generic	UBS AG
.uconnect	generic	FCA US LLC.
.ug	country-code	Uganda Online Ltd.
.uk	country-code	Nominet UK
.um	country-code	Not assigned
.unicom	generic	China United Network Communications Corporation Limited
.university	generic	Little Station, LLC
.uno	generic	Dot Latin LLC
.uol	generic	UBN INTERNET LTDA.
.ups	generic	UPS Market Driver, Inc.
.us	country-code	NeuStar, Inc.
.uy	country-code	SeCIU - Universidad de la Republica
.uz	country-code	"Computerization and Information Technologies Developing Center UZINFOCOM"
.va	country-code	Holy See - Vatican City State
.vacations	generic	Atomic Tigers, LLC
.vana	generic	Lifestyle Domain Holdings, Inc.
.vanguard	generic	The Vanguard Group, Inc.
.vc	country-code	Ministry of Telecommunications, Science, Technology and Industry
.ve	country-code	Comisión Nacional de Telecomunicaciones (CONATEL)
.vegas	generic	Dot Vegas, Inc.
.ventures	generic	Binky Lake, LLC
.verisign	generic	VeriSign, Inc.
.versicherung	generic	dotversicherung-registry GmbH
.vet	generic	United TLD Holdco, Ltd
.vg	country-code	Telecommunications Regulatory Commission of the Virgin Islands
.vi	country-code	Virgin Islands Public Telecommunications System, Inc.
.viajes	generic	Black Madison, LLC
.video	generic	United TLD Holdco, Ltd
.vig	generic	VIENNA INSURANCE GROUP AG Wiener Versicherung Gruppe
.viking	generic	Viking River Cruises (Bermuda) Ltd.
.villas	generic	New Sky, LLC
.vin	generic	Holly Shadow, LLC
.vip	generic	Minds + Machines Group Limited
.virgin	generic	Virgin Enterprises Limited
.visa	generic	Visa Worldwide Pte. Limited
.vision	generic	Koko Station, LLC
.vista	generic	Vistaprint Limited
.vistaprint	generic	Vistaprint Limited
.viva	generic	Saudi Telecom Company
.vivo	generic	Telefonica Brasil S.A.
.vlaanderen	generic	DNS.be vzw
.vn	country-code	Ministry of Information and Communications of Socialist Republic of Viet Nam
.vodka	generic	Top Level Domain Holdings Limited
.volkswagen	generic	Volkswagen Group of America Inc.
.volvo	generic	Volvo Holding Sverige Aktiebolag
.vote	generic	Monolith Registry LLC
.voting	generic	Valuetainment Corp.
.voto	generic	Monolith Registry LLC
.voyage	generic	Ruby House, LLC
.vu	country-code	Telecom Vanuatu Limited
.vuelos	generic	Travel Reservations SRL
.wales	generic	Nominet UK
.walmart	generic	Wal-Mart Stores, Inc.
.walter	generic	Sandvik AB
.wang	generic	Zodiac Wang Limited
.wanggou	generic	Amazon Registry Services, Inc.
.warman	generic	Weir Group IP Limited
.watch	generic	Sand Shadow, LLC
.watches	generic	Richemont DNS Inc.
.weather	generic	International Business Machines Corporation
.weatherchannel	generic	International Business Machines Corporation
.webcam	generic	dot Webcam Limited
.weber	generic	Saint-Gobain Weber SA
.website	generic	DotWebsite Inc.
.wed	generic	Atgron, Inc.
.wedding	generic	Top Level Domain Holdings Limited
.weibo	generic	Sina Corporation
.weir	generic	Weir Group IP Limited
.wf	country-code	Association Française pour le Nommage Internet en Coopération (A.F.N.I.C.)
.whoswho	generic	Who's Who Registry
.wien	generic	punkt.wien GmbH
.wiki	generic	Top Level Design, LLC
.williamhill	generic	William Hill Organization Limited
.win	generic	First Registry Limited
.windows	generic	Microsoft Corporation
.wine	generic	June Station, LLC
.winners	generic	The TJX Companies, Inc.
.wme	generic	William Morris Endeavor Entertainment, LLC
.wolterskluwer	generic	Wolters Kluwer N.V.
.woodside	generic	Woodside Petroleum Limited
.work	generic	Top Level Domain Holdings Limited
.works	generic	Little Dynamite, LLC
.world	generic	Bitter Fields, LLC
.wow	generic	Amazon Registry Services, Inc.
.ws	country-code	Government of Samoa Ministry of Foreign Affairs & Trade
.wtc	generic	World Trade Centers Association, Inc.
.wtf	generic	Hidden Way, LLC
.xbox	generic	Microsoft Corporation
.xerox	generic	Xerox DNHC LLC
.xfinity	generic	Comcast IP Holdings I, LLC
.xihuan	generic	QIHOO 360 TECHNOLOGY CO. LTD.
.xin	generic	Elegant Leader Limited
.测试	test	Internet Assigned Numbers Authority
.कॉम	generic	VeriSign Sarl
.परीक्षा	test	Internet Assigned Numbers Authority
.セール	generic	Amazon Registry Services, Inc.
.佛山	generic	Guangzhou YU Wei Information Technology Co., Ltd.
.ಭಾರತ	country-code	Not assigned
.慈善	generic	Excellent First Limited
.集团	generic	Eagle Horizon Limited
.在线	generic	TLD REGISTRY LIMITED
.한국	country-code	KISA (Korea Internet & Security Agency)
.ଭାରତ	country-code	Not assigned
.大众汽车	generic	Volkswagen (China) Investment Co., Ltd.
.点看	generic	VeriSign Sarl
.คอม	generic	VeriSign Sarl
.ভাৰত	country-code	Not assigned
.ভারত	country-code	National Internet Exchange of India
.八卦	generic	Zodiac Gemini Ltd
‏.موقع‎	generic	Suhub Electronic Establishment
.বাংলা	country-code	Posts and Telecommunications Division
.公益	generic	China Organizational Name Administration Center
.公司	generic	Computer Network Information Center of Chinese Academy of Sciences （China Internet Network Information Center）
.香格里拉	generic	Shangri‐La International Hotel Management Limited
.网站	generic	Global Website TLD Asia Limited
.移动	generic	Afilias plc
.我爱你	generic	Tycoon Treasure Limited
.москва	generic	Foundation for Assistance for Internet Technologies and Infrastructure Development (FAITID)
.испытание	test	Internet Assigned Numbers Authority
.қаз	country-code	Association of IT Companies of Kazakhstan
.католик	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
.онлайн	generic	CORE Association
.сайт	generic	CORE Association
.联通	generic	China United Network Communications Corporation Limited
.срб	country-code	Serbian National Internet Domain Registry (RNIDS)
.бг	country-code	Imena.BG AD
.бел	country-code	Reliable Software, Ltd.
‏.קום‎	generic	VeriSign Sarl
.时尚	generic	RISE VICTORY LIMITED
.微博	generic	Sina Corporation
.테스트	test	Internet Assigned Numbers Authority
.淡马锡	generic	Temasek Holdings (Private) Limited
.ファッション	generic	Amazon Registry Services, Inc.
.орг	generic	Public Interest Registry
.नेट	generic	VeriSign Sarl
.ストア	generic	Amazon Registry Services, Inc.
.삼성	generic	SAMSUNG SDS CO., LTD
.சிங்கப்பூர்	country-code	Singapore Network Information Centre (SGNIC) Pte Ltd
.商标	generic	HU YI GLOBAL INFORMATION RESOURCES(HOLDING) COMPANY.HONGKONG LIMITED
.商店	generic	Wild Island, LLC
.商城	generic	Zodiac Aquarius Limited
.дети	generic	The Foundation for Network Initiatives “The Smart Internet”
.мкд	country-code	Macedonian Academic Research Network Skopje
‏.טעסט‎	test	Internet Assigned Numbers Authority
.ею	country-code	EURid vzw/asbl
.ポイント	generic	Amazon Registry Services, Inc.
.新闻	generic	Xinhua News Agency Guangdong Branch 新华通讯社广东分社
.工行	generic	Industrial and Commercial Bank of China Limited
.家電	generic	Amazon Registry Services, Inc.
‏.كوم‎	generic	VeriSign Sarl
.中文网	generic	TLD REGISTRY LIMITED
.中信	generic	CITIC Group Corporation
.中国	country-code	China Internet Network Information Center (CNNIC)
.中國	country-code	China Internet Network Information Center (CNNIC)
.娱乐	generic	Will Bloom, LLC
.谷歌	generic	Charleston Road Registry Inc.
.భారత్	country-code	National Internet Exchange of India
.ලංකා	country-code	LK Domain Registry
.電訊盈科	generic	PCCW Enterprises Limited
.购物	generic	Minds + Machines Group Limited
.測試	test	Internet Assigned Numbers Authority
.クラウド	generic	Amazon Registry Services, Inc.
.ભારત	country-code	National Internet Exchange of India
.通販	generic	Amazon Registry Services, Inc.
.भारतम्	country-code	Not assigned
.भारत	country-code	National Internet Exchange of India
.भारोत	country-code	Not assigned
‏.آزمایشی‎	test	Internet Assigned Numbers Authority
.பரிட்சை	test	Internet Assigned Numbers Authority
.网店	generic	Zodiac Taurus Ltd.
.संगठन	generic	Public Interest Registry
.餐厅	generic	HU YI GLOBAL INFORMATION RESOURCES (HOLDING) COMPANY. HONGKONG LIMITED
.网络	generic	Computer Network Information Center of Chinese Academy of Sciences （China Internet Network Information Center）
.ком	generic	VeriSign Sarl
.укр	country-code	Ukrainian Network Information Centre (UANIC), Inc.
.香港	country-code	Hong Kong Internet Registration Corporation Ltd.
.诺基亚	generic	Nokia Corporation
.食品	generic	Amazon Registry Services, Inc.
.δοκιμή	test	Internet Assigned Numbers Authority
.飞利浦	generic	Koninklijke Philips N.V.
‏.إختبار‎	test	Internet Assigned Numbers Authority
.台湾	country-code	Taiwan Network Information Center (TWNIC)
.台灣	country-code	Taiwan Network Information Center (TWNIC)
.手表	generic	Richemont DNS Inc.
.手机	generic	Beijing RITT-Net Technology Development Co., Ltd
.мон	country-code	Datacom Co.,Ltd
‏.الجزائر‎	country-code	CERIST
‏.عمان‎	country-code	Telecommunications Regulatory Authority (TRA)
‏.ارامكو‎	generic	Aramco Services Company
‏.ایران‎	country-code	Institute for Research in Fundamental Sciences (IPM)
‏.العليان‎	generic	Crescent Holding GmbH
‏.امارات‎	country-code	Telecommunications Regulatory Authority (TRA)
‏.بازار‎	generic	CORE Association
‏.پاکستان‎	country-code	Not assigned
‏.الاردن‎	country-code	National Information Technology Center (NITC)
‏.موبايلي‎	generic	GreenTech Consultancy Company W.L.L.
‏.بارت‎	country-code	Not assigned
‏.بھارت‎	country-code	National Internet Exchange of India
‏.المغرب‎	country-code	Agence Nationale de Réglementation des Télécommunications (ANRT)
‏.ابوظبي‎	generic	Abu Dhabi Systems and Information Centre
‏.السعودية‎	country-code	Communications and Information Technology Commission
‏.ڀارت‎	country-code	Not assigned
‏.كاثوليك‎	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
‏.سودان‎	country-code	Sudan Internet Society
‏.همراه‎	generic	Asia Green IT System Bilgisayar San. ve Tic. Ltd. Sti.
‏.عراق‎	country-code	Communications and Media Commission (CMC)
‏.مليسيا‎	country-code	MYNIC Berhad
.澳門	country-code	Bureau of Telecommunications Regulation (DSRT)
.닷컴	generic	VeriSign Sarl
.政府	generic	Net-Chinese Co., Ltd.
‏.شبكة‎	generic	International Domain Registry Pty. Ltd.
‏.بيتك‎	generic	Kuwait Finance House
.გე	country-code	Information Technologies Development Center (ITDC)
.机构	generic	Public Interest Registry
.组织机构	generic	Public Interest Registry
.健康	generic	Stable Tone Limited
.ไทย	country-code	Thai Network Information Center Foundation
‏.سورية‎	country-code	National Agency for Network Services (NANS)
.рус	generic	Rusnames Limited
.рф	country-code	Coordination Center for TLD RU
.珠宝	generic	Richemont DNS Inc.
‏.تونس‎	country-code	Agence Tunisienne d'Internet
.大拿	generic	VeriSign Sarl
.みんな	generic	Charleston Road Registry Inc.
.グーグル	generic	Charleston Road Registry Inc.
.ελ	country-code	ICS-FORTH GR
.世界	generic	Stable Tone Limited
.書籍	generic	Amazon Registry Services, Inc.
.ഭാരതം	country-code	Not assigned
.ਭਾਰਤ	country-code	National Internet Exchange of India
.网址	generic	KNET Co., Ltd
.닷넷	generic	VeriSign Sarl
.コム	generic	VeriSign Sarl
.天主教	generic	Pontificium Consilium de Comunicationibus Socialibus (PCCS) (Pontifical Council for Social Communication)
.游戏	generic	Spring Fields, LLC
.vermögensberater	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.vermögensberatung	generic	Deutsche Vermögensberatung Aktiengesellschaft DVAG
.企业	generic	Dash McCook, LLC
.信息	generic	Beijing Tele-info Network Technology Co., Ltd.
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
.テスト	test	Internet Assigned Numbers Authority
.政务	generic	China Organizational Name Administration Center
.xperia	generic	Sony Mobile Communications AB
.xxx	sponsored	ICM Registry LLC
.xyz	generic	XYZ.COM LLC
.yachts	generic	DERYachts, LLC
.yahoo	generic	Yahoo! Domain Services Inc.
.yamaxun	generic	Amazon Registry Services, Inc.
.yandex	generic	YANDEX, LLC
.ye	country-code	TeleYemen
.yodobashi	generic	YODOBASHI CAMERA CO.,LTD.
.yoga	generic	Top Level Domain Holdings Limited
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
.zippo	generic	Zadco Company
.zm	country-code	Zambia Information and Communications Technology Authority (ZICTA)
.zone	generic	Outer Falls, LLC
.zuerich	generic	Kanton Zürich (Canton of Zurich)
.zw	country-code	Postal and Telecommunications Regulatory Authority of Zimbabwe (POTRAZ)

__ICCTLD__
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Internationalized_country_code_top-level_domains
# https://www.icann.org/resources/pages/string-evaluation-completion-2014-02-19-en
# DNS name	IDN ccTLD	Country	Language	Script	Transliteration	Comments	Other ccTLD	DNSSEC
xn--ygbi2ammx	فلسطين.	State of Palestine	Arabic	Arabic (Arabic)	Filastīn		.ps	No
xn--yfro4i67o	.新加坡	Singapore	Chinese	Chinese (Simplified and Traditional)	Xīnjiāpō		.sg	No
xn--y9a3aq	.հայ	Armenia	Armenian	Armenian	hay		.am	Yes
xn--xkc2dl3a5ee0h	.இந்தியா	India	Tamil	Tamil	Intiyā	Became available 2015	.in	Yes
xn--xkc2al3hye2a	.இலங்கை	Sri Lanka	Tamil	Tamil	Ilaṅkai		.lk	Partial[21]
xn--wgbl6a	قطر.	Qatar	Arabic	Arabic (Arabic)	Qatar		.qa	No
xn--wgbh1c	مصر.	Egypt	Arabic	Arabic (Arabic)	Masr [39]		.eg	Yes
xn--s9brj9c	.ਭਾਰਤ	India	Punjabi	Gurmukhī	Bhārat	Not in use	.in	Yes
xn--qxam	.ελ[38]	Greece	Greek	Greek	el	Not in use	.gr	No
xn--pgbs0dh	تونس.	Tunisia	Arabic	Arabic (Arabic)	Tūnis		.tn	Yes
xn--p1ai	.рф	Russia	Russian	Cyrillic (Russian)	rf		.ru	Yes
xn--ogbpf8fl	سورية.	Syria	Arabic	Arabic (Arabic)	Sūryā		.sy	No
xn--o3cw4h	.ไทย	Thailand	Thai	Thai	Thai		.th	Yes
xn--node	.გე	Georgia	Georgian	Georgian (Mkhedruli)	GE		.ge	No
xn--mix891f	.澳門	Macao	Chinese	Chinese (Traditional)	Ou3 mun4 / Àomén	Not in use	.mo	No
xn--mix082f	.澳门	Macao	Chinese	Chinese (Simplified)	Ou3 mun4 / Àomén	Not in use	.mo	No
xn--mgbx4cd0ab	مليسيا.	Malaysia	Malay	Arabic (Jawi)	Malaysia		.my	Yes
xn--mgbtx2b	عراق.	Iraq	Arabic	Arabic (Arabic)	Iraq	Not in use	.iq	No
xn--mgbpl2fh	سودان.	Sudan	Arabic	Arabic (Arabic)	Sudan		.sd	No
xn--mgberp4a5d4ar	السعودية.	Saudi Arabia	Arabic	Arabic (Arabic)	as-Sa'ūdiyyah		.sa	No
xn--mgbc0a9azcg	المغرب.	Morocco	Arabic	Arabic (Arabic)	al Maghrib		.ma	No
xn--mgbbh1a71e	بھارت.	India	Urdu	Urdu	Bhārat	Not in use	.in	Yes
xn--mgbayh7gpa	الاردن.	Jordan	Arabic	Arabic (Arabic)	al 'Urdun		.jo	No
xn--mgbai9azgqp6j	پاکستان.	Pakistan	Urdu	Urdu	Pakistan	Not delegated	.pk	No
xn--mgbaam7a8h	امارات.	United Arab Emirates	Arabic	Arabic (Arabic)	Imārāt		.ae	No
xn--mgba3a4f16a	ایران.	Iran	Persian	Persian (Persian)	Īrān		.ir	No
xn--mgb9awbf	عمان.	Oman	Arabic	Arabic (Arabic)	Oman		.om	No
xn--mgb2ddes	اليمن.	Yemen	Arabic	Arabic (Arabic)	al Yemen	Not delegated	.ye	No
xn--lgbbat1ad8j	الجزائر.	Algeria	Arabic	Arabic (Arabic)	al Jaza'ir		.dz	No
xn--l1acc	.мон	Mongolia	Mongolian	Cyrillic (Mongolian)	mon		.mn	Yes
xn--kpry57d	.台灣	Taiwan	Chinese	Chinese (Traditional)	Táiwān		.tw	Yes
xn--kprw13d	.台湾	Taiwan	Chinese	Chinese (Simplified)	Táiwān		.tw	Yes
xn--j6w193g	.香港	Hong Kong	Chinese	Chinese (Simplified and Traditional)	Hoeng1 gong2		.hk	No
xn--j1amh	.укр	Ukraine	Ukrainian	Cyrillic (Ukrainian)	ukr		.ua	No
xn--h2brj9c	.भारत	India	Hindi	Devanagari	Bhārat	Became available 27 Aug 2014 [40]	.in	Yes
xn--gecrj9c	.ભારત	India	Gujarati	Gujarati	Bhārat	Not in use	.in	Yes
xn--fzc2c9e2c	.ලංකා	Sri Lanka	Sinhalese	Sinhalese	Lanka		.lk	Partial[21]
xn--fpcrj9c3d	.భారత్	India	Telugu	Telugu	Bhārata	Not in use	.in	Yes
xn--fiqz9s	.中國	China	Chinese	Chinese (Traditional)	Zhōngguó		.cn	Yes
xn--fiqs8s	.中国	China	Chinese	Chinese (Simplified)	Zhōngguó		.cn	Yes
xn--e1a4c	.ею	European Union	Bulgarian	Cyrillic	eyu		.eu	No
xn--d1alf	.мкд	Macedonia	Macedonian	Cyrillic (Macedonian)	mkd		.mk	No
xn--clchc0ea0b2g2a9gcd	.சிங்கப்பூர்	Singapore	Tamil	Tamil	Cinkappūr		.sg	No
xn--90ais	.бел	Belarus	Belarusian	Cyrillic	bel		.by	No
xn--90ae	.бг[38]	Bulgaria	Bulgarian	Cyrillic	bg		.bg	No
xn--90a3ac	.срб	Serbia	Serbian (Serbo-Croatian)	Cyrillic (Serbian)	srb		.rs	No
xn--80ao21a	.қаз	Kazakhstan	Kazakh	Cyrillic (Kazakh)	qaz		.kz	No
xn--54b7fta0cc	.বাংলা	Bangladesh	Bengali	Bengali	Bangla	Not delegated	.bd	No
xn--45brj9c	.ভারত	India	Bengali	Bengali	Bharôt	Not in use	.in	Yes
xn--3e0b707e	.한국	South Korea	Korean	Hangul	Han-guk		.kr	Yes
xn--2scrj9c	.ಭಾರತ	India	Kannada	Kannada	Bhārat	Not delegated	.in	
xn--rvc1e0am3e	.ഭാരതം	India	Malayalam	Malayalam	Bhārat	Not delegated	.in	
xn--45brj9c	.ভাৰত	India	Assamese	Bengali	Bharatam	Not delegated	.in	
xn--3hcrj9c	.ଭାରତ	India	Oriya	Oriya	Bhārat	Not delegated	.in	
__INTERNATIONALIZED_BRAND_TLD__
# Internationalized brand top-level domains
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Brand_top-level_domains
# DNS	IDN TLD	Entity	Script	Transliteration	Comments	DNSSEC
xn--fiq64b	.中信	CITIC Group	Chinese	zhōngxìn	[220]	Yes
xn--vermgensberater-ctb	.vermögensberater	Deutsche Vermögensberatung Aktiengesellschaft	Latin	[221]	Yes
xn--vermgensberatung-pwb	.vermögensberatung	Deutsche Vermögensberatung Aktiengesellschaft	Latin	[222]	Yes
xn--qcka1pmc	.グーグル	Google	Katakana	gūguru	[223]	Yes
xn--flw351e	.谷歌	Google	Chinese (Simplified)	gǔgē	[224]	Yes
xn--cg4bki	.삼성	Samsung	Hangul	samseong	[225]	Yes
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
