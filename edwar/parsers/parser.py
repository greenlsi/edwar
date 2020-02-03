from abc import ABC, abstractmethod
import pandas as pd
import functools


class Parser(ABC):

    def __init__(self, inputs, outputs, optional_inputs=None, optional_outputs=None):

        if type(inputs) is dict:
            self.inputs = inputs
        else:
            raise TypeError("(!) Parser arguments 'inputs' must be dictionary")

        if type(outputs) is dict:
            self.outputs = outputs
        else:
            raise TypeError("(!) Parser arguments 'outputs' must be dictionary")

        if optional_inputs:
            if type(optional_inputs) is dict:
                self.optional_inputs = optional_inputs
            else:
                raise TypeError("(!) Parser arguments 'optional_inputs' must be dictionary")
        else:
            self.optional_inputs = dict()

        if optional_outputs:
            if type(optional_outputs) is dict:
                self.optional_outputs = optional_outputs
            else:
                raise TypeError("(!) Parser arguments 'optional_inputs' must be dictionary")
        else:
            self.optional_outputs = dict()

        super().__init__()

    @staticmethod
    def check_input(name, data, expected_inputs, optional_inputs):
        inputs = list()
        expected = list(expected_inputs.keys())
        plus = list(optional_inputs.keys())
        for d in data:
            inputs += list(d.columns)
        if [i for i in inputs if i in expected] != expected:
            raise ValueError('(!) {} expected input is {}, but got {}'.format(name, expected, inputs))
        elif [i for i in inputs if i in plus] != plus:
            raise UserWarning('(!) {} expected input is {}, but got {}: Parser will work only partially'.
                              format(name, expected + plus, inputs))

    @staticmethod
    def adapt_input(data):
        out = functools.reduce(lambda df1, df2: pd.merge(df1, df2, right_index=True, left_index=True), data)
        return out

    @abstractmethod
    def run(self, data):
        pass


class EDAparser(Parser):
    def __init__(self):
        super().__init__(inputs={'EDA': 'uS'}, optional_inputs={'ACCx': 'g', 'ACCy': 'g', 'ACCz': 'g'},
                         outputs={'EDA': 'uS', 'SCL': 'uS', 'SCR': 'uS'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        out = self.adapt_input(data)
        return out


class ACCparser(Parser):
    def __init__(self):
        super().__init__(inputs={'ACCx': 'g', 'ACCy': 'g', 'ACCz': 'g'},
                         outputs={'ACCx': 'g', 'ACCy': 'g', 'ACCz': 'g'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        out = self.adapt_input(data)
        return out


class IBIparser(Parser):
    def __init__(self):
        super().__init__(inputs={'IBI': 's'}, outputs={'IBI': 's'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        out = self.adapt_input(data)
        return out


class TEMPparser(Parser):
    def __init__(self):
        super().__init__(inputs={'TEMP': 'ºC'}, outputs={'TEMP': 'ºC'})

    def run(self, data):
        self.check_input(self.__class__.__name__, data, self.inputs, self.optional_inputs)
        out = self.adapt_input(data)
        return out
