import os
from abc import ABC, abstractmethod

from . import e4, everion
from ..utils import Settings, configuration


__enum__ = {
    'LoaderE4',
    'LoaderEverion'
}


class Loader(ABC):

    class Units:
        # Kwards for adding new variables
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, path, settings=Settings()):
        structure_file = os.path.join(settings.path, settings.structureini)
        if not os.path.exists(structure_file):
            raise Exception("\n\t(!) Something went wrong: Configuration file {} not found"
                            "\n\t    Run edwar.install.structure_cfg() to create it".format(structure_file))
        self.path = path
        self.variables = None
        self.units = None
        super().__init__()

    def get_units(self):
        return self.units.__dict__

    @abstractmethod
    def get_data(self):
        pass


# Given examples
class LoaderE4(Loader):
    def __init__(self, path, settings=Settings()):
        super().__init__(path, settings=settings)
        self.variables = configuration.get_input_variables(settings, 'E4')[1]
        self.units = super().Units(hr='bpm', acc='g', bvp=None, eda='uS', temp='ºC', ibi='s')

    def get_data(self):
        return e4.load_files(self.path, self.variables)


class LoaderEverion(Loader):
    def __init__(self, path, settings=Settings()):
        super().__init__(path, settings=settings)
        self.variables = configuration.get_input_variables(settings, 'Everion')[1]
        self.units = super().Units(eda='uS', temp='ºC', ibi='s', hr='bpm', hrv='s', bperf=None, bpw=None,
                                   activity=None, act_class=None, rr='bpm', ee='cal/s', barometer='mbar', sp02='%',
                                   steps='steps')

    def get_data(self):
        return everion.load_files(self.path, self.variables)


class LoaderBioplux(Loader):
    def __init__(self, path, settings=Settings()):
        super().__init__(path, settings=settings)
        self.variables = configuration.get_input_variables(settings, 'OnyxII')[1]
        self.units = super().Units(eda='uS', temp='ºC', ecg='V', eeg='V')

    def get_data(self):
        return everion.load_files(self.path, self.variables)


class LoaderOnyx(Loader):
    def __init__(self, path, settings=Settings()):
        super().__init__(path, settings=settings)
        self.variables = configuration.get_input_variables(settings, 'Onyx')[1]
        self.units = super().Units(ppg='V',)

    def get_data(self):
        return everion.load_files(self.path, self.variables)
