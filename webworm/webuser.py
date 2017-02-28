# -*- coding: utf-8 -*-
import logging
import logging.config
from functools import reduce

LOG_FILE = 'log.cfg'
with open(LOG_FILE, encoding='utf-8') as fp:
    logging.config.fileConfig(fp)
debug_logger = logging.getLogger('debug.webuser')
info_logger = logging.getLogger('info.webuser')
warn_logger = logging.getLogger('warn.webuser')
error_logger = logging.getLogger('error.webuser')
critical_logger = logging.getLogger('critical.webuser')


def url_generator(start_url):
    yield start_url


class DefaultContentsDispatcher(object):

    def __init__(self):
        pass

    def __call__(self, page_spider):
        pass


class StoreInDataBase(object):

    def __init__(self, db, table_name, items):
        self.db = db
        self.table_name = table_name
        self.items = items

    def __call__(self, *data_to_dispatch):
        data_to_store = {}
        try:
            for index, data in enumerate(*data_to_dispatch):
                if data['specified_contents'] == '':
                    data_get = data['contexts']
                elif data['specified_contents'].startswith('@'):
                    data_get = data['attributes']
                elif data['specified_contents'] == 'text()':
                    data_get = data['text']
                else:
                    data_get = data['tags']
                data_to_store[self.items[index]] = self.list2str(data_get)
            self.db.insert_table(self.table_name, *self.items, **data_to_store)
        except Exception as e:
            error_logger.error(
                'Failed to store data: {} into table "{}" since: {}'. format(
                    data_to_store, self.table_name, e))

    @staticmethod
    def list2str(data_list):
        result = ''
        for data in data_list:
            result = result + reduce(lambda x, y: x + ' ; ' + y, data) + '\n'
        return result.strip('\n')
