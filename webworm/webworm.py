# -*- coding: utf-8 -*-
import logging
import logging.config
import sqlite3
import sys
import os
import io
import re
import types
import copy
import threading
from urllib import request, parse
try:
    from bs4 import BeautifulSoup, element
except ImportError:
    BeautifulSoup = None
    element = None
    sys.exit(2)


__author__ = 'Tangxing Zhou'
__status__ = 'production'
__version__ = '2.0.1'
__date__ = '14th Aug. 2016'


with open('log.cfg', encoding='utf-8') as fp:
    logging.config.fileConfig(fp)
debug_logger = logging.getLogger('debug.webworm')
info_logger = logging.getLogger('info.webworm')
warn_logger = logging.getLogger('warn.webworm')
error_logger = logging.getLogger('error.webworm')
critical_logger = logging.getLogger('critical.webworm')


class DBWrapper(object):

    def __init__(self):
        pass

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            args[0].threads_lock.acquire()
            if 'connect' not in kwargs or not isinstance(kwargs['connect'], sqlite3.Connection):
                kwargs['connect'] = args[0].connect_db()
            else:
                pass
            response = func(*args, **kwargs)
            args[0].close_db(kwargs['connect'])
            args[0].threads_lock.release()
            return response
        return wrapper


class SqlDB(object):

    def __init__(self, db_name):
        self._db_name = db_name
        self.threads_lock = threading.RLock()

    def connect_db(self):
        connect = sqlite3.connect(self._db_name)
        connect.text_factory = str
        return connect

    @staticmethod
    def close_db(connect=None):
        if isinstance(connect, sqlite3.Connection):
            connect.close()
        else:
            return

    @staticmethod
    def generate_insert_command(table_name, *items, **insert_info):
        values = []
        for item in items:
            if item in insert_info:
                values.append(insert_info[item])
            else:
                values.append('')
        values = tuple(values)
        values_format = '?,'*len(items)
        values_format = '(' + values_format[:-1] + ')'
        command = ('INSERT INTO ' + table_name + ' VALUES' + values_format, values)
        debug_logger.debug('Generate the insert command: {} of SQLite3'.format(command))
        return command

    @DBWrapper()
    def execute(self, *command, **kwargs):
        result = True
        if 'connect' in kwargs and isinstance(kwargs['connect'], sqlite3.Connection):
            connect = kwargs['connect']
        else:
            connect = self.connect_db()
        debug_logger.debug('Try to run the command: {} of SQLite3'.format(command))
        try:
            cursor = connect.cursor()
            cursor.execute(*command)
            cursor.close()
            connect.commit()
        except Exception as e:
            error_logger.error('Failed to run the command: {} since {}'.format(command, e))
            result = False
        return result

    def create_table(self, table_name, item_attributes=tuple(), connect=None, *items):
        prefix = 'CREATE TABLE IF NOT EXISTS '
        table_items = ''
        if item_attributes is tuple():
            table_items = '(' + ' TEXT, '.join(items) + ' TEXT' + ')'
        else:
            if len(item_attributes) is not len(items):
                error_logger.error('In data base: {} of table: {} items: {} and attributes: {} are not corresponding'
                                   .format(self._db_name, table_name, items, item_attributes))
                raise ValueError('In data base: {} of table: {} items: {} and attributes: {} are not corresponding'
                                 .format(self._db_name, table_name, items, item_attributes))
            else:
                for index, item in enumerate(items):
                    table_items += item + ' ' + item_attributes[index] + ','
                table_items = '(' + table_items[:-1] + ')'
        command = (prefix + table_name + ' ' + table_items,)
        debug_logger.debug('Table "{}" will be created by the command: {}'.format(table_name, command))
        return self.execute(*command, connect=connect)

    def insert_table(self, table_name, *items, **values):
        command = self.generate_insert_command(table_name, *items, **values)
        debug_logger.debug('{} will be inserted into table "{}" by the command: {}'.format(values, table_name, command))
        return self.execute(*command)

    @DBWrapper()
    def fetchall(self, *command, **kwargs):
        if 'connect' in kwargs and isinstance(kwargs['connect'], sqlite3.Connection):
            connect = kwargs['connect']
        else:
            connect = self.connect_db()
        try:
            cursor = connect.cursor()
            cursor.execute(*command)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            error_logger.error('Failed to fetchall with the command: {} since {}'.format(command, e))
            result = []
        debug_logger.debug('Result {} is got by the command: {}'.format(result, command))
        return result


class PageSpider(object):

    def __init__(self):
        self._page_url = ''
        self._soup = None
        self.tags = list()
        self.xpath = list()
        self.specified_contents = ''
        self._flag_all = False
        self.text = list()
        self.attributes = list()
        self.contexts = list()

    @staticmethod
    def request_page(page_url, request_header=None, data=None):
        if request_header is not None:
            if not isinstance(request_header, dict):
                error_logger.error('The request header {} must be a dict'.format(request_header))
                raise TypeError('The request header {} must be a dict'.format(request_header))
            else:
                debug_logger.debug('The request header is {}'.format(request_header))
        else:
            request_header = {}
        if data is None:
            post_data = None
        else:
            if isinstance(data, dict):
                debug_logger.debug('The request is with the data{}'.format(data))
                if data is {}:
                    post_data = None
                else:
                    post_data = parse.urlencode(data)
            else:
                error_logger.error('The data {} for the request must be a dict'.format(data))
                raise TypeError('The data {} for the request must be a dict'.format(data))
        try:
            req = request.Request(page_url, headers=request_header)
            response = request.urlopen(req, data=post_data)
        except Exception as e:
            error_logger.error('Failed to request the url: "{}" {}'.format(page_url, e))
            return {}
        response_headers = response.getheaders()
        response_header = {}
        html_content = ''
        for item in response_headers:
            if len(item) is 1:
                response_header[item[0]] = None
            elif len(item) is 2:
                response_header[item[0]] = item[1]
            else:
                continue
        if 'Content-Encoding' in response_header and response_header['Content-Encoding'] is 'gzip':
            try:
                import gzip
                buf = io.BytesIO(response.read())
                unzip_buf = gzip.GzipFile(fileobj=buf)
                html_content = unzip_buf.read().decode()
            except Exception as e:
                error_logger.error('Unknown Exception: {}'.format(e))
            info_logger.info('The response header indicates that the response body is encoded by gzip')
        else:
            html_content = response.read().decode()
        return {'header': response_header, 'body': html_content}

    def spider_page(self, page_url, **kwargs):
        if 'header' in kwargs:
            header = kwargs['header']
        else:
            header = {}
        if 'data' in kwargs:
            data = kwargs['data']
        else:
            data = None
        soup = None
        try:
            info_logger.info('Start to request the page with the url: {}'.format(page_url))
            body = PageSpider.request_page(page_url, request_header=header, data=data)['body']
            info_logger.info('Convert the response body to BeautifulSoup instance')
            soup = BeautifulSoup(body, 'lxml')
        except Exception as e:
            error_logger.error('Failed to generate BeautifulSoup instance: {}'.format(e))
        finally:
            self._page_url = page_url
            self._soup = soup
            return soup

    def init_for_next_xpath(self):
        self.tags = list()
        self.xpath = list()
        self.specified_contents = ''
        self._flag_all = False
        self.text = list()
        self.attributes = list()
        self.contexts = list()

    def parse_xpath_of_tag(self, xpath=''):
        self.xpath = list()
        self.specified_contents = ''
        self._flag_all = False
        info_logger.info('Start to parse the xpath: "{}"'.format(xpath))
        path_list = xpath.split('/')
        debug_logger.debug('Split "{}" into {} by "/"'.format(xpath, path_list))
        if len(path_list) < 2 or xpath.endswith('/'):
            error_logger.error('"{}" is not a correct xpath'.format(xpath))
        else:
            try:
                if path_list[1:].index('') > 0:
                    error_logger.error('"{}" is not a correct xpath'.format(xpath))
                    return
                elif path_list[1:].index('') is 0:
                    self._flag_all = True
            except ValueError:
                info_logger.info("'' is not in {}".format(path_list[1:]))
            except Exception as e:
                critical_logger.critical('Unknown Exception: {}'.format(e))
            for path in path_list[1:]:
                if path == '':
                    continue
                elif path == 'text()' or path.startswith('@'):
                    debug_logger.debug('Parse the path: "{}"'.format(path))
                    self.specified_contents = path
                else:
                    debug_logger.debug('Parse the path: "{}"'.format(path))
                    tag_info_list = re.split('[\[@,\]]+', path)
                    debug_logger.debug('Split "{}" into {}'.format(path, tag_info_list))
                    tag_name = tag_info_list[0].strip()
                    if len(tag_info_list) is 1:
                        append_tag_info = {tag_name: {}}
                    else:
                        attr_dict = {}
                        for attr in tag_info_list[1:-1]:
                            attr = attr.strip()
                            debug_logger.debug('Parse the attribute: "{}" of {}'.format(attr, tag_info_list))
                            if re.match(r'\w+="[\w\s-]+"', attr) is None:
                                warn_logger.warn('"{}" is not the correct format for attribute of a tag'.format(attr))
                                continue
                            else:
                                attr_list = re.split('[="]+', attr)
                                debug_logger.debug('Split "{}" into {}'.format(attr, attr_list))
                            attr_dict[attr_list[0]] = attr_list[1]
                            debug_logger.debug('Convert "{}" to {}'.format(attr, attr_dict))
                        append_tag_info = {tag_name: attr_dict}
                    self.xpath.append(append_tag_info)
                    debug_logger.debug('Path "{}" is parsed to {}'.format(path, append_tag_info))
            debug_logger.debug('Xpath "{}" is parsed to {}'.format(xpath, self.xpath))

    def get_specified_elements(self):
        self.text = list()
        self.attributes = list()
        self.contexts = list()
        for tag_set in self.tags:
            if self.specified_contents == 'text()':
                self.text.append([])
            elif self.specified_contents.startswith('@'):
                self.attributes.append([])
            else:
                self.contexts.append([])
            for tag in tag_set:
                if self.specified_contents == 'text()':
                    self.text[-1].append(PageSpider.get_text(tag))
                    debug_logger.debug('Get the text: {}'.format(self.text))
                elif self.specified_contents.startswith('@'):
                    if self.specified_contents == '@':
                        attr_select = tuple()
                    else:
                        attr_select = tuple(re.split('[@,]+', self.specified_contents)[1:])
                    self.attributes[-1].append(PageSpider.get_attributes(tag, *attr_select))
                    debug_logger.debug('Get the attributes: {}'.format(self.attributes))
                else:
                    self.contexts[-1].append(PageSpider.get_contexts(tag))
                    debug_logger.debug('Get the contents: {}'.format(self.contexts))

    def find_tag(self, tags, *tag_info):
        one_element_length = 1
        first_elem_index = 0
        if isinstance(tags, element.Tag):
            tags = [tags]
        elif isinstance(tags, element.ResultSet):
            pass
        else:
            error_logger.error('{} is not an instance of element.Tag or element.ResultSet'.format(type(tags)))
            raise TypeError('{} is not an instance of element.Tag or element.ResultSet'.format(type(tags)))
        if len(tag_info) is 0:
            error_logger.error('{} has no information of the tag'.format(tag_info))
            raise ValueError('{} has no information of the tag'.format(tag_info))
        else:
            pass
        for tag in tags:
            if self._flag_all is False and len(self.tags) is one_element_length:
                info_logger.info('One tag is found ends.')
                return
            else:
                pass
            if isinstance(tag, element.Tag):
                info = tag_info[first_elem_index]
                debug_logger.debug('Search {} in {}'.format(info, tag_info))
                if isinstance(info, dict) and len(info) is one_element_length \
                        and isinstance(tuple(info.values())[first_elem_index], dict):
                    tag_name = tuple(info.keys())[first_elem_index]
                    tag_attributes = tuple(info.values())[first_elem_index]
                    tag_found = tag.find_all(tag_name, tag_attributes)
                    debug_logger.debug('Tag name is "{}", attributes are {}'.format(tag_name, tag_attributes))
                    if tag_found == list():
                        warn_logger.warn('{} is not found'.format(info))
                        continue
                    else:
                        if len(tag_info) is one_element_length:
                            self.tags.append(tag_found)
                            info_logger.info('Tags {} are found'.format(self.tags))
                        else:
                            new_tag_info = tag_info[first_elem_index+1:]
                            self.find_tag(tag_found, *tuple(new_tag_info))
                else:
                    error_logger.error('{} value is wrong'.format(info))
                    raise ValueError('{} value is wrong'.format(info))
            else:
                error_logger.error('{} is not an instance of element.Tag'.format(type(tag)))
                raise TypeError('{} is not an instance of element.Tag'.format(type(tag)))

    @staticmethod
    def get_attributes(tag, *attr_key):
        if not isinstance(tag, element.Tag):
            error_logger.error('{} is not an instance of element.Tag'.format(type(tag)))
            raise TypeError('{} is not an instance of element.Tag'.format(type(tag)))
        else:
            pass
        name = ''
        try:
            name = tag.name
            attributes = tag.attrs
        except Exception as e:
            error_logger.error('Failed to get the attributes of tag "{}" : {}'.format(name, e))
            return {}
        attributes_select = {}
        for key in attr_key:
            if key in attributes:
                attributes_select[key] = attributes[key]
            else:
                warn_logger.warn('"{}" is not the attribute of tag "{}"'.format(key, name))
        if len(attr_key) is 0:
            debug_logger.debug('The attributes of tag "{}" are {}'.format(name, attributes))
            return attributes
        else:
            debug_logger.debug('The specified attributes of tag "{}" are {} with the names {}'.
                               format(name, attributes, attr_key))
            return attributes_select

    @staticmethod
    def get_text(tag):
        if not isinstance(tag, element.Tag):
            error_logger.error('{} is not an instance of element.Tag'.format(type(tag)))
            raise TypeError('{} is not an instance of element.Tag'.format(type(tag)))
        else:
            pass
        name = ''
        text = ''
        try:
            name = tag.name
            text = tag.text.strip()
        except Exception as e:
            error_logger.error('Failed to get the text of "{}" : {}'.format(name, e))
        finally:
            debug_logger.debug('The text of tag "{}" is {}'.format(name, text))
            return text

    @staticmethod
    def get_contexts(tag):
        if not isinstance(tag, element.Tag):
            error_logger.error('{} is not an instance of element.Tag'.format(type(tag)))
            raise TypeError('{} is not an instance of element.Tag'.format(type(tag)))
        else:
            pass
        name = ''
        contexts = ''
        try:
            name = tag.name
            contexts = tag.decode()
        except Exception as e:
            error_logger.error('Failed to get the contexts of "{}" : {}'.format(name, e))
        finally:
            debug_logger.debug('The contexts of tag "{}" is {}'.format(name, contexts))
        return contexts

    @staticmethod
    def retrieve(url, filename=None, **kwargs):
        if os.path.exists(filename):
            debug_logger.debug('"{}" exists, skip it'.format(filename))
        else:
            if os.path.exists(filename.rpartition(os.sep)[0]):
                pass
            else:
                os.makedirs(filename.rpartition(os.sep)[0])
                info_logger.info('Directory "{}" is made'.format(filename.rpartition(os.sep)[0]))
            try:
                local_file_name = request.urlretrieve(url, filename, **kwargs)
                info_logger.info('"{}" is retrieved from "{}"'.format(local_file_name, url))
            except Exception as e:
                error_logger.error('Failed to get "{}" from "{}" since: {}'.format(filename, url, e))


class WebSpider(object):

    def __init__(self, entry_url, url_func, xpath_and_caller, web_caller, threads_number=1, **kwargs):
        self._entry_url = entry_url
        self._url_func = url_func
        self._url_generator = self._url_func(self._entry_url)
        self._xpath_and_caller = xpath_and_caller
        self._web_caller = web_caller
        self._threads_number = threads_number
        self._threads_list = list()
        self._lock = threading.Lock()
        self._kwargs = kwargs

    def get_into_new_page(self, **kwargs):
        while True:
            try:
                self._lock.acquire()
                new_url = next(self._url_generator)
                debug_logger.debug('Get into the new page with the url: {}'.format(new_url))
                return self.get_elements_from_page(new_url, self._web_caller, **kwargs)
            except StopIteration as e:
                warn_logger.warn('There is no more url to parse: {}'.format(e))
                break
            except Exception as e:
                critical_logger.critical('Unknown exception: {}'.format(e))
                return
            finally:
                self._lock.release()

    def get_elements_from_page(self, new_url, caller_in_page=None, **kwargs):
        if 'page_spider' in kwargs and isinstance(kwargs['page_spider'], PageSpider):
            page_spider = kwargs['page_spider']
        else:
            error_logger.error('PageSpider instance is not correctly specified')
            raise ValueError('PageSpider instance is not correctly specified')
        kwargs_for_spider_page = {}
        if 'header' in self._kwargs:
            kwargs_for_spider_page['header'] = self._kwargs['header']
        else:
            kwargs_for_spider_page['header'] = {}
        if 'data' in self._kwargs:
            kwargs_for_spider_page['data'] = self._kwargs['data']
        else:
            kwargs_for_spider_page['data'] = None
        try:
            soup = page_spider.spider_page(new_url, **kwargs_for_spider_page)
            xpath_result_in_page = []
            for xpath, caller in self._xpath_and_caller.items():
                page_spider.init_for_next_xpath()
                page_spider.parse_xpath_of_tag(xpath)
                page_spider.find_tag(soup, *tuple(page_spider.xpath))
                page_spider.get_specified_elements()
                info_logger.info('The instance of {} starts to process the contents specified by the xpath: "{}"'.
                                 format(caller.__class__, xpath))
                caller(page_spider)
                temp_inst = copy.copy(page_spider)
                xpath_result_in_page.append(vars(temp_inst))
            info_logger.info('The instance of {} starts to process the contents found in this page'.
                             format(caller_in_page.__class__))
            return caller_in_page(tuple(xpath_result_in_page))
        except Exception as e:
            error_logger.error('Unknown exception: {}'.format(e))

    def start_threads(self):
        if isinstance(self._url_func, types.FunctionType):
            self._url_generator = self._url_func(self._entry_url)
            if isinstance(self._url_generator, types.GeneratorType):
                pass
            else:
                error_logger.error('{} is not a generator'.format(type(self._url_generator)))
                raise TypeError('{} is not a generator'.format(type(self._url_generator)))
        else:
            error_logger.error('{} is not a function'.format(self._url_func))
            raise TypeError('{} is not a function'.format(self._url_func))
        if not isinstance(self._web_caller, type) and callable(self._web_caller):
            pass
        else:
            error_logger.error('The caller: {} for web is not correctly specified'.format(self._web_caller))
            raise ValueError('The caller: {} for web is not correctly specified'.format(self._web_caller))
        if isinstance(self._xpath_and_caller, dict):
            for xpath, caller in self._xpath_and_caller.items():
                if isinstance(xpath, str) and not isinstance(caller, type) and callable(caller):
                    continue
                else:
                    error_logger.error('The caller: {} to process the xpath: {} are not correctly specified'.
                                       format(caller, xpath))
                    raise ValueError('The caller: {} to process the xpath: {} are not correctly specified'.
                                     format(caller, xpath))
        else:
            error_logger.error('{} is not a dict'.format(self._xpath_and_caller))
            raise ValueError('{} is not a dict'.format(self._xpath_and_caller))
        kw = {}
        for i in range(self._threads_number):
            page_spider = PageSpider()
            kw['page_spider'] = page_spider
            thread_request_pages = threading.Thread(target=self.get_into_new_page, kwargs=kw)
            thread_request_pages.start()
            info_logger.info('Thread {} starts'.format(thread_request_pages.name))
            info_logger.info('Thread {} calls function {} with arguments {}'.
                             format(thread_request_pages.name, self.get_into_new_page, kw))
            self._threads_list.append(thread_request_pages)

    def wait_threads(self):
        for thread in self._threads_list:
            thread.join()
            info_logger.info('Thread {} ends'.format(thread.name))
