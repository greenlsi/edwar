from abc import ABC, abstractmethod


class Module(ABC):

    def __init__(self):
        self._activated = True
        self._inputs = set()
        self._outputs = set()
        super().__init__()

    @property
    def is_active(self):
        return self._activated

    @is_active.setter
    def is_active(self, newvalue):
        if isinstance(newvalue, bool):
            self._activated = newvalue
        else:
            raise TypeError("\n\t(!) Something went wrong: is_active method from Module class needs a boolean" +
                            " as parameter\n")

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, newvalue):
        if isinstance(newvalue, set):
            self._inputs = newvalue
        elif isinstance(newvalue, str):
            self._inputs.add(newvalue)
        else:
            raise TypeError("\n\t(!) Something went wrong: input method from Module class needs a string or set of " +
                            "strings as parameter\n")

    @inputs.deleter
    def inputs(self):
        self._inputs = set()

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, newvalue):
        if isinstance(newvalue, set):
            self._outputs = newvalue
        elif isinstance(newvalue, str):
            self._outputs.add(newvalue)
        else:
            raise TypeError("\n\t(!) Something went wrong: output method from Module class needs a string or set of " +
                            "strings as parameter\n")

    @outputs.deleter
    def outputs(self):
        self._outputs = set()

    @abstractmethod
    def run_module(self, data):
        pass


class EDAmodule(Module):
    def __init__(self):
        super().__init__()
        self.inputs = {'EDA', 'ACCx', 'ACCy', 'ACCz'}
        self.outputs = {'EDA', 'SCL', 'SCR'}

    def run_module(self, data):
        return data


class ACCmodule(Module):
    def __init__(self):
        super().__init__()
        self.inputs = {'ACCx', 'ACCy', 'ACCz'}
        self.outputs = {'ACCx', 'ACCy', 'ACCz'}

    def run_module(self, data):
        return data


class IBImodule(Module):
    def __init__(self):
        super().__init__()
        self.inputs = {'IBI'}
        self.outputs = {'IBI'}

    def run_module(self, data):
        return data


class TEMPmodule(Module):
    def __init__(self):
        super().__init__()
        self.inputs = {'TEMP'}
        self.outputs = {'TEMP'}

    def run_module(self, data):
        return data
