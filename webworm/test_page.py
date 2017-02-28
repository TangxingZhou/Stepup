# -*- coding: utf-8 -*-
from webworm import PageSpider
from bs4 import BeautifulSoup
import unittest
from proboscis import test
from nose_parameterized import parameterized
from nose.tools import assert_is_not_none, assert_is_instance, assert_equal


@test(groups=['page.request'])
def test_request_page():
    assert_is_not_none(PageSpider.request_page('http://sh.meituan.com')['body'], msg='No response got')


@test(groups=['page.spider'], depends_on_groups=['page.request'])
def test_spider_page():
    page_spider = PageSpider()
    assert_is_instance(page_spider.spider_page('http://sh.meituan.com'), BeautifulSoup,
                       msg='No BeautifulSoup instance got')


@test(groups=['page.xpath'], depends_on=[test_spider_page])
class TestXpath(unittest.TestCase):

    def setUp(self):
        self.spider = PageSpider()
        self.spider.spider_page('http://sh.meituan.com')

    @parameterized.expand([
        ('//h1/a', ([{'h1': {}}, {'a': {}}], '', True)),
        ('/h1/a', ([{'h1': {}}, {'a': {}}], '', False)),
        ('//h1/a/text()', ([{'h1': {}}, {'a': {}}], 'text()', True)),
        ('/h1/a/@', ([{'h1': {}}, {'a': {}}], '@', False)),
        ('//h1/a/@href', ([{'h1': {}}, {'a': {}}], '@href', True)),
        ('//h1/a/@', ([{'h1': {}}, {'a': {}}], '@', True)),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/@href',
         ([{'div': {'class': 'J-nav-item'}}, {'dl': {}}, {'dt': {}},
           {'a': {'class': "nav-level1__label", 'hidefocus': 'true'}}], '@href', False)),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/text()',
         ([{'div': {'class': 'J-nav-item'}}, {'dl': {}}, {'dt': {}},
           {'a': {'class': "nav-level1__label", 'hidefocus': 'true'}}], 'text()', False))
    ])
    def test_parse_xpath_of_tag(self, xpath, expected):
        self.spider.parse_xpath_of_tag(xpath)
        print(self.spider.xpath)
        print(self.spider.specified_contents)
        print(self.spider._flag_all)
        assert_equal((self.spider.xpath, self.spider.specified_contents, self.spider._flag_all), expected)


@test(groups=['page.elements'], depends_on_groups=['page.tags'])
class TestElements(unittest.TestCase):

    def setUp(self):
        self.spider = PageSpider()
        self.spider.spider_page('http://sh.meituan.com')

    @parameterized.expand([
        ('//h1/a', ([['<a class="site-logo" gaevent="header/logo" href="http://sh.meituan.com">上海团购</a>']], [], [])),
        ('/h1/a', ([['<a class="site-logo" gaevent="header/logo" href="http://sh.meituan.com">上海团购</a>']], [], [])),
        ('//h1/a/text()', ([], [['上海团购']], [])),
        ('/h1/a/@', ([], [], [[{'class': ['site-logo'], 'href': 'http://sh.meituan.com', 'gaevent': 'header/logo'}]])),
        ('//h1/a/@href', ([], [], [[{'href': 'http://sh.meituan.com'}]])),
        ('//h1/a/@', ([], [], [[{'class': ['site-logo'], 'href': 'http://sh.meituan.com', 'gaevent': 'header/logo'}]])),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/@href',
         ([], [], [[{'href': 'http://sh.meituan.com/category/meishi'}]])),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/text()',
         ([], [['美食']], []))
    ])
    def test_get_specified_elements(self, xpath, expected):
        self.spider.parse_xpath_of_tag(xpath)
        self.spider.find_tag(self.spider._soup, *tuple(self.spider.xpath))
        self.spider.get_specified_elements()
        assert_equal((self.spider.contexts, self.spider.text, self.spider.attributes), expected)


@test(groups=['page.tags'], depends_on_groups=['page.xpath'])
class TestTags(unittest.TestCase):

    def setUp(self):
        self.spider = PageSpider()
        self.spider.spider_page('http://sh.meituan.com')

    @parameterized.expand([
        ('//h1/a', 1),
        ('/h1/a', 1),
        ('//h1/a/text()', 1),
        ('/h1/a/@', 1),
        ('//h1/a/@href', 1),
        ('//h1/a/@', 1),
        ('//div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/@href', 9),
        ('/div[@class="J-nav-item"]/dl/dt/a[@class="nav-level1__label",@hidefocus="true"]/text()', 1)
    ])
    def test_find_tag(self, xpath, expected):
        self.spider.parse_xpath_of_tag(xpath)
        self.spider.find_tag(self.spider._soup, *tuple(self.spider.xpath))
        assert_equal(len(self.spider.tags), expected)
