class Error(Exception):
    def __init__(self, msg=''):
        self.message = msg
        super().__init__(self, msg)

    def __str__(self):
        return self.message


class StructureFileNotFoundError(Error):
    """Raised when no structure.ini file is found."""

    def __init__(self, structure_file):
        Error.__init__(self, "No structure description file {} found. ".format(structure_file) +
                             "Run edwar.install.structure_cfg() first.")


class DatabaseFileNotFoundError(Error):
    """Raised when no database.ini file is found."""

    def __init__(self, database_file):
        Error.__init__(self, "No database configuration file {} found. ".format(database_file) +
                             "Run edwar.install.database_cfg() first.")


class PasswordError(Error):
    """Raised when database.ini decryption fails."""

    def __init__(self, database_file):
        Error.__init__(self, "Database configuration file {} could not be correctly decrypted.".format(database_file))


class DatabaseError(Error):
    """Raised when connection to database gives an error."""

    def __init__(self, msg):
        Error.__init__(self, msg)


class DatabaseLoginError(DatabaseError):
    def __init__(self):
        DatabaseError("Connection to database failed: wrong user or password.")


class DatabaseConnectionError(DatabaseError):
    def __init__(self):
        DatabaseError("Connection to database failed.")


class DeviceNotFoundError(Error):
    """Raised when no configuration for a given device is found."""

    def __init__(self, device):
        Error.__init__(self, "No device {} configured found. ".format(device) +
                             "Run edwar.configure.devices() first.")
        self.device = device


class DeviceConfigurationError(Error):
    """Raised when configuration for a given device is not well implemented."""

    def __init__(self, msg):
        Error.__init__(self, msg)


class DeviceFileNotFoundError(DeviceConfigurationError):
    def __init__(self, file):
        msg = "Data file {} not found".format(file)
        DeviceConfigurationError.__init__(self, msg)


class SeveralFilesFoundError(DeviceConfigurationError):
    def __init__(self, search, found):
        msg = "Loader searchs file *{}*, but {} found.".format(search, found)
        DeviceConfigurationError.__init__(self, msg)
        self.search = '*' + search + '*'
        self.found = found


class MissingInputDataError(DeviceConfigurationError):
    def __init__(self, parser, miss_data, needed_data):
        msg = "Parser {} needs as input data {} but {} is missing.".format(parser, miss_data, needed_data)
        DeviceConfigurationError.__init__(self, msg)


class MissingOutputDataError(DeviceConfigurationError):
    def __init__(self, parser, miss_data, needed_data):
        msg = "Output expected from parser {} is {} but got {}.".format(parser, needed_data, miss_data)
        DeviceConfigurationError.__init__(self, msg)


class NoOutputDataError(DeviceConfigurationError):
    def __init__(self):
        msg = "No output data to return"
        DeviceConfigurationError.__init__(self, msg)


class FileFormatError(Error):
    """Raised when no configuration for a given device is found."""

    def __init__(self, file, expected_format, error):
        msg = "File {} has not the expected format ({}): {}".format(file, expected_format, error)
        Error.__init__(self, msg)


class WrongImplementationError(Error):
    """Raised when code is not well implemented."""

    def __init__(self, msg):
        Error.__init__(self, msg)


class SubclassError(WrongImplementationError):
    def __init__(self, class_used, subclass):
        msg = "{} is not a subclass of {}".format(class_used, subclass)
        WrongImplementationError.__init__(self, msg)
        self.class_used = class_used
        self.subclass = subclass


class CodeImportedError(WrongImplementationError):
    def __init__(self, code_import):
        msg = "{} not found".format(code_import)
        WrongImplementationError.__init__(self, msg)
        self.code_import = code_import
