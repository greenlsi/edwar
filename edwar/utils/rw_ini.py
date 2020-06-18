import os
import io
import base64
import hashlib
import logging
import configparser
from Crypto import Random
from Crypto.Cipher import AES

from ..errors import *


class Settings:
    def __init__(self, path: str = None, databaseini: str = None, structureini: str = None, log_path: str = None):
        self.path = path if path else '.cfg_edwar'
        self.databaseini = databaseini if databaseini else 'database.ini'
        self.structureini = structureini if structureini else 'structure.ini'
        self.log_path = log_path if log_path else '.log'


class Structure:
    def __init__(self, settings):
        self.parser = configparser.ConfigParser(inline_comment_prefixes="#", allow_no_value=True)
        self.parser.optionxform = str
        self.structurefile = os.path.join(settings.path, settings.structureini)
        ok = self.parser.read(self.structurefile)
        self.log = logging.getLogger('EDWAR')
        if not ok:
            self.log.critical("No structure description file '{}' found.".format(settings.structureini))
            raise StructureFileNotFoundError(settings.structureini)
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
        self.log.critical("No device '{}' configured found.".format(device))
        raise DeviceNotFoundError(device)

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
            newfile = '.' + file
            if file in self.variables(device).keys():
                self.parser['VARIABLES ' + device.upper()][newfile] = self.parser['VARIABLES ' + device.upper()].pop(
                    file)
                self.log.info("File '{}' locked.".format(file))
            elif newfile in self.variables(device).keys():
                self.log.info("File '{}' was already locked.".format(file))
            else:
                self.log.warning("No file '{}' found for device {}.".format(file, device))

    def unlock_file(self, device, file):
        lockfile = '.' + file
        if self.check_device(device):
            if lockfile in self.variables(device).keys():
                self.parser['VARIABLES ' + device.upper()][file] = self.parser['VARIABLES ' + device.upper()].pop(
                    lockfile)
                self.log.info("File '{}' unlocked.".format(file))
            elif file in self.variables(device).keys():
                self.log.info("File '{}' was already unlocked.".format(file))
            else:
                self.log.warning("No {} data file '{}' found.".format(device, file))

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

    def lock_module(self, device, module):
        features_section = 'FEATURES ' + device.upper()
        if self.check_device(device):
            newmodule = '.' + module
            if module in self.features(device).keys():
                self.parser[features_section][newmodule] = self.parser[features_section].pop(
                    module)
                self.log.info("Parser '{}' locked.")
            elif newmodule in self.features(device).keys():
                self.log.info("Parser '{}' was already locked.")
            else:
                self.log.warning("No {} data parser '{}' found.".format(device, module))

    def unlock_module(self, device, module):
        features_section = 'FEATURES ' + device.upper()
        lockmodule = '.' + module
        if self.check_device(device):
            if lockmodule in self.features(device).keys():
                self.parser[features_section][module] = self.parser[features_section].pop(lockmodule)
                self.log.info("Parser '{}' unlocked.")
            elif lockmodule in self.features(device).keys():
                self.log.info("Parser '{}' was already unlocked.")
            else:
                self.log.warning("No {} data parser '{}' found.".format(device, module))

    def update_file(self):
        with open(self.structurefile, 'w') as confFile:
            self.parser.write(confFile)


class DataBase:
    def __init__(self, settings, password):
        self.parser = configparser.ConfigParser(inline_comment_prefixes="#", allow_no_value=True)
        self.parser.optionxform = str
        self.databasefile = os.path.join(settings.path, settings.databaseini)
        self.password = self.complete_password(password)
        self.log = logging.getLogger('EDWAR')

        try:
            with open(self.databasefile, 'r') as confFile:
                ciphertext = confFile.read()
            text = AESCipher(self.password).decrypt(ciphertext)
        except FileNotFoundError:
            self.log.critical("No database configuration file '{}' found.".format(settings.databaseini))
            raise DatabaseFileNotFoundError(settings.databaseini)
        except UnicodeDecodeError:
            raise PasswordError(settings.databaseini)
        self.parser.read_string(text)

        try:
            self._db = dict(self.parser.items(section='DB'))
        except configparser.NoSectionError:
            raise PasswordError(settings.databaseini)

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
    def complete_password(pwd: str):
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
