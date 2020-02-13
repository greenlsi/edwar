import logging
from datetime import datetime

from .loaders import *
from .savers import *
from .parsers import *
from .utils import Settings
from .utils import configuration
from .utils.user_input import check_answer
from .utils.logs import setup_logger
from .errors import *


class AbstractRun(ABC):
    def __init__(self, path, device, settings=None):
        # Configurable settings & platform structure
        self.path = path
        self.device = device
        self.settings = settings if settings else Settings()
        self.loader = None
        self.parsers = dict()
        # Non configurable
        self.input = None
        self.output = None
        super().__init__()

    @abstractmethod
    def get_output(self):
        pass


class Run(AbstractRun):
    def __init__(self, path: str, device: str, logs_path: str = None, **kwargs):
        super().__init__(path, device)
        for k, v in kwargs.items():
            if k == 'settings':  # Optional settings alternative path
                self.settings = v
            elif k == 'loader':  # Optional temporal use of a loader not specified in configuration
                self.loader = v
            else:
                self.parsers.update({k: v})  # Optional temporal use of a parser not specified in configuration

        # LOGS: one for how the platform is working and other for data and its process
        setup_logger('EDWAR', log_directory=logs_path)

    @staticmethod
    def load(my_settings: classmethod, my_path: str, my_device: str, my_loader: classmethod = None) \
            -> 'list of input dataframes':

        log = logging.getLogger('EDWAR')
        if my_loader is None:
            try:  # search for the device
                load_method = configuration.get_devices(my_settings)[my_device]
            except KeyError:
                log.critical("No device {} configured found.".format(my_device))
                raise DeviceNotFoundError(my_device)
            else:  # try to find its loader
                try:
                    my_loader = eval(load_method)
                except NameError:
                    log.critical("Loader {} not found. ".format(load_method))
                    raise CodeImportedError(load_method)

        # check loader is well implemented
        if not issubclass(my_loader, Loader):
            log.critical("Loader {} is not a subclass of {}.".format(my_loader.__name__, Loader.__name__))
            raise SubclassError(my_loader.__name__, Loader.__name__)
        else:
            log.info("Loader {} of {} data successfully selected.".format(my_loader.__name__, my_device))

        data = my_loader(path=my_path, settings=my_settings).get_data()
        return data

    @staticmethod
    def run(my_settings: classmethod, device: str, data_in: list, my_parsers: dict):
        log = logging.getLogger('EDWAR')
        parsers = dict()
        parsers_in_cfg, working_parsers, locked_parsers = configuration.get_output_features(my_settings, device)
        # Check parsers in config file
        for p in working_parsers.keys():
            if p not in parsers.keys():
                try:
                    parsers.update({p: eval(p)})
                except NameError:
                    log.error('Parser {} not found.'.format(p))
                    # raise CodeImportedError(p)

        # Add or substitute parsers passed as parameter
        parsers.update(my_parsers)

        # Check all parsers are subclass of Parser
        for p in parsers.keys():
            if not issubclass(parsers[p], Parser):
                log.error("Parser {} is not a subclass of {}, so it can not be used.".format(p, Parser.__name__))
                del parsers[p]
                # raise SubclassError(p, Parser.__name__)
            else:
                log.info("Parser {} successfully selected.".format(p))

        # Run parsers
        outputs = list()
        for p in parsers.values():
            parser_name = p.__name__
            inputs = list()
            for df in data_in:
                i = [data for data in df.columns if ((data in p().inputs) or (data in p().optional_inputs))]
                if i:
                    inputs.append(df[i])
            log.info("Executing parser {}.".format(parser_name))
            try:
                output = p().run(inputs)
            except Exception as err:
                log.error('Parser {} unexpected error: {}'.format(parser_name, err))
            else:
                if isinstance(output, pd.DataFrame):
                    output.parser_name = parser_name
                    outputs.append(output)
                    log.info("Parser {} results ready".format(parser_name))
                elif isinstance(output, list):
                    n = 0
                    for o in output:
                        n += 1
                        if isinstance(o, pd.DataFrame):
                            o.parser_name = parser_name
                            outputs.append(o)
                            log.info("Parser {} result {} ready".format(parser_name, n))
                        else:
                            log.error("Unexpected output {} from {}, expected a dataframe.".format(parser_name, n))
                else:
                    log.error("Unexpected output from {}, expected a dataframe.".format(parser_name))

        if not outputs:
            raise NoOutputDataError()
        return outputs

    @staticmethod
    def adapt_output(my_settings: classmethod, device: str, data: list):
        log = logging.getLogger('EDWAR')
        parsers_in_cfg, working_parsers, locked_parsers = configuration.get_output_features(my_settings, device)
        data1 = data.copy()
        expected_return = dict()  # all parsers and the output they must return
        not_returned = dict()  # all parsers and the output they not returned
        for w in working_parsers.keys():
            expected_return[w] = not_returned[w] = working_parsers[w].replace(' ', '').split(',')
        for d in data1:
            for p in expected_return.keys():
                if p == d.parser_name:
                    data.remove(d)
                    selected = working_parsers[p]
                    if '*' in selected:
                        combined = list(d.columns)
                    else:
                        combined = [col for col in d.columns if col in selected]
                        # list all expected outputs not returned yet
                        not_returned[p] = [x for x in not_returned[p] if x not in combined]
                    if combined:
                        output = d[combined]
                        output.parser_name = d.parser_name
                        data.append(output)
        for n in not_returned.keys():
            if not_returned[n]:
                log.warning('Expected output {} from parser {} not found.'.format(not_returned[n], n))
        return data

    def get_output(self):
        data_in = self.get_input()
        data_out = self.run(device=self.device, data_in=data_in, my_settings=self.settings, my_parsers=self.parsers)
        self.output = self.adapt_output(self.settings, self.device, data_out)
        return self.output

    def to_csv(self, path: str):
        log = logging.getLogger('EDWAR')
        now = datetime.now()
        date2 = now.strftime("%Y%m%dT%H%M%S")
        outputs = self.get_output()
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except Exception as err:
                log.error("Save directory {} not found. New {} could not be created: {}".format(path, path, err))
                return self.output
            else:
                log.info("Save directory {} not found. New {} created".format(path, path))

        for output in outputs:
            columns = output.columns
            col = ''
            for c in columns:
                col += c + '-'
            col = col[:-1]
            date1 = output.index[0].strftime("%Y%m%dT%H%M%S")
            file_name = output.parser_name + '_' + col + '_' + date1 + '_' + date2 + '.csv'
            try:
                save_in_csv(path, file_name, output)
            except Exception as err:
                log.error('Unexpected error saving output data {}: {}.'.format(col, err))
            else:
                log.info('Output data {} ready in {}.'.format(col, path))
        return self.output

    def to_database(self, data_to_db_function: callable = None):
        log = logging.getLogger('EDWAR')
        pw = check_answer("Password of database: ", password=True)
        configuration.check_password(self.settings, pw)
        if data_to_db_function is None:
            data_to_db_function = adapt_features
        for output in self.get_output():
            try:
                data = data_to_db_function(output)
                save_in_db(self.settings, data, pw)
            except Exception as err:
                log.error('Unexpected error uploading to database output data {} from parser {}: {}.'.format(
                    list(output.columns), output.parser_name, err))
            else:
                log.info('Output data {} from parser {} already updated to database'.format(list(output.columns),
                                                                                            output.parser_name))
        return self.output

    def get_input(self):
        self.input = self.load(my_path=self.path, my_device=self.device, my_loader=self.loader,
                               my_settings=self.settings)
        return self.input
