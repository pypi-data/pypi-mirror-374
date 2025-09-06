from . import instruments
import astropy.coordinates as coord
import astropy.units as u
import numpy as np
from dataclasses import dataclass, field
import logging
from ..utils.utilities import logger_default
from .telescope_config import TELESCOPE_CONFIGS

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger = logger_default(logger)


@dataclass
class Telescope():
    name: str
    location: coord.earth.EarthLocation
    instruments: list = field(default_factory=list)
    diameter: u.Quantity = 0 * u.m,
    operational: bool = True,
    variable_name: str = ''

    def telescope_constraints(self, Event):
        logger.warning('Telescope constraints not implemented yet.')
        return

    def zenith_constraints(self, Event):
        logger.warning('Telescope zenith constraints not implemented yet.')
        return


class SwissEulerTelescope(Telescope):
    pass


SwissEuler = SwissEulerTelescope(
    name='Swiss Euler Telescope',
    location=coord.EarthLocation.of_site('La Silla Observatory'),
    instruments=[instruments.CORALIE],
    diameter=1.2 * u.m
)


class LaSilla36mTelescope(Telescope):
    pass


LaSilla3_6m = LaSilla36mTelescope(
    name='ESO 3.6m Telescope (La Silla)',
    location=coord.EarthLocation.of_site('La Silla Observatory (ESO)'),
    instruments=[instruments.HARPS, instruments.NIRPS],
    diameter=3.6 * u.m
)


class VLTTelescope(Telescope):
    pass


VLT = VLTTelescope(
    name='Very Large Telescope (VLT)',
    location=coord.EarthLocation.of_site('Paranal'),
    instruments=[instruments.ESPRESSO, instruments.UVES],
    diameter=8.2 * u.m
)


class VLT4UTTelescope(Telescope):
    pass


VLT_4UT = VLT4UTTelescope(
    name='Very Large Telescope (VLT) 4-UT',
    location=coord.EarthLocation.of_site('Paranal'),
    instruments=[instruments.ESPRESSO_4UT],
    diameter=2 * 8.2 * u.m  # Combined light from all 4 UTs
)


class LowellDiscoveryTelescope(Telescope):
    pass


LowellDiscovery = LowellDiscoveryTelescope(
    name='Lowell Discovery Telescope',
    location=coord.EarthLocation.of_site('Lowell Observatory'),
    instruments=[instruments.EXPRES],
    diameter=4.3 * u.m
)


class TNGTelescope(Telescope):
    pass


TNG = TNGTelescope(
    name='Telescopio Nazionale Galileo (TNG)',
    location=coord.EarthLocation.of_site('Roque de los Muchachos'),
    instruments=[instruments.GIANO, instruments.HARPS_N],
    diameter=3.58 * u.m
)


class GeminiNorthTelescope(Telescope):
    pass


GeminiNorth = GeminiNorthTelescope(
    name='Gemini North Telescope',
    location=coord.EarthLocation.of_site('gemini_north'),
    instruments=[instruments.MAROON_X],
    diameter=8.1 * u.m
)


class CFHTTelescope(Telescope):
    pass


CFHT = CFHTTelescope(
    name='Canada-France-Hawaii Telescope (CFHT)',
    location=coord.EarthLocation.of_site('Canada-France-Hawaii Telescope'),
    instruments=[instruments.SPIROU],
    diameter=3.6 * u.m
)


class HauteProvenceTelescope(Telescope):
    pass


HauteProvence = HauteProvenceTelescope(
    name='Haute-Provence Observatory',
    location=coord.EarthLocation.of_site('Observatoire de Haute Provence'),
    instruments=[instruments.SOPHIE],
    diameter=1.93 * u.m
)


class CalarAltoObservatory(Telescope):
    pass


CalarAlto = CalarAltoObservatory(
    name='Calar Alto Observatory',
    location=coord.EarthLocation.of_site('Observatorio de Calar Alto'),
    instruments=[instruments.CARMENES],
    diameter=3.5 * u.m
)


class TelescopeFactory:
    @staticmethod
    def create_telescope(telescope_type: str) -> Telescope:
        """Create a telescope instance based on the telescope type."""
        if telescope_type not in TELESCOPE_CONFIGS:
            raise ValueError(f"Unknown telescope type: {telescope_type}")

        config = TELESCOPE_CONFIGS[telescope_type]
        return Telescope(
            name=config['name'],
            location=coord.EarthLocation.of_site(config['location']),
            instruments=config['instruments'],
            diameter=config['diameter']
        )

def print_all_telescopes(instruments: str = 'all') -> None:
    if instruments != 'all':
        raise NotImplementedError

    telescopes_list = [(telescope_name, telescope) for telescope_name,
                       telescope in globals().items() if isinstance(telescope, Telescope)]
    telescopes_list.sort(
        reverse=True, key=lambda telescopes_list: telescopes_list[1].diameter.to(u.m).value)

    logger.print('Printing available telescopes:')
    logger.info('Use the first name to access the telescope object.')
    logger.info(
        '    e.g., to access the VLT telescope, use "VLT" instead of "Very Large Telescope (VLT)"')
    logger.print('='*25)
    for (telescope_name, telescope) in telescopes_list:
        logger.print(
            f"{telescope_name} : {telescope.name} | {telescope.diameter} | Operational: {bool(telescope.operational)}")
        logger.print(
            f"    {[instrument.name for instrument in telescope.instruments]}")


if __name__ == '__main__':
    logger.warning('='*25)
    logger.warning('Debugging mode: Telescopes module')
    logger.warning('='*25)
    print_all_telescopes()
    from . import instruments as inst
    inst.print_all_spectrographs()

    print([mode for mode in inst.ESPRESSO.modes if mode.exposure_time_calculator is not None])

    for mode in [mode for mode in inst.ESPRESSO.modes if mode.exposure_time_calculator is not None]:
        mode.exposure_time_calculator.open_all_scenarios(
            stellar_temperature=5500)

    logger.warning('='*25)
    logger.warning('End of debugging mode: Telescopes module')
    logger.warning('='*25)
