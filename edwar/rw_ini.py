import configparser


class Structure:
    def __init__(self, structurefile='structure.ini'):
        self.parser = configparser.ConfigParser(inline_comment_prefixes="#", allow_no_value=True)
        self.parser.optionxform = str
        ok = self.parser.read(structurefile)
        if not ok:
            raise IOError("(!) Something went wrong: No file %s found" % structurefile)
        self.structurefile = structurefile
        try:
            self._devices = dict(self.parser.items(section='DEVICES'))
        except configparser.NoSectionError:
            raise RuntimeError("(!) Something went wrong: No section 'DEVICES' found in %s" % structurefile)

    def devices(self):
        return self._devices

    def set_device(self, device, load_function):
        self._devices[device] = load_function

    def remove_device(self, device):
        if self.check_device(device):
            del self._devices[device]
            self.parser.remove_section('VARIABLES ' + device.upper())
            self.parser.remove_section('FEATURES ' + device.upper())

    def check_device(self, device):
        if device in self.devices().keys():
            return 1
        raise KeyError("(!) Something went wrong: No device %s found" % device)

    def variables(self, device):
        v = dict()
        if self.check_device(device):
            try:
                v = dict(self.parser.items(section='VARIABLES ' + device.upper()))
            except configparser.NoSectionError:
                pass
        return v

    def set_variable(self, device, file, variables):
        self.set_variables(device, {file: variables})

    def set_variables(self, device, variables):
        variables.update(self.variables(device))
        if self.check_device(device):
            self.parser['VARIABLES ' + device.upper()] = variables

    def remove_file(self, device, file):
        if self.check_device(device):
            try:
                del self.parser['VARIABLES ' + device.upper()][file]
            except KeyError:
                raise KeyError("(!) Something went wrong: No file %s found for device %s" % (file, device))

    def lock_file(self, device, file):
        if self.check_device(device):
            if file in self.variables(device).keys():
                newfile = '.' + file
                self.parser['VARIABLES ' + device.upper()][newfile] = self.parser['VARIABLES ' + device.upper()].pop(
                    file)
            else:
                raise KeyError("(!) Something went wrong: No unlocked file %s found for device %s" % (file, device))

    def unlock_file(self, device, file):
        lockfile = '.' + file
        if self.check_device(device):
            if lockfile in self.variables(device).keys():
                self.parser['VARIABLES ' + device.upper()][file] = self.parser['VARIABLES ' + device.upper()].pop(
                    lockfile)
            else:
                raise KeyError("(!) Something went wrong: No locked file %s found for device %s" % (file, device))

    def features(self, device):
        f = dict()
        if self.check_device(device):
            try:
                f = dict(self.parser.items(section='FEATURES ' + device.upper()))
            except configparser.NoSectionError:
                pass
        return f

    def set_feature(self, device, module, features):
        self.set_features(device, {module: features})

    def set_features(self, device, features):
        features.update(self.features(device))
        if self.check_device(device):
            self.parser['FEATURES ' + device.upper()] = features

    def remove_module(self, device, module):
        if self.check_device(device):
            try:
                del self.parser['FEATURES ' + device.upper()][module]
            except KeyError:
                raise KeyError("(!) Something went wrong: No module %s found for device %s" % (module, device))

    def lock_module(self, device, module):
        features_section = 'FEATURES ' + device.upper()
        if self.check_device(device):
            if module in self.features(device).keys():
                newfile = '.' + module
                self.parser[features_section][newfile] = self.parser[features_section].pop(
                    module)
            else:
                msg = "(!) Something went wrong: No unlocked module %s found for device %s" % (module, device)
                raise KeyError(msg)

    def unlock_module(self, device, module):
        features_section = 'FEATURES ' + device.upper()
        lockfile = '.' + module
        if self.check_device(device):
            if lockfile in self.features(device).keys():
                self.parser[features_section][module] = self.parser[features_section].pop(
                    lockfile)
            else:
                msg = "(!) Something went wrong: No locked module %s found for device %s" % (module, device)
                raise KeyError(msg)

    def update_file(self):
        with open(self.structurefile, 'w') as confFile:
            self.parser.write(confFile)
