import json
from . import abc_parts

from ..constants import LIQUID_FUEL_DENSITY, OXIDISER_DENSITY, CONFIG_PATH


class Tank(abc_parts.ABCPart):
    def __init__(self, tank_name: str):
        self._tank_name = tank_name
        self._read_config()

    def _read_config(self):
        with open(CONFIG_PATH) as file:
            data = json.load(file)['Parts']['Tanks']

        if self._tank_name not in data.keys():
            raise ValueError(f'{self._tank_name} is not a fuel tank')
        else:
            data = data[self._tank_name]
        
        self._dry_mass = data['mass']
        self._oxidiser_volume = data['max_oxidiser_volume']
        self._fuel_volumne = data['max_fuel_volume']

    @property
    def dry_mass(self):
        return self._dry_mass

    @property
    def thrust(self):
        return 0

    @property
    def isp(self):
        return 0

    @property
    def propellant_mass(self):
        oxidiser_mass = self._oxidiser_volume * OXIDISER_DENSITY
        fuel_mass = self._fuel_volumne * LIQUID_FUEL_DENSITY
        return fuel_mass + oxidiser_mass