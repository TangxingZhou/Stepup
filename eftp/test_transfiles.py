# -*- coding: utf-8 -*-
import unittest
import os
from transfiles import TransFile


def setUpModule():
    print('<<<<<<<<<<Testtransfer module start>>>>>>>>>>')


def tearDownModule():
    print('<<<<<<<<<<Testtransfer module end>>>>>>>>>>>>')


class Testmkdir(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print('----------test methord mkdir starts----------')
        self.mtransfer = TransFile('.',
                                   '/home/tangxinz/eftp',
                                   '135.251.238.34',
                                   'tangxinz',
                                   'zhou19891001',
                                   ['asd.txt',
                                    'zxc.txt'])
        self.mtransfer.getReady(0)

    @classmethod
    def tearDownClass(self):
        self.mtransfer.mftp.quit()
        print('----------test methord mkdir ends------------')

    def test_mkdir_local_case1(self):
        path = 'newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'LOCAL', path)
        self.assertTrue(
            os.path.isdir(path),
            msg='Make "' +
            path +
            '" at local failed!')

    def test_mkdir_local_case2(self):
        path = 'newdir0/newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'LOCAL', path)
        self.assertTrue(
            os.path.isdir(path),
            msg='Make "' +
            path +
            '" at local failed!')

    def test_mkdir_local_case3(self):
        path = 'newdir1/newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'LOCAL', path)
        self.assertTrue(
            os.path.isdir(path),
            msg='Make "' +
            path +
            '" at local failed!')

    def test_mkdir_local_case4(self):
        path = 'newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'LOCAL', path)
        self.assertTrue(
            os.path.isdir(path),
            msg='Make "' +
            path +
            '" at local failed!')

    def test_mkdir_remote_case1(self):
        path = 'newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'REMOTE', path)
        result = self.mtransfer.mftp.nlst('')
        print(result)
        self.assertIn(
            path,
            result,
            msg='Make "' +
            path +
            '" at remote failed!')

    def test_mkdir_remote_case2(self):
        path = 'newdir0/newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'REMOTE', path)
        result = self.mtransfer.mftp.nlst('newdir0')
        print(result)
        self.assertIn(
            path,
            result,
            msg='Make "' +
            path +
            '" at remote failed!')

    def test_mkdir_remote_case3(self):
        path = 'newdir1/newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'REMOTE', path)
        result = self.mtransfer.mftp.nlst('newdir1')
        print(result)
        self.assertIn(
            path,
            result,
            msg='Make "' +
            path +
            '" at remote failed!')

    def test_mkdir_remote_case4(self):
        path = 'newdir0'
        self.mtransfer.mkdir(self.mtransfer.mftp, 'REMOTE', path)
        result = self.mtransfer.mftp.nlst('')
        print(result)
        self.assertIn(
            path,
            result,
            msg='Make "' +
            path +
            '" at remote failed!')


class Testisfile(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print('----------test methord isfile starts----------')
        self.mtransfer = TransFile('.',
                                   '/home/tangxinz/eftp',
                                   '135.251.238.34',
                                   'tangxinz',
                                   'zhou19891001',
                                   ['asd.txt',
                                    'zxc.txt'])
        self.mtransfer.getReady(0)

    @classmethod
    def tearDownClass(self):
        self.mtransfer.mftp.quit()
        print('----------test methord isfile ends------------')

    def test_isfile_local_case1(self):
        tocheck = 'mydir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'does not exist')

    def test_isfile_local_case2(self):
        tocheck = 'myfile.txt'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'does not exist')

    def test_isfile_local_case3(self):
        tocheck = 'mydir\\mydir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'does not exist')

    def test_isfile_local_case4(self):
        tocheck = 'mydir\\myfile.txt'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'does not exist')

    def test_isfile_local_case5(self):
        tocheck = 'testdir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'is not file')

    def test_isfile_local_case6(self):
        tocheck = 'test.txt'
        self.assertTrue(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'is not file')

    def test_isfile_local_case7(self):
        tocheck = 'testdir\\testdir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'is not file')

    def test_isfile_local_case8(self):
        tocheck = 'testdir\\test.txt'
        self.assertTrue(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'UP'),
            msg=tocheck +
            'is not file')

    def test_isfile_remote_case1(self):
        tocheck = 'mydir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'does not exist')

    def test_isfile_remote_case2(self):
        tocheck = 'myfile.txt'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'does not exist')

    def test_isfile_remote_case3(self):
        tocheck = 'mydir/mydir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'does not exist')

    def test_isfile_remote_case4(self):
        tocheck = 'mydir/myfile.txt'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'does not exist')

    def test_isfile_remote_case5(self):
        tocheck = 'testdir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'is not file')

    def test_isfile_remote_case6(self):
        tocheck = 'test.txt'
        self.assertTrue(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'is not file')

    def test_isfile_remote_case7(self):
        tocheck = 'testdir/testdir'
        self.assertFalse(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'is not file')

    def test_isfile_remote_case8(self):
        tocheck = 'testdir/test.txt'
        self.assertTrue(
            self.mtransfer.isfile(
                self.mtransfer.mftp,
                tocheck,
                'DOWN'),
            msg=tocheck +
            'is not file')

if __name__ == '__main__':
    # unittest.main()
    suite_mkdir = unittest.TestSuite()
    suite_isfile = unittest.TestSuite()
    suite_local = unittest.TestSuite()
    suite_remote = unittest.TestSuite()
    suite_mkdir.addTest(Testmkdir('test_mkdir_local_case1'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_local_case2'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_local_case3'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_local_case4'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_remote_case1'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_remote_case2'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_remote_case3'))
    suite_mkdir.addTest(Testmkdir('test_mkdir_remote_case4'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case1'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case2'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case3'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case4'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case5'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case6'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case7'))
    suite_isfile.addTest(Testisfile('test_isfile_local_case8'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case1'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case2'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case3'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case4'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case5'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case6'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case7'))
    suite_isfile.addTest(Testisfile('test_isfile_remote_case8'))
    suite_local.addTest(Testmkdir('test_mkdir_local_case1'))
    suite_local.addTest(Testmkdir('test_mkdir_local_case2'))
    suite_local.addTest(Testmkdir('test_mkdir_local_case3'))
    suite_local.addTest(Testmkdir('test_mkdir_local_case4'))
    suite_local.addTest(Testisfile('test_isfile_local_case1'))
    suite_local.addTest(Testisfile('test_isfile_local_case2'))
    suite_local.addTest(Testisfile('test_isfile_local_case3'))
    suite_local.addTest(Testisfile('test_isfile_local_case4'))
    suite_local.addTest(Testisfile('test_isfile_local_case5'))
    suite_local.addTest(Testisfile('test_isfile_local_case6'))
    suite_local.addTest(Testisfile('test_isfile_local_case7'))
    suite_local.addTest(Testisfile('test_isfile_local_case8'))
    suite_remote.addTest(Testmkdir('test_mkdir_remote_case1'))
    suite_remote.addTest(Testmkdir('test_mkdir_remote_case2'))
    suite_remote.addTest(Testmkdir('test_mkdir_remote_case3'))
    suite_remote.addTest(Testmkdir('test_mkdir_remote_case4'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case1'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case2'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case3'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case4'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case5'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case6'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case7'))
    suite_remote.addTest(Testisfile('test_isfile_remote_case8'))
    runner = unittest.TextTestRunner()
    runner.run(suite_mkdir)
