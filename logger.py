import logging

def __get_logger():
    __logger = logging.getLogger('logger')
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler('./error.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)
    __logger.addHandler(stream_handler)
    __logger.setLevel(logging.INFO)
    return __logger