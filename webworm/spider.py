# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import sys
import random
from webworm import SqlDB, WebSpider
from webuser import *

LOG_FILE = 'log.cfg'
with open(LOG_FILE, encoding='utf-8') as fp:
    logging.config.fileConfig(fp)
debug_logger = logging.getLogger('debug')
info_logger = logging.getLogger('info')
warn_logger = logging.getLogger('warn')
error_logger = logging.getLogger('error')
critical_logger = logging.getLogger('critical')


def args_parser(name, description=None, usage='usage: %(prog)s [options] arg1 arg2', version='1.0'):

    parser = argparse.ArgumentParser(prog=name,
                                     description=description,
                                     usage=usage
                                     )
    parser.add_argument('--version', action='version', version='%(prog)s '+version)
    parser.add_argument('-l', '--url', action='store', required=True, dest='start_url', help='The entry url for spider')
    parser.add_argument('-n', '--number', action='store', required=False, type=int, default=1, choices=range(1, 5),
                        dest='number_of_threads', help='The number of threads for spider')
    parser.add_argument('-x', '--xpath', action='store', required=True, nargs='+', dest='xpath',
                        help='The xpath you wanna get')
    parser.add_argument('-c', '--caller', action='store', required=False, nargs='*', dest='xpath_caller',
                        help='The caller for corresponding xpath')
    parser.add_argument('-p', '--page', action='store', required=True, dest='page_caller', help='The caller for page')
    parser.add_argument('-i', '--item', action='store', required=True, nargs='+', dest='item',
                        help='The item to process for corresponding xpath')
    parser.add_argument('-f', '--filter', action='store', required=False, default='', dest='filter',
                        help='The filter for logs')
    parser.add_argument('-b', '--base', action='store', required=False, default=name[:-3]+'.db', dest='data_base',
                        help='The data base name')
    parser.add_argument('-t', '--table', action='store', required=False, default=name[:-3], dest='table',
                        help='The table name')
    return parser


def main():
    # Some User Agents
    hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6 .1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safa'
                          'ri/535.11'},
           {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
           {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0'
                          '.2403.89 Chrome/44.0.2403.89 Safari/537.36'},
           {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Ge'
                          'cko) Version/5.1 Safari/534.50'},
           {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Vers'
                          'ion/5.1 Safari/534.50'},
           {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
           {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
           {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrom'
                          'e/17.0.963.56 Safari/535.11'},
           {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
           {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}
           ]
    parser = args_parser(sys.argv[0].rpartition('/')[2],
                         description='These are the options for the web spider\nAuthor: Tangxing Zhou')
    if len(sys.argv) is 1:
        parser.print_help()
        sys.exit(1)
    else:
        pass
    args = parser.parse_args()
    m_start_url = args.start_url
    m_database = args.data_base
    m_table = args.table
    m_number_of_threads = args.number_of_threads
    m_xpath = args.xpath
    m_xpath_caller = args.xpath_caller
    if m_xpath_caller is None:
        m_xpath_caller = ['DefaultContentsDispatcher'] * len(m_xpath)
    else:
        pass
    m_page_caller = args.page_caller
    m_item = args.item
    if not args.filter == '':
        m_filter = logging.Filter(args.filter)
        for filter_instance in [debug_logger, info_logger, warn_logger, error_logger, critical_logger]:
            filter_instance.addFilter(m_filter)
    else:
        pass
    m_xpath_and_caller = {}
    if len(m_xpath_caller) is not len(m_xpath) or len(m_item)is not len(m_xpath):
        error_logger.error('The xpaths: {} callers: {} items: {} are not corresponding'.
                           format(m_xpath, m_xpath_caller, m_item))
        raise ValueError('The xpaths: {} callers: {} items: {} are not corresponding'.
                         format(m_xpath, m_xpath_caller, m_item))
    else:
        for index, xpath in enumerate(m_xpath):
            try:
                xpath_caller_instance = eval('{}()'.format(m_xpath_caller[index]))
                m_xpath_and_caller[xpath] = xpath_caller_instance
            except Exception as e:
                error_logger.error('Failed to create the xpath caller instance of {} for xpath: {} {}'.
                                   format(m_xpath_caller[index], m_xpath, e))
    m_db = SqlDB(m_database)
    m_db.create_table(m_table, tuple(), None, *tuple(m_item))
    web_caller = None
    try:
        web_caller = eval('{}({}, "{}", {})'.format(m_page_caller, 'm_db', m_table, m_item))
    except Exception as e:
        error_logger.error('Failed to create the web caller instance of {} {}'.
                           format(m_page_caller, e))
    m_web_spider = WebSpider(m_start_url, url_generator, m_xpath_and_caller, web_caller, m_number_of_threads,
                             header=hds[random.randint(0, len(hds)-1)])
    m_web_spider.start_threads()
    m_web_spider.wait_threads()
    print(m_db.fetchall('select * from {}'.format(m_table))[0][0])

if __name__ == '__main__':
    main()
