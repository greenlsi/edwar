from datetime import datetime

from .loaders import *
from .savers import *
from .parsers import *
from .utils.configuration import Settings
from .utils import configuration


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
    def __init__(self, path, device, **kwargs):
        super().__init__(path, device)
        for k, v in kwargs.items():
            if k == 'settings':  # Optional settings alternative path
                self.settings = v
            elif k == 'loader':  # Optional temporal use of a loader not specified in configuration
                self.loader = v
            else:
                self.parsers.update({k: v})  # Optional temporal use of a parser not specified in configuration

    @staticmethod
    def load(my_settings, my_path, my_device, my_loader=None):
        if my_loader is None:
            try:
                load_method = configuration.get_devices(my_settings)[my_device]
            except KeyError:
                raise KeyError("(!) Device '{}' not found: Run 'edwar.configure.devices()' to configure it".format(
                    my_device))
            else:
                try:
                    my_loader = eval(load_method)
                except NameError:
                    raise NameError("(!) Loader '{}' not found".format(load_method))

        if not issubclass(my_loader, Loader):
            raise TypeError("(!) Something went wrong whith parameter 'loader={}': {} is not a subclass of "
                            "Loader".format(my_loader, my_loader))

        data = my_loader(path=my_path, settings=my_settings).get_data()
        return data

    @staticmethod
    def adapt_output(my_settings, device, data):
        parsers_in_cfg, working_parsers, locked_parsers = configuration.get_output_features(my_settings, device)
        data1 = data.copy()
        for d in data1:
            parser_name = d.parser_name.replace(' ', '').split('(')[0]
            for p in working_parsers.keys():
                if p == parser_name:
                    selected = working_parsers[p].replace(' ', '').split(',')
                    combined = list(set(selected) & set(d.columns))
                    output = d[combined]
                    output.parser_name = d.parser_name
                    data.remove(d)
                    data.append(output)
        return data

    @staticmethod
    def run(my_settings, device, data_in, my_parsers):
        parsers = dict()
        parsers_in_cfg, working_parsers, locked_parsers = configuration.get_output_features(my_settings, device)
        # Check parsers in config file
        for p in working_parsers.keys():
            if p not in parsers.keys():
                try:
                    parsers.update({p: eval(p)})
                except NameError:
                    raise NameError("(!) Parser '{}' not found'.format(p)")

        # Add or substitute parsers passed as parameter
        parsers.update(my_parsers)

        # Check all parsers are subclass of Parser
        for p in parsers.values():
            if not issubclass(p, Parser):
                raise TypeError("(!) Something went wrong whith parser '{}': It is not a subclass of "
                                "Parser".format(p.__name__))

        # Run parsers
        outputs = list()
        for p in parsers.values():
            parser_name = p.__name__
            inputs = list()
            for df in data_in:
                i = [data for data in df.columns if ((data in p().inputs) or (data in p().optional_inputs))]
                if i:
                    inputs.append(df[i])
            output = p().run(inputs)
            if isinstance(output, pd.DataFrame):
                output.parser_name = parser_name
                outputs.append(output)
            elif isinstance(output, list):
                for o in output:
                    if isinstance(o, pd.DataFrame):
                        o.parser_name = parser_name
                        outputs.append(o)
                    else:
                        raise TypeError("(!) Something went wrong whith parser '{}': Expected dataframe or list of "
                                        "dataframes as output".format(parser_name))
            else:
                raise TypeError("(!) Something went wrong whith parser '{}': Expected dataframe or list of "
                                "dataframes as output".format(parser_name))
        return outputs

    def get_output(self):
        self.output = self.adapt_output(self.settings, self.device,
                                        self.run(device=self.device, data_in=self.get_input(),
                                                 my_settings=self.settings, my_parsers=self.parsers))
        return self.output

    def to_csv(self, path):
        now = datetime.now()
        date2 = now.strftime("%Y%m%dT%H%M%S")
        for output in self.get_output():
            columns = output.columns
            col = ''
            for c in columns:
                col += c + '-'
            col = col[:-1]
            date1 = output.index[0].strftime("%Y%m%dT%H%M%S")
            file_name = output.parser_name + '_' + col + '_' + date1 + '_' + date2 + '.csv'
            save_in_csv(path, file_name, output)
        return self.output

    def to_database(self, data_to_db_function=None):
        if data_to_db_function is None:
            data_to_db_function = adapt_features
        for output in self.get_output():
            data = data_to_db_function(output)
            save_in_db(self.settings, data)
        return self.output

    def get_input(self):
        self.input = self.load(my_path=self.path, my_device=self.device, my_loader=self.loader,
                               my_settings=self.settings)
        return self.input
