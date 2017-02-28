# -*- coding: utf-8 -*-
from webworm import WebSpider, PageSpider
import unittest
from proboscis import test
from nose_parameterized import parameterized
from nose.tools import assert_equal


def url_generator(start_url):
    yield start_url


class XpathCaller(object):

    def __init__(self):
        self.data = None

    def __call__(self, page_spider):
        if isinstance(page_spider, PageSpider):
            if page_spider.specified_contents == '':
                return page_spider.contexts
            elif page_spider.specified_contents.startswith('@'):
                return page_spider.attributes
            elif page_spider.specified_contents == 'text()':
                return page_spider.text
            else:
                return page_spider.tags


class WebCaller(object):

    def __init__(self):
        self.data = None

    def __call__(self, page_data):
        for data in page_data:
            if data['specified_contents'] == '':
                return data['contexts']
            elif data['specified_contents'].startswith('@'):
                return data['attributes']
            elif data['specified_contents'] == 'text()':
                return data['text']
            else:
                return data['tags']


@test(groups=['web'], depends_on_groups=['page.elements'])
class TestWebPage(unittest.TestCase):

    @parameterized.expand([
        ('//h1/a', [['<a class="site-logo" gaevent="header/logo" href="http://sh.meituan.com">上海团购</a>']]),
        ('/h1/a', [['<a class="site-logo" gaevent="header/logo" href="http://sh.meituan.com">上海团购</a>']]),
        ('//h1/a/text()', [['上海团购']]),
        ('/h1/a/@', [[{'class': ['site-logo'], 'href': 'http://sh.meituan.com', 'gaevent': 'header/logo'}]]),
        ('//h1/a/@href', [[{'href': 'http://sh.meituan.com'}]]),
        ('//h1/a/@', [[{'class': ['site-logo'], 'href': 'http://sh.meituan.com', 'gaevent': 'header/logo'}]]),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/@href',
         [[{'href': 'http://sh.meituan.com/category/meishi'}]]),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/text()', [['美食']])
    ])
    def test_get_elements_from_page(self, xpath, expected):
        self.page_spider = PageSpider()
        self.web_spider = WebSpider('http://sh.meituan.com', url_generator, {xpath: XpathCaller()}, WebCaller())
        result = self.web_spider.get_into_new_page(page_spider=self.page_spider)
        assert_equal(result, expected)
