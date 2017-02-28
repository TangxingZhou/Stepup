# -*- coding = utf-8 -*-
import unittest
from proboscis import test
from proboscis.asserts import assert_equal
from nose_parameterized import parameterized
from calculator import Count
import time


@test(groups=['unit', 'add'])
@parameterized([
    (1, 2, 4),
    (2, 3, 5),
    (3, 4, 7),
    (4, 5, 9),
    (5, 6, 11),
    (6, 7, 13),
])
def test_add(para1, para2, expected):
    assert_equal(Count(para1, para2).add(), expected)


@test(groups=['unit', 'sub'])
@parameterized([
    (2, 1, 1),
    (3, 1, 2),
    (4, 1, 3),
    (5, 1, 4),
    (6, 1, 5),
    (7, 1, 6),
])
def test_sub(para1, para2, expected):
    assert_equal(Count(para1, para2).sub(), expected)


@test(groups=['unit'])
class TestCalculator(unittest.TestCase):

    expected = 20

    @test(groups=['sub.a'])
    @parameterized.expand([
        (2, 1, 0),
        (3, 1, 2),
        (4, 1, 3),
        (5, 1, 4),
        (6, 1, 5),
        (7, 1, 6),
    ])
    def test_sub_function(self, para1, para2, expected):
        TestCalculator.expected = expected
        assert_equal(Count(para1, para2).sub(), expected)

    @test(groups=['sub.b'], depends_on_groups=[test_sub_function])
    @parameterized.expand([
        (2, 1, 0),
    ])
    def test_expected(self, para1, para2, expected):
        print('ztx', TestCalculator.expected)
        time.sleep(2)
        assert_equal(Count(para1, para2).sub(), expected)
