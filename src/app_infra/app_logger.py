import json
import logging
import traceback
from logging import INFO, ERROR

from loguru import logger


def serialize(record: dict):
    subset = {
        'level': record['level'].name,
        'time': record['time'].strftime('%Y-%m-%d %H:%M:%S %z'),
        'message': record['message'],
        **record.get('extra'),
        'timestamp': record['time'].timestamp(),
        # 'function': record['function'],
        # 'module': record['module'],
        # 'file': record['file'].path,
        'process_id': record['process'].id,
        'process_name': record['process'].name,
        'thread_id': record['thread'].id,
        'thread_name': record['thread'].name,
        'exception': None,
    }
    # if record['exception']:
    #     subset['exception'] = ''.join(traceback.format_exception(
    #         record['exception'].type,
    #         record['exception'].value,
    #         record['exception'].traceback
    #     ))

    return json.dumps(subset, ensure_ascii=False)


def formatter(record: dict):
    record['serialized'] = serialize(record)
    return '{serialized}\n'


def info_filter(record: dict):
    return record['level'].no == INFO


def error_filter(record: dict):
    return record['level'].no >= ERROR


def make_logger():
    # logger.remove()  # removes default handler, but we keep it by commenting this line
    # logger.add('info.log', format=formatter, filter=info_filter, enqueue=True)
    # logger.add('error.log', format=formatter, filter=error_filter, enqueue=True)
    logging.getLogger('passlib').setLevel(logging.ERROR)  # todo: this is a dirty code to remove passlib wrong error
    logger.add('logs/api.log', format=formatter, enqueue=True)


def get_logger():
    return logger
