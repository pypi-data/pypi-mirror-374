from typing import Dict
import astropy.units as u
from . import instruments

TELESCOPE_CONFIGS: Dict[str, dict] = {
    'AAO': {
        'name': 'aao',
        'location': 'aao',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'ALLEN_TELESCOPE_ARRAY': {
        'name': 'Allen Telescope Array',
        'location': 'Allen Telescope Array',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRI website https://archive.sri.com/research-development/specialized-facilities/hat-creek-radio-observatory',
    },
    'ALMA': {
        'name': 'alma',
        'location': 'alma',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://almascience.eso.org/about-alma/alma-site',
    },
    'ANDERSON_MESA': {
        'name': 'Anderson Mesa',
        'location': 'Anderson Mesa',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'ANGLO_AUSTRALIAN_OBSERVATORY': {
        'name': 'Anglo-Australian Observatory',
        'location': 'Anglo-Australian Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'AO': {
        'name': 'ao',
        'location': 'ao',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Arecibo_Observatory',
    },
    'APACHE_POINT': {
        'name': 'Apache Point',
        'location': 'Apache Point',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'APACHE_POINT_OBSERVATORY': {
        'name': 'Apache Point Observatory',
        'location': 'Apache Point Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'APO': {
        'name': 'apo',
        'location': 'apo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'ARCA': {
        'name': 'arca',
        'location': 'arca',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'ARECIBO': {
        'name': 'arecibo',
        'location': 'arecibo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Arecibo_Observatory',
    },
    'ARECIBO_OBSERVATORY': {
        'name': 'Arecibo Observatory',
        'location': 'Arecibo Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Arecibo_Observatory',
    },
    'ASKAP': {
        'name': 'askap',
        'location': 'askap',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'ASKAP Science Observation Guide, Version 1.1 https://confluence.csiro.au/display/askapsst/?preview=/733676544/887260100/ASKAP_sci_obs_guide.pdf',
    },
    'ASTROPARTICLE_RESEARCH_WITH_COSMICS_IN_THE_ABYSS': {
        'name': 'Astroparticle Research with Cosmics in the Abyss',
        'location': 'Astroparticle Research with Cosmics in the Abyss',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'ATA': {
        'name': 'ATA',
        'location': 'ATA',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRI website https://archive.sri.com/research-development/specialized-facilities/hat-creek-radio-observatory',
    },
    'ATACAMA_LARGE_MILLIMETER_ARRAY': {
        'name': 'Atacama Large Millimeter Array',
        'location': 'Atacama Large Millimeter Array',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://almascience.eso.org/about-alma/alma-site',
    },
    'ATST': {
        'name': 'ATST',
        'location': 'ATST',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'DKIST website: https://www.nso.edu/telescopes/dki-solar-telescope/',
    },
    'AUSTRALIAN_SQUARE_KILOMETRE_ARRAY_PATHFINDER': {
        'name': 'Australian Square Kilometre Array Pathfinder',
        'location': 'Australian Square Kilometre Array Pathfinder',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'ASKAP Science Observation Guide, Version 1.1 https://confluence.csiro.au/display/askapsst/?preview=/733676544/887260100/ASKAP_sci_obs_guide.pdf',
    },
    'BAO': {
        'name': 'BAO',
        'location': 'BAO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'BBSO': {
        'name': 'bbso',
        'location': 'bbso',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'BBSO website: http://www.bbso.njit.edu/newinfo.html',
    },
    'BEIJING_XINGLONG_OBSERVATORY': {
        'name': 'Beijing XingLong Observatory',
        'location': 'Beijing XingLong Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'BIG_BEAR_SOLAR_OBSERVATORY': {
        'name': 'Big Bear Solar Observatory',
        'location': 'Big Bear Solar Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'BBSO website: http://www.bbso.njit.edu/newinfo.html',
    },
    'BLACK_MOSHANNON_OBSERVATORY': {
        'name': 'Black Moshannon Observatory',
        'location': 'Black Moshannon Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'BMO': {
        'name': 'bmo',
        'location': 'bmo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CAHA': {
        'name': 'CAHA',
        'location': 'CAHA',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CAHA Wikipedia page (https://en.wikipedia.org/wiki/Calar_Alto_Observatory)',
    },
    'CANADA_FRANCE_HAWAII_TELESCOPE': {
        'name': 'Canada-France-Hawaii Telescope',
        'location': 'Canada-France-Hawaii Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CANADIAN_HYDROGEN_INTENSITY_MAPPING_EXPERIMENT': {
        'name': 'Canadian Hydrogen Intensity Mapping Experiment',
        'location': 'Canadian Hydrogen Intensity Mapping Experiment',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Journey to the center of CHIME, Calvin Leung, CHIME memo. Also, 2018 ApJ...863...48C.',
    },
    'CATALINA_OBSERVATORY': {
        'name': 'Catalina Observatory',
        'location': 'Catalina Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CATALINA_OBSERVATORY:_61_INCH_TELESCOPE': {
        'name': 'Catalina Observatory: 61 inch telescope',
        'location': 'Catalina Observatory: 61 inch telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CENTRO_ASTRONOMICO_HISPANO_ALEMAN,_ALMERIA': {
        'name': 'Centro Astronomico Hispano-Aleman, Almeria',
        'location': 'Centro Astronomico Hispano-Aleman, Almeria',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CAHA Wikipedia page (https://en.wikipedia.org/wiki/Calar_Alto_Observatory)',
    },
    'CERRO_ARMAZONES_OBSERVATORY': {
        'name': 'Cerro Armazones Observatory',
        'location': 'Cerro Armazones Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://araucaria.camk.edu.pl/index.php/observatory-cerro-armazones/',
    },
    'CERRO_PACHON': {
        'name': 'Cerro Pachon',
        'location': 'Cerro Pachon',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CTIO Website',
    },
    'CERRO_PARANAL': {
        'name': 'Cerro Paranal',
        'location': 'Cerro Paranal',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Official reference in VLTI raw data products',
    },
    'CERRO_TOLOLO': {
        'name': 'Cerro Tololo',
        'location': 'Cerro Tololo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CERRO_TOLOLO_INTERAMERICAN_OBSERVATORY': {
        'name': 'Cerro Tololo Interamerican Observatory',
        'location': 'Cerro Tololo Interamerican Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CFHT': {
        'name': 'cfht',
        'location': 'cfht',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CHARA': {
        'name': 'CHARA',
        'location': 'CHARA',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CHARA website',
    },
    'CHIME': {
        'name': 'chime',
        'location': 'chime',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Journey to the center of CHIME, Calvin Leung, CHIME memo. Also, 2018 ApJ...863...48C.',
    },
    'CIMA_EKAR_182_CM_TELESCOPE': {
        'name': 'Cima Ekar 182 cm Telescope',
        'location': 'Cima Ekar 182 cm Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CIMA_EKAR_OBSERVING_STATION': {
        'name': 'Cima Ekar Observing Station',
        'location': 'Cima Ekar Observing Station',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'CTIO': {
        'name': 'ctio',
        'location': 'ctio',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'DANIEL_K._INOUYE_SOLAR_TELESCOPE': {
        'name': 'Daniel K. Inouye Solar Telescope',
        'location': 'Daniel K. Inouye Solar Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'DKIST website: https://www.nso.edu/telescopes/dki-solar-telescope/',
    },
    'DAO': {
        'name': 'dao',
        'location': 'dao',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'DCT': {
        'name': 'dct',
        'location': 'dct',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Site GPS on 20130708 UT as recorded in observatory wiki',
    },
    'DISCOVERY_CHANNEL_TELESCOPE': {
        'name': 'Discovery Channel Telescope',
        'location': 'Discovery Channel Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Site GPS on 20130708 UT as recorded in observatory wiki',
    },
    'DKIST': {
        'name': 'dkist',
        'location': 'dkist',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'DKIST website: https://www.nso.edu/telescopes/dki-solar-telescope/',
    },
    'DOMINION_ASTROPHYSICAL_OBSERVATORY': {
        'name': 'Dominion Astrophysical Observatory',
        'location': 'Dominion Astrophysical Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'DOMINION_RADIO_ASTROPHYSICAL_OBSERVATORY': {
        'name': 'Dominion Radio Astrophysical Observatory',
        'location': 'Dominion Radio Astrophysical Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Geometry of the Penticton 25.6 m, John Galt, DRAO memo',
    },
    'DRAO': {
        'name': 'drao',
        'location': 'drao',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Geometry of the Penticton 25.6 m, John Galt, DRAO memo',
    },
    'DRAO_26M_TELESCOPE': {
        'name': 'DRAO 26m Telescope',
        'location': 'DRAO 26m Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Geometry of the Penticton 25.6 m, John Galt, DRAO memo',
    },
    'EFFELSBERG': {
        'name': 'effelsberg',
        'location': 'effelsberg',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Effelsberg radio telescope. These are the coordinates used for VLBI as of March 2020 (MJD 58919). They are based on
        a fiducial position at MJD 56658 plus a(continental) drift velocity of
        [-0.0144, 0.0167, 0.0106] m/yr. This data was obtained from Ben Perera in September 2021.
        via PINT''',
    },
    'EFFELSBERG_100_M_RADIO_TELESCOPE': {
        'name': 'Effelsberg 100-m Radio Telescope',
        'location': 'Effelsberg 100-m Radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Effelsberg radio telescope.

        These are the coordinates used for VLBI as of March 2020 (MJD 58919). They are based on
        a fiducial position at MJD 56658 plus a(continental) drift velocity of
        [-0.0144, 0.0167, 0.0106] m/yr. This data was obtained from Ben Perera in September 2021.
        via PINT''',
    },
    'EKAR': {
        'name': 'ekar',
        'location': 'ekar',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'EXAMPLE_SITE': {
        'name': 'example_site',
        'location': 'example_site',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Ordnance Survey via http://gpsinformation.net/main/greenwich.htm and UNESCO',
    },
    'FAST': {
        'name': 'fast',
        'location': 'fast',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The FAST radio telescope in China.

        Origin of this data is unknown but as of 2021 June 8 it agrees exactly with the
        TEMPO value and disagrees by about 17 km with the TEMPO2 value.
        via PINT''',
    },
    'FIVE_HUNDRED_METER_APERTURE_SPHERICAL_RADIO_TELESCOPE': {
        'name': 'Five-hundred-meter Aperture Spherical radio Telescope',
        'location': 'Five-hundred-meter Aperture Spherical radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The FAST radio telescope in China.

        Origin of this data is unknown but as of 2021 June 8 it agrees exactly with the
        TEMPO value and disagrees by about 17 km with the TEMPO2 value.
        via PINT''',
    },
    'FLWO': {
        'name': 'flwo',
        'location': 'flwo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'G1': {
        'name': 'G1',
        'location': 'G1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'GBT': {
        'name': 'gbt',
        'location': 'gbt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Green_Bank_Telescope + Google Elevation service for elevation',
    },
    'GEMINI_NORTH': {
        'name': 'gemini_north',
        'location': 'gemini_north',
        'instruments': [],  # TODO: Add instruments
        'diameter': 8.1 * u.m,
        'operational': True,
        'source': 'CTIO Website',
    },
    'GEMINI_SOUTH': {
        'name': 'gemini_south',
        'location': 'gemini_south',
        'instruments': [],  # TODO: Add instruments
        'diameter': 8.1 * u.m,
        'operational': True,
        'source': 'CTIO Website',
    },
    'GEMN': {
        'name': 'gemn',
        'location': 'gemn',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CTIO Website',
    },
    'GEMS': {
        'name': 'gems',
        'location': 'gems',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CTIO Website',
    },
    'GEO': {
        'name': 'GEO',
        'location': 'GEO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'GEO600_GRAVITATIONAL_WAVE_DETECTOR': {
        'name': 'GEO600 Gravitational Wave Detector',
        'location': 'GEO600 Gravitational Wave Detector',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'GEO_600': {
        'name': 'geo_600',
        'location': 'geo_600',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'GIANT_METREWAVE_RADIO_TELESCOPE': {
        'name': 'Giant Metrewave Radio Telescope',
        'location': 'Giant Metrewave Radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Giant Metrewave Radio Telescope.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'GMRT': {
        'name': 'gmrt',
        'location': 'gmrt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Giant Metrewave Radio Telescope.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'GREENWICH': {
        'name': 'greenwich',
        'location': 'greenwich',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Ordnance Survey via http://gpsinformation.net/main/greenwich.htm and UNESCO',
    },
    'GREEN_BANK_OBSERVATORY': {
        'name': 'Green Bank Observatory',
        'location': 'Green Bank Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Green_Bank_Telescope + Google Elevation service for elevation',
    },
    'GREEN_BANK_TELESCOPE': {
        'name': 'Green Bank Telescope',
        'location': 'Green Bank Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Green_Bank_Telescope + Google Elevation service for elevation',
    },
    'H1': {
        'name': 'H1',
        'location': 'H1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'HALEAKALA': {
        'name': 'haleakala',
        'location': 'haleakala',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Ifa/University of Hawaii website',
    },
    'HALEAKALA_OBSERVATORIES': {
        'name': 'Haleakala Observatories',
        'location': 'Haleakala Observatories',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Ifa/University of Hawaii website',
    },
    'HALE_TELESCOPE': {
        'name': 'Hale Telescope',
        'location': 'Hale Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'HALO': {
        'name': 'halo',
        'location': 'halo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'HAPPY_JACK': {
        'name': 'Happy Jack',
        'location': 'Happy Jack',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Site GPS on 20130708 UT as recorded in observatory wiki',
    },
    'HAT_CREEK': {
        'name': 'Hat Creek',
        'location': 'Hat Creek',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRI website https://archive.sri.com/research-development/specialized-facilities/hat-creek-radio-observatory',
    },
    'HAT_CREEK_RADIO_OBSERVATORY': {
        'name': 'Hat Creek Radio Observatory',
        'location': 'Hat Creek Radio Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRI website https://archive.sri.com/research-development/specialized-facilities/hat-creek-radio-observatory',
    },
    'HCRO': {
        'name': 'hcro',
        'location': 'hcro',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRI website https://archive.sri.com/research-development/specialized-facilities/hat-creek-radio-observatory',
    },
    'HELIUM_AND_LEAD_OBSERVATORY': {
        'name': 'Helium And Lead Observatory',
        'location': 'Helium And Lead Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'HET': {
        'name': 'het',
        'location': 'het',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Wikipedia',
    },
    'HOBBY_EBERLY_TELESCOPE': {
        'name': 'Hobby Eberly Telescope',
        'location': 'Hobby Eberly Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Wikipedia',
    },
    'HYPERK': {
        'name': 'hyperk',
        'location': 'hyperk',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Design Report, arXiv:1805.04163v2',
    },
    'HYPER_KAMIOKANDE': {
        'name': 'Hyper-Kamiokande',
        'location': 'Hyper-Kamiokande',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Design Report, arXiv:1805.04163v2',
    },
    'IAO': {
        'name': 'iao',
        'location': 'iao',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.iiap.res.in/centers/iao?q=iao_site',
    },
    'ICECUBE': {
        'name': 'icecube',
        'location': 'icecube',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'ICECUBE_NEUTRINO_OBSERVATORY': {
        'name': 'IceCube Neutrino Observatory',
        'location': 'IceCube Neutrino Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'INDIAN_ASTRONOMICAL_OBSERVATORY': {
        'name': 'Indian Astronomical Observatory',
        'location': 'Indian Astronomical Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.iiap.res.in/centers/iao?q=iao_site',
    },
    'IRTF': {
        'name': 'irtf',
        'location': 'irtf',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRTF Website',
    },
    'JAMES_CLERK_MAXWELL_TELESCOPE': {
        'name': 'James Clerk Maxwell Telescope',
        'location': 'James Clerk Maxwell Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '2007-04-11 GPS measurements by R. Tilanus (via Starlink/PAL)',
    },
    'JANSKY_VERY_LARGE_ARRAY': {
        'name': 'Jansky Very Large Array',
        'location': 'Jansky Very Large Array',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Very_Large_Array',
    },
    'JCMT': {
        'name': 'jcmt',
        'location': 'jcmt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '2007-04-11 GPS measurements by R. Tilanus (via Starlink/PAL)',
    },
    'JOHN_GALT_TELESCOPE': {
        'name': 'John Galt Telescope',
        'location': 'John Galt Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Geometry of the Penticton 25.6 m, John Galt, DRAO memo',
    },
    'K1': {
        'name': 'K1',
        'location': 'K1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'KAGRA': {
        'name': 'kagra',
        'location': 'kagra',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'KAMIOKA_GRAVITATIONAL_WAVE_DETECTOR': {
        'name': 'Kamioka Gravitational Wave Detector',
        'location': 'Kamioka Gravitational Wave Detector',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'KECK': {
        'name': 'keck',
        'location': 'keck',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'KECK_OBSERVATORY': {
        'name': 'Keck Observatory',
        'location': 'Keck Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 10.0 * u.m,
        'operational': True,
        'source': 'IRAF Observatory Database',
    },
    'KITT_PEAK': {
        'name': 'Kitt Peak',
        'location': 'Kitt Peak',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'KITT_PEAK_NATIONAL_OBSERVATORY': {
        'name': 'Kitt Peak National Observatory',
        'location': 'Kitt Peak National Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'KM3NET_ARCA': {
        'name': 'km3net arca',
        'location': 'km3net arca',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'KM3NET_ORCA': {
        'name': 'km3net orca',
        'location': 'km3net orca',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'KPNO': {
        'name': 'kpno',
        'location': 'kpno',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'L1': {
        'name': 'L1',
        'location': 'L1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LAPALMA': {
        'name': 'lapalma',
        'location': 'lapalma',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LARGE_BINOCULAR_TELESCOPE': {
        'name': 'Large Binocular Telescope',
        'location': 'Large Binocular Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LBT website',
    },
    'LASILLA': {
        'name': 'lasilla',
        'location': 'lasilla',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LAS_CAMPANAS_OBSERVATORY': {
        'name': 'Las Campanas Observatory',
        'location': 'Las Campanas Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LA_SILLA_OBSERVATORY': {
        'name': 'La Silla Observatory',
        'location': 'La Silla Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LA_SILLA_OBSERVATORY_(ESO)': {
        'name': 'La Silla Observatory (ESO)',
        'location': 'La Silla Observatory (ESO)',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LBT': {
        'name': 'lbt',
        'location': 'lbt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LBT website',
    },
    'LCO': {
        'name': 'lco',
        'location': 'lco',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LDT': {
        'name': 'ldt',
        'location': 'ldt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Site GPS on 20130708 UT as recorded in observatory wiki',
    },
    'LHO': {
        'name': 'LHO',
        'location': 'LHO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LHO_4K': {
        'name': 'lho_4k',
        'location': 'lho_4k',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LICK': {
        'name': 'lick',
        'location': 'lick',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LICK_OBSERVATORY': {
        'name': 'Lick Observatory',
        'location': 'Lick Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LIGO_HANFORD_OBSERVATORY': {
        'name': 'LIGO Hanford Observatory',
        'location': 'LIGO Hanford Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LIGO_LIVINGSTON_OBSERVATORY': {
        'name': 'LIGO Livingston Observatory',
        'location': 'LIGO Livingston Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LLO': {
        'name': 'LLO',
        'location': 'LLO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LLO_4K': {
        'name': 'llo_4k',
        'location': 'llo_4k',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'LOFAR': {
        'name': 'lofar',
        'location': 'lofar',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Dutch low-frequency array LOFAR.

        Note that other TEMPO codes have been used for this telescope.

        Imported from TEMPO2 observatories.dat 2021 June 7.
        via PINT''',
    },
    'LONG_WAVELENGTH_ARRAY_1': {
        'name': 'Long Wavelength Array 1',
        'location': 'Long Wavelength Array 1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The LWA(long wavelength array, in New Mexico).

        Origin of this data is unknown but as of 2021 June 8 this value agrees exactly with
        the value used by TEMPO2 but disagrees with the value used by TEMPO by about 125 m.
        via PINT''',
    },
    'LOWELL': {
        'name': 'lowell',
        'location': 'lowell',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LOWELL_DISCOVERY_TELESCOPE': {
        'name': 'Lowell Discovery Telescope',
        'location': 'Lowell Discovery Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Site GPS on 20130708 UT as recorded in observatory wiki',
    },
    'LOWELL_OBSERVATORY': {
        'name': 'Lowell Observatory',
        'location': 'Lowell Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 4.3 * u.m,
        'operational': True,
        'source': 'IRAF Observatory Database',
    },
    'LOWELL_OBSERVATORY___ANDERSON_MESA': {
        'name': 'Lowell Observatory - Anderson Mesa',
        'location': 'Lowell Observatory - Anderson Mesa',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LOWELL_OBSERVATORY___MARS_HILL': {
        'name': 'Lowell Observatory - Mars Hill',
        'location': 'Lowell Observatory - Mars Hill',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Lowell Observatory Staff',
    },
    'LOW_FREQUENCY_ARRAY': {
        'name': 'Low-Frequency Array',
        'location': 'Low-Frequency Array',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Dutch low-frequency array LOFAR.

        Note that other TEMPO codes have been used for this telescope.

        Imported from TEMPO2 observatories.dat 2021 June 7.
        via PINT''',
    },
    'LO_AM': {
        'name': 'lo-am',
        'location': 'lo-am',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'LO_MH': {
        'name': 'lo-mh',
        'location': 'lo-mh',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Lowell Observatory Staff',
    },
    'LSST': {
        'name': 'LSST',
        'location': 'LSST',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'LSST_1.4M': {
        'name': 'LSST 1.4m',
        'location': 'LSST 1.4m',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'LSST_8.4M': {
        'name': 'LSST 8.4m',
        'location': 'LSST 8.4m',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'LSST_AUXTEL': {
        'name': 'LSST AuxTel',
        'location': 'LSST AuxTel',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'LWA1': {
        'name': 'lwa1',
        'location': 'lwa1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The LWA(long wavelength array, in New Mexico).

        Origin of this data is unknown but as of 2021 June 8 this value agrees exactly with
        the value used by TEMPO2 but disagrees with the value used by TEMPO by about 125 m.
        via PINT''',
    },
    'MANASTASH_RIDGE_OBSERVATORY': {
        'name': 'Manastash Ridge Observatory',
        'location': 'Manastash Ridge Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'MRO website',
    },
    'MARS_HILL': {
        'name': 'mars_hill',
        'location': 'mars_hill',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Lowell Observatory Staff',
    },
    'MCDONALD': {
        'name': 'mcdonald',
        'location': 'mcdonald',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MCDONALD_OBSERVATORY': {
        'name': 'McDonald Observatory',
        'location': 'McDonald Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MDM': {
        'name': 'mdm',
        'location': 'mdm',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MDM_OBSERVATORY': {
        'name': 'MDM Observatory',
        'location': 'MDM Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MEDICINA': {
        'name': 'medicina',
        'location': 'medicina',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Medicina Radio Telescope website & google maps',
    },
    'MEDICINA_DISH': {
        'name': 'Medicina Dish',
        'location': 'Medicina Dish',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Medicina Radio Telescope website & google maps',
    },
    'MEDICINA_RADIO_TELESCOPE': {
        'name': 'Medicina Radio Telescope',
        'location': 'Medicina Radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Medicina Radio Telescope website & google maps',
    },
    'MEERKAT': {
        'name': 'meerkat',
        'location': 'meerkat',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''MEERKAT, used in timing mode.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'MH': {
        'name': 'mh',
        'location': 'mh',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Lowell Observatory Staff',
    },
    'MICHIGAN_DARTMOUTH_MIT_OBSERVATORY': {
        'name': 'Michigan-Dartmouth-MIT Observatory',
        'location': 'Michigan-Dartmouth-MIT Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MJO': {
        'name': 'MJO',
        'location': 'MJO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.geodesy.linz.govt.nz/gdb/index.cgi?code=6702',
    },
    'MMA': {
        'name': 'mma',
        'location': 'mma',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OVRO staff measurement of center of T using GNSS',
    },
    'MMT': {
        'name': 'mmt',
        'location': 'mmt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MOA': {
        'name': 'MOA',
        'location': 'MOA',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.geodesy.linz.govt.nz/gdb/index.cgi?code=6702',
    },
    'MONT_MÉGANTIC_OBSERVATORY': {
        'name': 'Mont Mégantic Observatory',
        'location': 'Mont Mégantic Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Google Maps',
    },
    'MOUNT_GRAHAM_INTERNATIONAL_OBSERVATORY': {
        'name': 'Mount Graham International Observatory',
        'location': 'Mount Graham International Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LBT website',
    },
    'MOUNT_WILSON_OBSERVATORY': {
        'name': 'Mount Wilson Observatory',
        'location': 'Mount Wilson Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CHARA website',
    },
    'MRO': {
        'name': 'mro',
        'location': 'mro',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'MRO website',
    },
    'MSO': {
        'name': 'mso',
        'location': 'mso',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MT._EKAR_182_CM_TELESCOPE': {
        'name': 'Mt. Ekar 182 cm Telescope',
        'location': 'Mt. Ekar 182 cm Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MT._STROMLO_OBSERVATORY': {
        'name': 'Mt. Stromlo Observatory',
        'location': 'Mt. Stromlo Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MTBIGELOW': {
        'name': 'mtbigelow',
        'location': 'mtbigelow',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MT_GRAHAM': {
        'name': 'Mt Graham',
        'location': 'Mt Graham',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LBT website',
    },
    'MT_JOHN': {
        'name': 'Mt John',
        'location': 'Mt John',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.geodesy.linz.govt.nz/gdb/index.cgi?code=6702',
    },
    'MULTIPLE_MIRROR_TELESCOPE': {
        'name': 'Multiple Mirror Telescope',
        'location': 'Multiple Mirror Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'MURCHISON_WIDEFIELD_ARRAY': {
        'name': 'Murchison Widefield Array',
        'location': 'Murchison Widefield Array',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'MWA website: http://mwatelescope.org/telescope',
    },
    'MURRIYANG': {
        'name': 'Murriyang',
        'location': 'Murriyang',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Parkes radio telescope.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'MWA': {
        'name': 'mwa',
        'location': 'mwa',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'MWA website: http://mwatelescope.org/telescope',
    },
    'MWO': {
        'name': 'mwo',
        'location': 'mwo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CHARA website',
    },
    'NANCAY': {
        'name': 'nancay',
        'location': 'nancay',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Nançay radio telescope.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'NANCAY_RADIO_TELESCOPE': {
        'name': 'Nancay Radio Telescope',
        'location': 'Nancay Radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Nançay radio telescope.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'NASA_INFRARED_TELESCOPE_FACILITY': {
        'name': 'NASA Infrared Telescope Facility',
        'location': 'NASA Infrared Telescope Facility',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRTF Website',
    },
    'NATIONAL_OBSERVATORY_OF_VENEZUELA': {
        'name': 'National Observatory of Venezuela',
        'location': 'National Observatory of Venezuela',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'NAVY_PRECISION_OPTICAL_INTERFEROMETER': {
        'name': 'Navy Precision Optical Interferometer',
        'location': 'Navy Precision Optical Interferometer',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'NOTO': {
        'name': 'noto',
        'location': 'noto',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Noto Radio Telescope website & google maps',
    },
    'NOTO_RADIO_TELESCOPE': {
        'name': 'Noto Radio Telescope',
        'location': 'Noto Radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Noto Radio Telescope website & google maps',
    },
    'NOV': {
        'name': 'NOV',
        'location': 'NOV',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'NOVA': {
        'name': 'nova',
        'location': 'nova',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'NPOI': {
        'name': 'NPOI',
        'location': 'NPOI',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'NST': {
        'name': 'NST',
        'location': 'NST',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'BBSO website: http://www.bbso.njit.edu/newinfo.html',
    },
    'NUMI_OFF_AXIS_ΝE_APPEARANCE': {
        'name': 'NuMI Off-axis νe Appearance',
        'location': 'NuMI Off-axis νe Appearance',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'OAJ': {
        'name': 'OAJ',
        'location': 'OAJ',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Google Earth',
    },
    'OAO': {
        'name': 'OAO',
        'location': 'OAO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OAO Website (http://www.oao.nao.ac.jp/en/telescope/abouttel188/)',
    },
    'OARMA': {
        'name': 'OARMA',
        'location': 'OARMA',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OpenStreetView',
    },
    'OBSERVATOIRE_DE_HAUTE_PROVENCE': {
        'name': 'Observatoire de Haute Provence',
        'location': 'Observatoire de Haute Provence',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OHP website',
    },
    'OBSERVATOIRE_DU_MONT_MÉGANTIC': {
        'name': 'Observatoire du Mont Mégantic',
        'location': 'Observatoire du Mont Mégantic',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Google Maps',
    },
    'OBSERVATOIRE_SIRENE': {
        'name': 'Observatoire SIRENE',
        'location': 'Observatoire SIRENE',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SIRENE website',
    },
    'OBSERVATORIO_ASTROFISICO_DE_JAVALAMBRE': {
        'name': 'Observatorio Astrofisico de Javalambre',
        'location': 'Observatorio Astrofisico de Javalambre',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Google Earth',
    },
    'OBSERVATORIO_ASTRONOMICO_NACIONAL,_SAN_PEDRO_MARTIR': {
        'name': 'Observatorio Astronomico Nacional, San Pedro Martir',
        'location': 'Observatorio Astronomico Nacional, San Pedro Martir',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'OBSERVATORIO_ASTRONOMICO_NACIONAL,_TONANTZINTLA': {
        'name': 'Observatorio Astronomico Nacional, Tonantzintla',
        'location': 'Observatorio Astronomico Nacional, Tonantzintla',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'OBSERVATORIO_ASTRONOMICO_RAMON_MARIA_ALLER,_SANTIAGO_DE_COMPOSTELA': {
        'name': 'Observatorio Astronomico Ramon Maria Aller, Santiago de Compostela',
        'location': 'Observatorio Astronomico Ramon Maria Aller, Santiago de Compostela',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OpenStreetView',
    },
    'OBSERVATORIO_CERRO_ARMAZONES': {
        'name': 'Observatorio Cerro Armazones',
        'location': 'Observatorio Cerro Armazones',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://araucaria.camk.edu.pl/index.php/observatory-cerro-armazones/',
    },
    'OBSERVATORIO_DEL_TEIDE': {
        'name': 'Observatorio del Teide',
        'location': 'Observatorio del Teide',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Instituto de Astrofisica de Canarias website (http://research.iac.es/OOCC/observatorio-del-teide/ot/)',
    },
    'OBSERVATORIO_DEL_TEIDE,_TENERIFE': {
        'name': 'Observatorio del Teide, Tenerife',
        'location': 'Observatorio del Teide, Tenerife',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Instituto de Astrofisica de Canarias website (http://research.iac.es/OOCC/observatorio-del-teide/ot/)',
    },
    'OBSERVATORIO_DE_CALAR_ALTO': {
        'name': 'Observatorio de Calar Alto',
        'location': 'Observatorio de Calar Alto',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'CAHA Wikipedia page (https://en.wikipedia.org/wiki/Calar_Alto_Observatory)',
    },
    'OBSERVATORIO_RAMON_MARIA_ALLER': {
        'name': 'Observatorio Ramon Maria Aller',
        'location': 'Observatorio Ramon Maria Aller',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OpenStreetView',
    },
    'OCA': {
        'name': 'oca',
        'location': 'oca',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://araucaria.camk.edu.pl/index.php/observatory-cerro-armazones/',
    },
    'OHP': {
        'name': 'ohp',
        'location': 'ohp',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OHP website',
    },
    'OKAYAMA_ASTROPHYSICAL_OBSERVATORY': {
        'name': 'Okayama Astrophysical Observatory',
        'location': 'Okayama Astrophysical Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OAO Website (http://www.oao.nao.ac.jp/en/telescope/abouttel188/)',
    },
    'OMM': {
        'name': 'omm',
        'location': 'omm',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Google Maps',
    },
    'ORCA': {
        'name': 'orca',
        'location': 'orca',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'OSCILLATION_RESEARCH_WITH_COSMICS_IN_THE_ABYSS': {
        'name': 'Oscillation Research with Cosmics in the Abyss',
        'location': 'Oscillation Research with Cosmics in the Abyss',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'OT': {
        'name': 'OT',
        'location': 'OT',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Instituto de Astrofisica de Canarias website (http://research.iac.es/OOCC/observatorio-del-teide/ot/)',
    },
    'OTEHIWAI': {
        'name': 'Otehiwai',
        'location': 'Otehiwai',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.geodesy.linz.govt.nz/gdb/index.cgi?code=6702',
    },
    'OTEHIWAI_OBSERVATORY': {
        'name': 'Otehiwai Observatory',
        'location': 'Otehiwai Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://www.geodesy.linz.govt.nz/gdb/index.cgi?code=6702',
    },
    'OVRO': {
        'name': 'ovro',
        'location': 'ovro',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OVRO staff measurement of center of T using GNSS',
    },
    'OWENS_VALLEY_RADIO_OBSERVATORY': {
        'name': 'Owens Valley Radio Observatory',
        'location': 'Owens Valley Radio Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'OVRO staff measurement of center of T using GNSS',
    },
    'PALOMAR': {
        'name': 'Palomar',
        'location': 'Palomar',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'PARANAL': {
        'name': 'paranal',
        'location': 'paranal',
        'instruments': [],  # TODO: Add instruments
        'diameter': 8.2 * u.m,
        'operational': True,
        'source': 'Official reference in VLTI raw data products',
    },
    'PARANAL_OBSERVATORY': {
        'name': 'Paranal Observatory',
        'location': 'Paranal Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Official reference in VLTI raw data products',
    },
    'PARANAL_OBSERVATORY_(ESO)': {
        'name': 'Paranal Observatory (ESO)',
        'location': 'Paranal Observatory (ESO)',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Official reference in VLTI raw data products',
    },
    'PARKES': {
        'name': 'parkes',
        'location': 'parkes',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': '''The Parkes radio telescope.

        The origin of this data is unknown but as of 2021 June 8 it agrees exactly with
        the values used by TEMPO and TEMPO2.
        via PINT''',
    },
    'PERKINS': {
        'name': 'Perkins',
        'location': 'Perkins',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'PTO': {
        'name': 'pto',
        'location': 'pto',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'ROQUE_DE_LOS_MUCHACHOS': {
        'name': 'Roque de los Muchachos',
        'location': 'Roque de los Muchachos',
        'instruments': [],  # TODO: Add instruments
        'diameter': 3.58 * u.m,
        'operational': True,
        'source': 'IRAF Observatory Database',
    },
    'ROQUE_DE_LOS_MUCHACHOS,_LA_PALMA': {
        'name': 'Roque de los Muchachos, La Palma',
        'location': 'Roque de los Muchachos, La Palma',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'ROYAL_OBSERVATORY_GREENWICH': {
        'name': 'Royal Observatory Greenwich',
        'location': 'Royal Observatory Greenwich',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Ordnance Survey via http://gpsinformation.net/main/greenwich.htm and UNESCO',
    },
    'RUBIN': {
        'name': 'rubin',
        'location': 'rubin',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'RUBIN_AUX': {
        'name': 'rubin_aux',
        'location': 'rubin_aux',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'RUBIN_AUXTEL': {
        'name': 'Rubin AuxTel',
        'location': 'Rubin AuxTel',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'RUBIN_OBSERVATORY': {
        'name': 'Rubin Observatory',
        'location': 'Rubin Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://arxiv.org/abs/1210.1616',
    },
    'SAAO': {
        'name': 'SAAO',
        'location': 'SAAO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SALT website & google maps',
    },
    'SACRAMENTO_PEAK': {
        'name': 'Sacramento Peak',
        'location': 'Sacramento Peak',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'NSO website: https://nsosp-dev.nso.edu/node/18',
    },
    'SACRAMENTO_PEAK_OBSERVATORY': {
        'name': 'Sacramento Peak Observatory',
        'location': 'Sacramento Peak Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'NSO website: https://nsosp-dev.nso.edu/node/18',
    },
    'SAC_PEAK': {
        'name': 'Sac Peak',
        'location': 'Sac Peak',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'NSO website: https://nsosp-dev.nso.edu/node/18',
    },
    'SALT': {
        'name': 'salt',
        'location': 'salt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SALT website & google maps',
    },
    'SARDINIA_RADIO_TELESCOPE': {
        'name': 'Sardinia Radio Telescope',
        'location': 'Sardinia Radio Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRT single dish tools & pulsar software such as TEMPO2 and PINT. Converted through EarthLocation(4865182.7660, 791922.6890, 4035137.1740, unit=u.m).to_geodetic() on 2022-11-21',
    },
    'SIDING_SPRING_OBSERVATORY': {
        'name': 'Siding Spring Observatory',
        'location': 'Siding Spring Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'SIRENE': {
        'name': 'sirene',
        'location': 'sirene',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SIRENE website',
    },
    'SNO+': {
        'name': 'sno+',
        'location': 'sno+',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'SOUTHERN_AFRICAN_LARGE_TELESCOPE': {
        'name': 'Southern African Large Telescope',
        'location': 'Southern African Large Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SALT website & google maps',
    },
    'SPM': {
        'name': 'spm',
        'location': 'spm',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'SPO': {
        'name': 'spo',
        'location': 'spo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'NSO website: https://nsosp-dev.nso.edu/node/18',
    },
    'SRT': {
        'name': 'srt',
        'location': 'srt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SRT single dish tools & pulsar software such as TEMPO2 and PINT. Converted through EarthLocation(4865182.7660, 791922.6890, 4035137.1740, unit=u.m).to_geodetic() on 2022-11-21',
    },
    'SSO': {
        'name': 'sso',
        'location': 'sso',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'SUBARU': {
        'name': 'Subaru',
        'location': 'Subaru',
        'instruments': [],  # TODO: Add instruments
        'diameter': 8.2 * u.m,
        'operational': True,
        'source': 'Subaru Telescope website (August 2015)',
    },
    'SUBARU_TELESCOPE': {
        'name': 'Subaru Telescope',
        'location': 'Subaru Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Subaru Telescope website (August 2015)',
    },
    'SUDBURY_NEUTRINO_OBSERVATORY_+': {
        'name': 'Sudbury Neutrino Observatory +',
        'location': 'Sudbury Neutrino Observatory +',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SNEWS 2.0 Collaboration',
    },
    'SUNSPOT': {
        'name': 'Sunspot',
        'location': 'Sunspot',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'NSO website: https://nsosp-dev.nso.edu/node/18',
    },
    'SUPERK': {
        'name': 'superk',
        'location': 'superk',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SK detector paper, Fukuda et al. 2003',
    },
    'SUPER_KAMIOKANDE': {
        'name': 'Super-Kamiokande',
        'location': 'Super-Kamiokande',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SK detector paper, Fukuda et al. 2003',
    },
    'SUTHERLAND': {
        'name': 'Sutherland',
        'location': 'Sutherland',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'SALT website & google maps',
    },
    'TEIDE': {
        'name': 'teide',
        'location': 'teide',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Instituto de Astrofisica de Canarias website (http://research.iac.es/OOCC/observatorio-del-teide/ot/)',
    },
    'THAI_NATIONAL_OBSERVATORY': {
        'name': 'Thai National Observatory',
        'location': 'Thai National Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'TNO Wikipedia page (https://en.wikipedia.org/wiki/Thai_National_Observatory)',
    },
    'THE_HALE_TELESCOPE': {
        'name': 'The Hale Telescope',
        'location': 'The Hale Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'TNO': {
        'name': 'TNO',
        'location': 'TNO',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'TNO Wikipedia page (https://en.wikipedia.org/wiki/Thai_National_Observatory)',
    },
    'TONA': {
        'name': 'tona',
        'location': 'tona',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'TUBITAK_NATIONAL_OBSERVATORY': {
        'name': 'TUBITAK National Observatory',
        'location': 'TUBITAK National Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'TUG Website: http://www.tug.tubitak.gov.tr/gozlemevi.php',
    },
    'TUG': {
        'name': 'tug',
        'location': 'tug',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'TUG Website: http://www.tug.tubitak.gov.tr/gozlemevi.php',
    },
    'UKIRT': {
        'name': 'ukirt',
        'location': 'ukirt',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IfA website via Starlink/PAL',
    },
    'UNITED_KINGDOM_INFRARED_TELESCOPE': {
        'name': 'United Kingdom Infrared Telescope',
        'location': 'United Kingdom Infrared Telescope',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IfA website via Starlink/PAL',
    },
    'V1': {
        'name': 'V1',
        'location': 'V1',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'VAINU_BAPPU_OBSERVATORY': {
        'name': 'Vainu Bappu Observatory',
        'location': 'Vainu Bappu Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'VBO': {
        'name': 'vbo',
        'location': 'vbo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'VERY_LARGE_ARRAY': {
        'name': 'Very Large Array',
        'location': 'Very Large Array',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Very_Large_Array',
    },
    'VIRGO': {
        'name': 'virgo',
        'location': 'virgo',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'VIRGO_OBSERVATORY': {
        'name': 'Virgo Observatory',
        'location': 'Virgo Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'LALSuite: https://git.ligo.org/lscsoft/lalsuite/-/blob/lalsuite-v6.70/lal/lib/tools/LALDetectors.h',
    },
    'VLA': {
        'name': 'vla',
        'location': 'vla',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'https://en.wikipedia.org/wiki/Very_Large_Array',
    },
    'W._M._KECK_OBSERVATORY': {
        'name': 'W. M. Keck Observatory',
        'location': 'W. M. Keck Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'WHIPPLE': {
        'name': 'Whipple',
        'location': 'Whipple',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'WHIPPLE_OBSERVATORY': {
        'name': 'Whipple Observatory',
        'location': 'Whipple Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'IRAF Observatory Database',
    },
    'WISE': {
        'name': 'wise',
        'location': 'wise',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Wise Observatory One Meter Telescope Manual http://wise-obs.tau.ac.il/observations/Man/wise_man.pdf',
    },
    'WISE_OBSERVATORY': {
        'name': 'Wise Observatory',
        'location': 'Wise Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'Wise Observatory One Meter Telescope Manual http://wise-obs.tau.ac.il/observations/Man/wise_man.pdf',
    },
    'WIYN': {
        'name': 'wiyn',
        'location': 'wiyn',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'WIYN 3.5m TCS',
    },
    'WIYN_3.5_M': {
        'name': 'WIYN 3.5 m',
        'location': 'WIYN 3.5 m',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'WIYN 3.5m TCS',
    },
    'WIYN_OBSERVATORY': {
        'name': 'WIYN Observatory',
        'location': 'WIYN Observatory',
        'instruments': [],  # TODO: Add instruments
        'diameter': 0.0 * u.m,
        'operational': False,
        'source': 'WIYN 3.5m TCS',
    },
}
