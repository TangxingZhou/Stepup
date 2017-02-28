from nose.tools import assert_equal
from nose_parameterized import parameterized
from calculator import Count


@parameterized([
    (1, 2, 3),
    (2, 3, 5),
    (3, 4, 7),
    (4, 5, 9),
    (5, 6, 11),
    (6, 7, 13),
])
def test_bdd(para1, para2, expected):
    assert_equal(Count(para1, para2).add(), expected)


class TestAdd(object):

    @parameterized([
    (1, 2, 3),
    (2, 3, 5),
    (3, 4, 7),
    (4, 5, 9),
    (5, 6, 11),
    (6, 7, 13)
    ])
    def test_dd(self, para1, para2, expected):
        assert_equal(Count(para1, para2).add(), expected)
