import configparser
import os
import io
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class Structure:
    def __init__(self, settings):
        self.parser = configparser.ConfigParser(inline_comment_prefixes="#", allow_no_value=True)
        self.parser.optionxform = str
        self.structurefile = os.path.join(settings.path, settings.structureini)
        ok = self.parser.read(self.structurefile)
        if not ok:
            raise FileNotFoundError("Configuration file {} found. ".format(settings.structureini) +
                                    "Run edwar.configure.devices() to create it")
        try:
            self._devices = dict(self.parser.items(section='DEVICES'))
        except configparser.NoSectionError:
            self.parser.add_section('DEVICES')
            self._devices = dict()

    def devices(self):
        return self._devices

    def set_device(self, device, load_function):
        self.parser.set('DEVICES', device, load_function)
        self._devices[device] = load_function

    def remove_device(self, device):
        try:
            self.check_device(device)
        except KeyError:
            pass
        else:
            del self._devices[device]
            self.parser.remove_option('DEVICES', device)
            self.parser.remove_section('VARIABLES ' + device.upper())  # Nothing happens if no section
            self.parser.remove_section('FEATURES ' + device.upper())

    def check_device(self, device):
        if device in self.devices().keys():
            return 1
        raise KeyError("No device %s found" % device)

    def variables(self, device):
        v = dict()
        if self.check_device(device):
            try:
                v = dict(self.parser.items(section='VARIABLES ' + device.upper()))
            except configparser.NoSectionError:
                self.parser.add_section('VARIABLES ' + device.upper())
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
                pass

    def remove_all_files(self, device):
        if self.check_device(device):
            try:
                self.parser.remove_section('VARIABLES ' + device.upper())
            except configparser.NoSectionError:
                pass

    def lock_file(self, device, file):
        if self.check_device(device):
            if file in self.variables(device).keys():
                newfile = '.' + file
                self.parser['VARIABLES ' + device.upper()][newfile] = self.parser['VARIABLES ' + device.upper()].pop(
                    file)
            else:
                raise KeyError("No unlocked file %s found for device %s" % (file, device))

    def unlock_file(self, device, file):
        lockfile = '.' + file
        if self.check_device(device):
            if lockfile in self.variables(device).keys():
                self.parser['VARIABLES ' + device.upper()][file] = self.parser['VARIABLES ' + device.upper()].pop(
                    lockfile)
            else:
                raise KeyError("No locked file %s found for device %s" % (file, device))

    def features(self, device):
        f = dict()
        if self.check_device(device):
            try:
                f = dict(self.parser.items(section='FEATURES ' + device.upper()))
            except configparser.NoSectionError:
                self.parser.add_section('FEATURES ' + device.upper())
        return f

    def set_feature(self, device, module, features):
        self.set_features(device, {module: features})

    def set_features(self, device, features):
        features.update(self.features(device))
        if self.check_device(device):
            self.parser['FEATURES ' + device.upper()] = features

    def remove_parser(self, device, module):
        if self.check_device(device):
            try:
                del self.parser['FEATURES ' + device.upper()][module]
            except KeyError:
                pass

    def remove_all_parsers(self, device):
        if self.check_device(device):
            try:
                self.parser.remove_section('FEATURES ' + device.upper())
            except configparser.NoSectionError:
                pass

    def lock_module(self, device, module):  # TODO: change raise error to warning log
        features_section = 'FEATURES ' + device.upper()
        if self.check_device(device):
            if module in self.features(device).keys():
                newfile = '.' + module
                self.parser[features_section][newfile] = self.parser[features_section].pop(
                    module)
            else:
                msg = "No unlocked module %s found for device %s" % (module, device)
                raise KeyError(msg)

    def unlock_module(self, device, module):  # TODO: same as upper
        features_section = 'FEATURES ' + device.upper()
        lockmodule = '.' + module
        if self.check_device(device):
            if lockmodule in self.features(device).keys():
                self.parser[features_section][module] = self.parser[features_section].pop(lockmodule)
            else:
                msg = "No locked module %s found for device %s" % (module, device)
                raise KeyError(msg)

    def update_file(self):
        with open(self.structurefile, 'w') as confFile:
            self.parser.write(confFile)


class DataBase:
    def __init__(self, settings, password):
        self.parser = configparser.ConfigParser(inline_comment_prefixes="#", allow_no_value=True)
        self.parser.optionxform = str
        self.databasefile = os.path.join(settings.path, settings.databaseini)
        self.password = self.complete_password(password)

        with open(self.databasefile, 'r') as confFile:
            ciphertext = confFile.read()

        try:
            text = AESCipher(self.password).decrypt(ciphertext)
        except UnicodeDecodeError:
            raise KeyError('Wrong password. Unable to read {}'.format(settings.databaseini))
        self.parser.read_string(text)

        try:
            self._db = dict(self.parser.items(section='DB'))
        except configparser.NoSectionError:
            raise KeyError('Incorrect syntax of {} file. Decryption must be wrong.'.format(settings.databaseini))

    def host(self):
        try:
            host = self.parser.get('DB', 'Host')
        except configparser.NoOptionError:
            host = ''
        try:
            port = self.parser.get('DB', 'Port')
        except configparser.NoOptionError:
            port = ''
        return host, port

    def set_host(self, host, port):
        self.parser.set('DB', 'Host', host)
        self.parser.set('DB', 'Port', port)

    def user(self):
        try:
            user = self.parser.get('DB', 'User')
        except configparser.NoOptionError:
            user = ''
        try:
            pwd = self.parser.get('DB', 'Password')
        except configparser.NoOptionError:
            pwd = ''
        return user, pwd

    def set_user(self, user, pwd):
        self.parser.set('DB', 'User', user)
        self.parser.set('DB', 'Password', pwd)

    def database(self):
        try:
            database = self.parser.get('DB', 'DB_name')
        except configparser.NoOptionError:
            database = ''
        return database

    def set_database(self, database):
        self.parser.set('DB', 'DB_name', database)

    def table(self):
        try:
            table = self.parser.get('DB', 'Tb_name')
        except configparser.NoOptionError:
            table = ''
        return table

    def set_table(self, table):
        self.parser.set('DB', 'Tb_name', table)

    def update_file(self):
        user, pw = self.user()
        pw = self.complete_password(pw) if pw else self.password
        buf = io.StringIO("")
        self.parser.write(buf)
        text = buf.getvalue()
        ciphertext = AESCipher(pw).encrypt(text)
        with open(self.databasefile, 'w') as confFile:
            confFile.write(ciphertext.decode('UTF-8'))
        confFile.close()

    @staticmethod
    def complete_password(pwd):
        if not isinstance(pwd, str):
            raise TypeError('Password must be a string with between 8 and 16 characters')
        default = '0123456789abcdef'
        filled = len(pwd) if len(pwd) <= 16 else 16
        full_password = pwd[0:15] + default[0:16-filled]
        return full_password


class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
