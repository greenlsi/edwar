from abc import ABC, abstractmethod
import pandas as pd
import functools

from .ibi import check_ibi, calculate_hr, calculate_josue_hr
from .eda import process_eda
from .parameters import *


class Parser(ABC):

    def __init__(self, inputs: dict, outputs: dict, optional_inputs: dict = None, optional_outputs: dict = None):

        self.inputs = inputs
        self.outputs = outputs
        self.optional_inputs = optional_inputs if optional_inputs else dict()
        self.optional_outputs = optional_outputs if optional_outputs else dict()
        super().__init__()

    @staticmethod
    def check_input(name, data, expected_inputs, optional_inputs):
        inputs = list()
        expected = list(expected_inputs.keys())
        plus = list(optional_inputs.keys())
        for d in data:
            inputs += list(d.columns)
        if [i for i in inputs if i in expected] != expected:
            raise ValueError('{} expected input is {}, but got {}'.format(name, expected, inputs))
        elif [i for i in inputs if i in plus] != plus:
            pass
            # raise UserWarning('expected input is {}, but got {}: Parser will work only partially'.
            #                   format(expected + plus, inputs))

    @staticmethod
    def adapt_input(data):
        out = functools.reduce(lambda df1, df2: pd.merge(df1, df2, right_index=True, left_index=True), data)
        return out

    @abstractmethod
    def run(self, data):
        pass


class EDAparser(Parser):
    def __init__(self):
        super().__init__(inputs={'EDA': 'uS'},  # optional_inputs={'ACCx': 'g', 'ACCy': 'g', 'ACCz': 'g'},
                         outputs={'EDA': 'uS', 'SCL': 'uS', 'SCR': 'uS'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        if not isinstance(EDA_CLASSIFIER, list):
            raise TypeError('EDA_CLASSIFIER must be a list')
        elif not ('Binary' or 'Multiclass') in EDA_CLASSIFIER:
            raise ValueError('EDA_CLASSIFIER must be Binary or Multiclass')
        eda_processed = process_eda(data[0], EDA_CLASSIFIER)
        return eda_processed


class ACCparser(Parser):
    def __init__(self):
        super().__init__(inputs={'ACCx': 'g', 'ACCy': 'g', 'ACCz': 'g'},
                         outputs={'ACCx': 'g', 'ACCy': 'g', 'ACCz': 'g'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        out = self.adapt_input(data)
        return out


class IBIparser(Parser):
    def __init__(self, signal=IBI_SIGNAL, correction=IBI_CORRECTION):
        super().__init__(inputs={'IBI': 's'}, outputs={'IBI': 's'})
        self.signal = signal
        self.correction = correction

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        ibi = check_ibi(self.adapt_input(data), self.correction)
        if self.signal == 'noisy':
            hr = calculate_hr(ibi)
        else:
            hr = calculate_josue_hr(ibi)
        return [ibi, hr]


class TEMPparser(Parser):
    def __init__(self):
        super().__init__(inputs={'TEMP': 'ºC'}, outputs={'TEMP': 'ºC'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        out = self.adapt_input(data)
        return out
