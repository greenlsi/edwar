import os
import logging


def setup_logger(logger_name, log_directory, level=logging.DEBUG):
    """
    :param logger_name:
    :param log_directory:
    :param level:
    :return:
    """
    log = logging.getLogger(logger_name)
    formatter_file = logging.Formatter('%(levelname)s : %(asctime)s : %(message)s')
    formatter_stream = logging.Formatter('%(name)s : %(levelname)s : %(message)s')

    log.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter_stream)
    log.addHandler(stream_handler)

    if log_directory:
        if not os.path.exists(log_directory):
            os.mkdir(log_directory)
        log_file = os.path.join(log_directory, logger_name + '.LOG')
        log.addHandler(stream_handler)
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setFormatter(formatter_file)
        log.addHandler(file_handler)
