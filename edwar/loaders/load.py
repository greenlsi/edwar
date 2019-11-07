from abc import ABC, abstractmethod
from . import e4, everion


class Loader(ABC):

    def __init__(self, path, downsample=None):
        self.path = path
        self.downsample = downsample
        super().__init__()

    @abstractmethod
    def get_data(self):
        pass


# Given examples
class LoaderE4(Loader):
    def get_data(self):
        return e4.load_files(self.path, self.downsample)


class LoaderEverion(Loader):
    def get_data(self):
        return everion.load_files(self.path, self.downsample)
