# -*- coding: utf-8 -*-
from webworm import SqlDB
import unittest
import os
from nose_parameterized import parameterized
from proboscis import test, TestProgram
from proboscis.decorators import before_class
from nose.tools import assert_true, assert_equal


@test(groups=['unit', 'db'])
class TestSql(unittest.TestCase):

    @before_class
    def create_db(self):
        """create sqlite3 database worm.db"""
        self.db = SqlDB('worm.db')
        assert_true(os.path.exists('worm.db'), msg='worm.db is not created')

    @test(groups=['commands'])
    @parameterized.expand([
        (("INSERT INTO user VALUES(?,?,?,?) ('Tom', '20', '1990-05-24', '90')"),
         'user', ['name', 'age', 'birthday', 'score'],
         {'name': 'Tom', 'age': '20', 'birthday': '1990-05-24', 'score': '90'}),
        (("INSERT INTO user VALUES(?,?) ('Jack', '21')"),
         'user', ['name', 'age', 'birthday', 'score'], {'name': 'Jack', 'age': '21'}),
    ])
    def test_gen_insert_command(
            self,
            expected,
            table_name,
            items_name=None,
            insert_info=None):
        """test the function of gen_insert_command"""
        assert_equal(
            self.db.gen_insert_command(
                table_name,
                items_name,
                insert_info),
            expected)
