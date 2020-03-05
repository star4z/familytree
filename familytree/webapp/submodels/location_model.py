from django.db import models
from django.utils.translation import gettext_lazy as _

class Location(models.Model):
    city = models.CharField(verbose_name='City/Town/Village', max_length=50, 
        blank=True)

    state = models.CharField(verbose_name='State/Province/Region', 
        max_length=50, blank=True)

    class Country(models.TextChoices):
        # ISO 3166-1 standard for countries
        AFGHANISTAN = 'AF', _('Afghanistan')
        ALAND_ISLANDS = 'AX', _('Aland Islands')
        ALBANIA = 'AL', _('Albania')
        ALGERIA = 'DZ', _('Algeria')
        AMERICAN_SAMOA = 'AS', _('American Samoa')
        ANDORRA = 'AD', _('Andorra')
        ANGOLA = 'AO', _('Angola')
        ANTARCTICA = 'AQ', _('Antarctica')
        ANTIGUA_AND_BARBUDA = 'AG', _('Antigua and Barbuda')
        ARGENTINA = 'AR', _('Argentina')
        ARMENIA = 'AM', _('Armenia')
        ARUBA = 'AW', _('Aruba')
        AUSTRALIA = 'AU', _('Australia')
        AUSTRIA = 'AT', _('Austria')
        AZERBAIJAN = 'AZ', _('Azerbaijan')
        BAHAMAS = 'BS', _('Bahamas')
        BAHRAIN = 'BH', _('Bahrain')
        BANGLADESH = 'BD', _('Bangladesh')
        BARBADOS = 'BB', _('Barbados')
        BELARUS = 'BY', _('Belarus')
        BELGIUM = 'BE', _('Belgium')
        BELIZE = 'BZ', _('Belize')
        BENIN = 'BJ', _('Benin')
        BERMUDA = 'BM', _('Bermuda')
        BHUTAN = 'BT', _('Bhutan')
        BOLIVIA = 'BO', _('Bolivia')
        BOSNIA_AND_HERZEGOVINA = 'BA', _('Bosnia and Herzegovina')
        BOTSWANA = 'BW', _('Botswana')
        BOUVET_ISLAND = 'BV', _('Bouvet Island')
        BRAZIL = 'BR', _('Brazil')
        BRITISH_INDIAN_OCEAN_TERRITORY = 'IO', _('British Indian Ocean Territory')
        BRITISH_VIRGIN_ISLANDS = 'VG', _('British Virgin Islands')
        BRUNEI = 'BN', _('Brunei Darussalam')
        BULGARIA = 'BG', _('Bulgaria')
        BURKINA_FASO = 'BF', _('Burkina Faso')
        BURUNDI = 'BI', _('Burundi')
        CABO_VERDE = 'CV', _('Cabo Verde')
        CAMBODIA = 'KH', _('Cambodia')
        CAMEROON = 'CM', _('Cameroon')
        CANADA = 'CA', _('Canada')
        CARIBBEAN_NETHERLANDS = 'BQ', _('Caribbean Netherlands')
        CAYMAN_ISLANDS = 'KY', _('Cayman Islands')
        CENTRAL_AFRICAN_REPUBLIC = 'CF', _('Central African Republic')
        CHAD = 'TD', _('Chad')
        CHILE = 'CL', _('Chile')
        CHINA = 'CN', _('China')
        CHRISTMAS_ISLAND = 'CX', _('Christmas Island')
        COCOS_ISLANDS = 'CC', _('Cocos Islands')
        COLOMBIA = 'CO', _('Colombia')
        COMOROS = 'KM', _('Comoros')
        CONGO = 'CG', _('Congo')
        COOK_ISLANDS = 'CK', _('Cook Islands')
        COSTA_RICA = 'CR', _('Costa Rica')
        COTE_DLVOIRE = 'CI', _("Côte d'Ivoire")
        CROATIA = 'HR', _('Croatia')
        CUBA = 'CU', _('Cuba')
        CURACAO = 'CW', _('Curaçao')
        CYPRUS = 'CY', _('Cyprus')
        CZECHIA = 'CZ', _('Czechia')
        DEMOCRATIC_REPUBLIC_OF_THE_CONGO = 'CD', _('Democratic Republic of the Congo')
        DENMARK = 'DK', _('Denmark')
        DJIBOUTI = 'DJ', _('Djibouti')
        DOMINICA = 'DM', _('Dominica')
        DOMINICAN_REPUBLIC = 'DO', _('Dominican Republic')
        ECUADOR = 'EC', _('Ecuador')
        EGYPT = 'EG', _('Egypt')
        EL_SALVADOR = 'SV', _('El Salvador')
        EQUATORIAL_GUINEA = 'GQ', _('Equatorial Guinea')
        ERITREA = 'ER', _('Eritrea')
        ESTONIA = 'EE', _('Estonia')
        ESWATINI = 'SZ', _('Eswatini')
        ETHIOPIA = 'ET', _('Ethiopia')
        FALKLAND_ISLANDS = 'FK', _('Falkland Islands')
        FAROE_ISLANDS = 'FO', _('Faroe Islands')
        FIJI = 'FJ', _('Fiji')
        FINLAND = 'FI', _('Finland')
        FRANCE = 'FR', _('France')
        FRENCH_GUIANA = 'GF', _('French Guiana')
        FRENCH_POLYNESIA = 'PF', _('French Polynesia')
        FRENCH_SOUTHERN_TERRITORIES = 'TF', _('French Southern Territories')
        GABON = 'GA', _('Gabon')
        GAMBIA = 'GM', _('Gambia')
        GEORGIA = 'GE', _('Georgia')
        GERMANY = 'DE', _('Germany')
        GHANA = 'GH', _('Ghana')
        GIBRALTAR = 'GI', _('Gibraltar')
        GREECE = 'GR', _('Greece')
        GREENLAND = 'GL', _('Greenland')
        GRENADA = 'GD', _('Grenada')
        GUADELOUPE = 'GP', _('Guadeloupe')
        GUAM = 'GU', _('Guam')
        GUATEMALA = 'GT', _('Guatemala')
        GUERNSEY = 'GG', _('Guernsey')
        GUINEA = 'GN', _('Guinea')
        GUINEA_BISSAU = 'GW', _('Guinea-Bissau')
        GUYANA = 'GY', _('Guyana')
        HAITI = 'HT', _('Haiti')
        HEARD_ISLAND_AND_MCDONALD_ISLANDS = 'HM', _('Heard Island and McDonald Islands')
        HOLY_SEE = 'VA', _('Holy See')
        HONDURAS = 'HN', _('Honduras')
        HONG_KONG = 'HK', _('Hong Kong')
        HUNGARY = 'HU', _('Hungary')
        ICELAND = 'IS', _('Iceland')
        INDIA = 'IN', _('India')
        INDONESIA = 'ID', _('Indonesia')
        IRAN = 'IR', _('Iran')
        IRAQ = 'IQ', _('Iraq')
        IRELAND = 'IE', _('Ireland')
        ISLE_OF_MAN = 'IM', _('Isle of Man')
        ISRAEL = 'IL', _('Israel')
        ITALY = 'IT', _('Italy')
        JAMAICA = 'JM', _('Jamaica')
        JAPAN = 'JP', _('Japan')
        JERSEY = 'JE', _('Jersey')
        JORDAN = 'JO', _('Jordan')
        KAZAKHSTAN = 'KZ', _('Kazakhstan')
        KENYA = 'KE', _('Kenya')
        KIRIBATI = 'KI', _('Kiribati')
        KUWAIT = 'KW', _('Kuwait')
        KYRGYZSTAN = 'KG', _('Kyrgyzstan')
        LAOS = 'LA', _('Laos')
        LATVIA = 'LV', _('Latvia')
        LEBANON = 'LB', _('Lebanon')
        LESOTHO = 'LS', _('Lesotho')
        LIBERIA = 'LR', _('Liberia')
        LIBYA = 'LY', _('Libya')
        LIECHTENSTEIN = 'LI', _('Liechtenstein')
        LITHUANIA = 'LT', _('Lithuania')
        LUXEMBOURG = 'LU', _('Luxembourg')
        MACAO = 'MO', _('Macao')
        MADAGASCAR = 'MG', _('Madagascar')
        MALAWI = 'MW', _('Malawi')
        MALAYSIA = 'MY', _('Malaysia')
        MALDIVES = 'MV', _('Maldives')
        MALI = 'ML', _('Mali')
        MALTA = 'MT', _('Malta')
        MARSHALL_ISLANDS = 'MH', _('Marshall Islands')
        MARTINIQUE = 'MQ', _('Martinique')
        MAURITANIA = 'MR', _('Mauritania')
        MAURITIUS = 'MU', _('Mauritius')
        MAYOTTE = 'YT', _('Mayotte')
        MEXICO = 'MX', _('Mexico')
        MICRONESIA = 'FM', _('Micronesia')
        MOLDOVA = 'MD', _('Moldova')
        MONACO = 'MC', _('Monaco')
        MONGOLIA = 'MN', _('Mongolia')
        MONTENEGRO = 'ME', _('Montenegro')
        MONTSERRAT = 'MS', _('Montserrat')
        MOROCCO = 'MA', _('Morocco')
        MOZAMBIQUE = 'MZ', _('Mozambique')
        MYANMAR = 'MM', _('Myanmar')
        NAMIBIA = 'NA', _('Namibia')
        NAURU = 'NR', _('Nauru')
        NEPAL = 'NP', _('Nepal')
        NETHERLANDS = 'NL', _('Netherlands')
        NEW_CALEDONIA = 'NC', _('New Caledonia')
        NEW_ZEALAND = 'NZ', _('New Zealand')
        NICARAGUA = 'NI', _('Nicaragua')
        NIGER = 'NE', _('Niger')
        NIGERIA = 'NG', _('Nigeria')
        NIUE = 'NU', _('Niue')
        NORFOLK_ISLAND = 'NF', _('Norfolk Island')
        NORTH_KOREA = 'KP', _('North Korea')
        NORTH_MACEDONIA = 'MK', _('North Macedonia')
        NORTH_MARIANA_ISLANDS = 'MP', _('Northern Mariana Islands')
        NORWAY = 'NO', _('Norway')
        OMAN = 'OM', _('Oman')
        PAKISTAN = 'PK', _('Pakistan')
        PALAU = 'PW', _('Palau')
        PALESTINE = 'PS', _('Palestine')
        PANAMA = 'PA', _('Panama')
        PAPUA_NEW_GUINEA = 'PG', _('Papua New Guinea')
        PARAGUAY = 'PY', _('Paraguay')
        PERU = 'PE', _('Peru')
        PHILIPPINES = 'PH', _('Philippines')
        PITCAIRN = 'PN', _('Pitcairn')
        POLAND = 'PL', _('Poland')
        PORTUGAL = 'PT', _('Portugal')
        PUERTO_RICO = 'PR', _('Puerto Rico')
        QATAR = 'QA', _('Qatar')
        REUNION = 'RE', _('Reunion')
        ROMANIA = 'RO', _('Romania')
        RUSSIA = 'RU', _('Russian Federation')
        RWANDA = 'RW', _('Rwanda')
        SAINT_BARTHELEMY = 'BL', _('Saint Barthelemy')
        SAINT_HELENA_ASCENSION_AND_TRISTAN_DA_CUNHA = 'SH', _('Saint Helena, Ascension and Tristan da Cunha')
        SAINT_KITTS_AND_NEVIS = 'KN', _('Saint Kitts and Nevis')
        SAINT_LUCIA = 'LC', _('Saint Lucia')
        SAINT_MARTIN = 'MF', _('Saint Martin')
        SAINT_PIERRE_AND_MIQUELON = 'PM', _('Saint Pierre and Miquelon')
        SAINT_VINCENT_AND_THE_GRENADINES = 'VC', _('Saint Vincent and the Grenadines')
        SAMOA = 'WS', _('Samoa')
        SAN_MARINO = 'SM', _('San Marino')
        SAO_TOME_AND_PRINCIPE = 'ST', _('Sao Tome and Principe')
        SAUDI_ARABIA = 'SA', _('Saudi Arabia')
        SENEGAL = 'SN', _('Senegal')
        SERBIA = 'RS', _('Serbia')
        SEYCHELLES = 'SC', _('Seychelles')
        SIERRA_LEONE = 'SL', _('Sierra Leone')
        SINGAPORE = 'SG', _('Singapore')
        SINT_MAARTEN = 'SX', _('Sint Maarten')
        SLOVAKIA = 'SK', _('Slovakia')
        SLOVENIA = 'SI', _('Slovenia')
        SOLOMON_ISLANDS = 'SB', _('Solomon Islands')
        SOMALIA = 'SO', _('Somalia')
        SOUTH_AFRICA = 'ZA', _('South Africa')
        SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = 'GS', _('South Georgia and the South Sandwich Islands')
        SOUTH_KOREA = 'KR', _('South Korea')
        SOUTH_SUDAN = 'SS', _('South Sudan')
        SPAIN = 'ES', _('Spain')
        SRI_LANKA = 'LK', _('Sri Lanka')
        SUDAN = 'SD', _('Sudan')
        SURINAME = 'SR', _('Suriname')
        SVALBARD_AND_JAN_MAYEN = 'SJ', _('Svalbard and Jan Mayen')
        SWEDEN = 'SE', _('Sweden')
        SWITZERLAND = 'CH', _('Switzerland')
        SYRIA = 'SY', _('Syria')
        TAIWAN = 'TW', _('Taiwan')
        TAJIKISTAN = 'TJ', _('Tajikistan')
        TANZANIA = 'TZ', _('Tanzania')
        THALIAND = 'TH', _('Thailand')
        TIMOR_LESTE = 'TL', _('Timor-Leste')
        TOGO = 'TG', _('Togo')
        TOKELAU = 'TK', _('Tokelau')
        TONGA = 'TO', _('Tonga')
        TRINIDAD_AND_TOBAGO = 'TT', _('Trinidad and Tobago')
        TUNISIA = 'TN', _('Tunisia')
        TURKEY = 'TR', _('Turkey')
        TURKMENISTAN = 'TM', _('Turkmenistan')
        TURKS_AND_CAICOS_ISLANDS = 'TC', _('Turks and Caicos Islands')
        TUVALU = 'TV', _('Tuvalu')
        UGANDA = 'UG', _('Uganda')
        UKRAINE = 'UA', _('Ukraine')
        UNITED_ARAB_EMIRATES = 'AE', _('United Arab Emirates')
        UNITED_KINGDOM = 'GB', _('United Kingdom')
        UNITED_STATES = 'US', _('United States')
        UNITED_STATES_VIRGIN_ISLANDS = 'VI', _('United States Virgin Islands')
        URUGUAY = 'UY', _('Uruguay')
        UZBEKISTAN = 'UZ', _('Uzebekistan')
        VANUATU = 'VU', _('Vanuatu')
        VENEZUELA = 'VE', _('Venezuela')
        VIETNAM = 'VN', _('Vietnam')
        WALLIS_AND_FUTUNA = 'WF', _('Wallis and Futuna')
        WESTERN_SAHARA = 'EH', _('Western Sahara')
        YEMEN = 'YE', _('Yemen')
        ZAMBIA = 'ZM', _('Zambia')
        ZIMBABWE = 'ZW', _('Zimbabwe')
        
    country = models.CharField(max_length=2, choices=Country.choices, 
        blank=True)

    '''
    class Meta:
        unique_together = ["city", "state", "country"]
    '''

    def __str__(self):
        return self.city + ', ' + self.state + ', ' + self.country