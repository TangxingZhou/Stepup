#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
import argparse
import sys
import logging
import threading
import subprocess
import paramiko
import os
import os.path
import shutil
import re
import zipfile
import datetime


__author__ = 'Tangxing Zhou'
UTE_SETUP_DIR = 'E:\\ute_setup\\'
LOGGING_FILE = 'update.log'
LINSEE_HOST_IP = ('10.135.159.10',
                  '10.135.159.11',
                  '10.135.159.12',
                  '10.135.159.13',
                  '10.135.159.14')
CLOUD_UTE_IP = ('10.42.194.11',
                '10.42.194.12',
                '10.42.194.13',
                '10.42.194.14',
                '10.42.194.15',
                '10.42.194.16',
                '10.42.194.21',
                '10.42.194.22',
                '10.42.194.23')
UTE_HOST_IP = {'1234': '10.9.45.90',
               '2234': '10.9.45.89',
               '3234': '10.9.45.103',
               '4234': '10.9.45.104',
               '5234': '10.9.45.106'}
UTE_TESTLINE_TYPE = {'1234': 'FSMF',
                     '2234': 'FSIP',
                     '3234': 'FSMF',
                     '4234': 'FSMF',
                     '5234': 'FSIP'}
CONFIGURATION_TO_INIT = [
    '''"from ute_testline_configuration.schema import UTE_WMP"''',
    '''""''',
    '''"tl = UTE_WMP(enb_hw_type='{0}',"''',
    '''"{0}pdu_ip='10.9.45.94',"'''.format(
        ' ' * 13),
    '''"{0}pdu_type='ATEN',"'''.format(
        ' ' * 13),
    '''"{0}enb_pdu_outlet=1,"'''.format(
        ' ' * 13),
    '''"{0}iphy_pdu_outlet=2)"'''.format(
        ' ' * 13),
    '''""''']
WHEELS_HOST_IP = '10.42.194.14'
WHEELS_HOME = 'wheelhouse'
UTE_USER = 'ute'
UTE_PASSWORD = 'ute'
UTE_LIBS_URL = {
    'robotlte': 'https://beisop70.china.nsn-net.net/isource/svnroot/robotlte/trunk/',
    'utelibs': 'https://beisop70.china.nsn-net.net/isource/svnroot/utelibs/',
    'talibs': 'https://beisop70.china.nsn-net.net/isource/svnroot/talibs/'}
UTE_LIBS_VERSION = {'robotlte': 'HEAD',
                    'utelibs': 'HEAD',
                    'talibs': 'HEAD'}
BASE_LIBS_VERSION = {'pip': '8.1.2',
                     'setuptools': '19',
                     'ute-installer': '1.2.3'}


def format_print(to_print):
    print datetime.datetime.now().strftime('%a %Y-%m-%d %H:%M:%S  ') + to_print

if os.path.exists(UTE_SETUP_DIR) is False:
    os.makedirs(UTE_SETUP_DIR)
    format_print('Create directory {0} for UTE setup'.format(UTE_SETUP_DIR))
    if os.path.isfile(UTE_SETUP_DIR + LOGGING_FILE) is False:
        with open(UTE_SETUP_DIR + LOGGING_FILE, 'w') as fp:
            fp.close()
            format_print(
                'Make file {0} for logging'.format(
                    UTE_SETUP_DIR + LOGGING_FILE))
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(filename)s [line:%(lineno)d] '
    '(process:%(process)d thread:%(thread)d) %(levelname)s: %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=UTE_SETUP_DIR + LOGGING_FILE,
    filemode='w')
logger = logging.getLogger('logger')
threads = list()
tls_id_ip = dict()
tls_update_result = dict()
tls_update_report = dict()


def args_parser(
        name,
        description=None,
        usage='usage: %(prog)s [options] arg1 arg2',
        version='1.0'):

    parser = argparse.ArgumentParser(
        prog=name, description=description, usage=usage)
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' +
        version)
    parser.add_argument(
        '-l',
        '--lip',
        action='store',
        required=False,
        default=LINSEE_HOST_IP[0],
        choices=LINSEE_HOST_IP,
        dest='linsee_ip',
        help='The IP for linsee')
    parser.add_argument(
        '-s',
        '--lu',
        action='store',
        required=True,
        dest='linsee_user',
        help='The user name for linsee')
    parser.add_argument(
        '-w',
        '--lpd',
        action='store',
        required=True,
        dest='linsee_password',
        help='The password for linsee')
    parser.add_argument(
        '-c',
        '--cip',
        action='store',
        required=True,
        choices=CLOUD_UTE_IP,
        dest='cloud_ip',
        help='The ip for cloud ute')
    parser.add_argument(
        '-d',
        '--cpd',
        action='store',
        required=True,
        dest='cloud_password',
        help='The password for cloud ute')
    parser.add_argument(
        '-i',
        '--iu',
        action='store',
        required=True,
        dest='isource_user',
        help='The user name for isource')
    parser.add_argument(
        '-p',
        '--ipd',
        action='store',
        required=True,
        dest='isource_password',
        help='The password for isource')
    parser.add_argument(
        '-u',
        '--ute',
        action='store',
        required=True,
        choices=UTE_HOST_IP.keys(),
        nargs='+',
        dest='tl_id',
        help='The ID for UTE testline')
    parser.add_argument(
        '-b',
        '--lib',
        action='store',
        required=False,
        nargs='*',
        default=[],
        dest='ute_lib',
        help='The lib to install or update for UTE')
    parser.add_argument(
        '-e',
        '--level',
        action='store',
        type=int,
        required=False,
        choices=range(4),
        default=1,
        dest='update_level',
        help='Update or install robotlte, talibs and utelibs, '
        '0 is for libs specified by option -b/--lib, '
        '1 is for robotlte by default or libs specified by option -b/--lib, '
        '2 is for talibs and utelibs, '
        '3 is for all.')
    parser.add_argument(
        '--local',
        action='store_true',
        required=False,
        default=False,
        dest='local',
        help='Update or install at local or remote for UTE, remote is by default.')
    parser.add_argument(
        '--verbose',
        action='store_true',
        required=False,
        default=False,
        dest='verbose',
        help='Show the verbose information of UTE setup, simple is by default.')
    return parser


class SSHService(object):

    def __init__(self, ip, user, password, tl_id=None):
        self.ssh_port = '22'
        self.ip = ip
        self.user = user
        self._password = password
        self.local_path = ''
        self.remote_path = ''
        self.ssh = None
        self.sftp = None
        self.local_system = ''
        self.remote_system = ''
        self.local_linesep = ''
        self.local_sep = ''
        self.remote_linesep = ''
        self.remote_sep = ''
        self.pip_libs = {}
        self.robotlte_ready = False
        self.update_yes = []
        self.update_no = {}
        self.remains = []
        self.tl_name = tl_id
        self.get_ready()

    def ssh_to_host(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            format_print(
                'Trying to connect to {0}@{1} via SSH...'.format(
                    self.user, self.ip))
            logger.info(
                'Trying to connect to {0}@{1} via SSH...'.format(
                    self.user, self.ip))
            self.ssh.connect(
                self.ip,
                username=self.user,
                password=self._password,
                timeout=15)
            format_print('Success to login {0}@{1}'.format(self.user, self.ip))
            logger.info('Success to login {0}@{1}'.format(self.user, self.ip))
        except Exception as e:
            format_print(
                'Fail to login {0}@{1}\n{2}'.format(
                    self.user, self.ip, e))
            logger.error(
                'Fail to login {0}@{1}\n{2}'.format(
                    self.user, self.ip, e))

    def ssh_close(self):
        self.ssh.close()
        self.ssh = None

    def ssh_run_command(self, cmd, verbose=True):
        m_exception = None
        for i in range(3):
            try:
                out = self.ssh.exec_command(cmd)
                std_out = out[1].read()
                std_err = out[2].read()
                logger.debug(std_out)
                if std_err == '':
                    logger.info(
                        'Success to run command: {0} on {1}@{2}'.format(
                            cmd, self.user, self.ip))
                    if verbose is True:
                        format_print(
                            'Success to run command: {0} on {1}@{2}'.format(
                                cmd, self.user, self.ip))
                else:
                    logger.error(
                        'Find errors when running command: {0} on {1}@{2}\n{3}' .format(
                            cmd, self.user, self.ip, std_err))
                    if verbose is True:
                        format_print(
                            'Find errors when running command: {0} on {1}@{2}\n{3}' .format(
                                cmd, self.user, self.ip, std_err))
                return std_out, std_err
            except Exception as e:
                format_print(
                    'Fail to run command:{3} on {0}@{1}\n{2}'.format(
                        self.user, self.ip, e, cmd))
                logger.error(
                    'Fail to run command: {3} on {0}@{1}\n{2}'.format(
                        self.user, self.ip, e, cmd))
                m_exception = e
                self.ssh_to_host()
        raise m_exception

    def execute_command(self, command, local=False, verbose=True):
        cmd = command.strip().split(' ')
        if local is True:
            try:
                if self.local_system == 'Linux':
                    child = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    child = subprocess.Popen(
                        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                std_out, std_err = child.communicate()
                logger.debug(std_out)
                not_found_error = '{0}: command not found at local {1}\n{2}'.format(
                    cmd[0], self.local_system, std_err)
                if std_err == '':
                    logger.info(
                        'Success to run command: {0} at local {1}\n'.format(
                            command, self.local_system))
                    if verbose is True:
                        format_print(
                            'Success to run command: {0} at local {1}\n'.format(
                                command, self.local_system))
                else:
                    logger.error(
                        'Find errors when running command: {0} at local {1}\n{2}' .format(
                            command, self.local_system, std_err))
                    if verbose is True:
                        format_print(
                            'Find errors when running command: {0} at local {1}\n{2}' .format(
                                command, self.local_system, std_err))
            except Exception as e:
                format_print(
                    'Fail to run command:{2} at local {0}\n{1}'.format(
                        self.local_system, e, cmd))
                logger.error(
                    'Fail to run command:{2} at local {0}\n{1}'.format(
                        self.local_system, e, cmd))
                raise e
        else:
            std_out, std_err = self.ssh_run_command(command, verbose)
            not_found_error = '{0}: command not found at {1}@{2}\n{3}'.format(
                cmd[0], self.user, self.ip, std_err)
        if cmd[0] in std_err and 'not' in std_err and 'command' in std_err:
            format_print(not_found_error)
            logger.error(not_found_error)
            raise AssertionError(not_found_error)
        return std_out, std_err

    def exists(self, path, symbol='-'):
        ls_info = self.ls(path, True)
        if len(ls_info) is 0:
            return False
        else:
            if ls_info[0].startswith(symbol):
                return True
            else:
                return False

    def is_file(self, path, local=False):
        if local is True:
            return os.path.isfile(path)
        else:
            return self.exists(path, '-')

    def is_dir(self, path, local=False):
        if local is True:
            return os.path.isdir(path)
        else:
            return self.exists(path, 'total')

    def list_dir(self, path, local=False):
        if local is True:
            if self.is_dir(path, local) is True:
                result = os.listdir(path)
            else:
                result = []
        else:
            result = self.ls(path)
        return result

    def remove(self, path=None, local=False):
        result = False
        if path is None:
            result = True
        else:
            if local is True:
                try:
                    if self.is_dir(path, local):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    logger.debug(
                        '{0} is removed at local {1}'.format(
                            path, self.local_system))
                    result = True
                except Exception as e:
                    logger.error(
                        'Fail to remove {0} at local {1}\n{2}'.format(
                            path, self.local_system, e))
            else:
                out = self.ssh_run_command('rm -rf {0}'.format(path), True)
                if out[1] == '':
                    logger.debug(
                        '{0} is removed at {1}@{2}'.format(
                            path, self.user, self.ip))
                    result = True
                else:
                    logger.error(
                        'Fail to remove {0} at {1}@{2}'.format(
                            path, self.user, self.ip))
        return result

    @staticmethod
    def get_contents_from_ls(ls_out, verbose=False):
        result = []
        for line in ls_out:
            if verbose is True:
                result.append(line)
            else:
                if line.startswith('total'):
                    continue
                else:
                    result.append(re.split(r'\s+', line)[8])
        return result

    def ls(self, path='', verbose=False):
        std_out, std_err = self.ssh_run_command(
            'ls -l {0}'.format(path), False)
        if std_err != '':
            logger.error(
                '{0} does not exist at {1}@{2}:{3}'.format(
                    path, self.user, self.ip, self.remote_path))
            result = []
        else:
            std_out = std_out.split('\n')
            std_out.pop()
            result = SSHService.get_contents_from_ls(std_out, verbose)
        return result

    def sftp_to_host(self):
        try:
            transport = paramiko.Transport(self.ip + ':' + self.ssh_port)
            transport.connect(username=self.user, password=self._password)
            self.sftp = paramiko.SFTPClient.from_transport(transport)
            self.sftp.chdir(self.remote_path)
            format_print(
                'Success to create SFTP session to {0}@{1}:{2}'.format(
                    self.user, self.ip, self.remote_path))
            logger.info(
                'Success to create SFTP session to {0}@{1}:{2}'.format(
                    self.user, self.ip, self.remote_path))
        except Exception as e:
            format_print(
                'Fail to create SFTP session to {0}@{1}: {2}'.format(
                    self.user, self.ip, e))
            logger.error(
                'Fail to create SFTP session to {0}@{1}: {2}'.format(
                    self.user, self.ip, e))

    def sftp_close(self):
        self.sftp.close()
        self.sftp = None

    def sftp_transmit_files(self, files=tuple(), direction='dl'):
        m_exception = None
        self.sftp_to_host()
        for file_name in files:
            local_file = self.local_path + file_name
            remote_file = self.remote_path + file_name
            for i in range(3):
                if direction.lower() == 'dl':
                    if self.is_file(remote_file, False) is True:
                        try:
                            self.sftp.get(remote_file, local_file)
                            format_print(
                                'Success to download {0} from {1}@{2} to {3} at local {4}' .format(
                                    remote_file, self.user, self.ip, local_file, self.local_system))
                            logger.info(
                                'Success to download {0} from {1}@{2} to {3} at local {4}' .format(
                                    remote_file, self.user, self.ip, local_file, self.local_system))
                            return True
                        except Exception as e:
                            format_print(
                                'Fail to download {0} from {1}@{2} to {3} at local {4}\n{5}' .format(
                                    remote_file, self.user, self.ip, local_file, self.local_system, e))
                            logger.error(
                                'Fail to download {0} from {1}@{2} to {3} at local {4}\n{5}' .format(
                                    remote_file, self.user, self.ip, local_file, self.local_system, e))
                            m_exception = e
                            self.sftp_to_host()
                    else:
                        format_print(
                            '{0} does not exist at {1}@{2}'.format(
                                remote_file, self.user, self.ip))
                        logger.error(
                            '{0} does not exist at {1}@{2}'.format(
                                remote_file, self.user, self.ip))
                        return False
                elif direction.lower() == 'ul':
                    if self.is_file(local_file, True) is True:
                        try:
                            self.sftp.put(local_file, file_name)
                            format_print('Success to upload {0} from local {1} to {2}@{3}:{4}' .format(
                                local_file, self.local_system, self.user, self.ip, remote_file))
                            logger.info('Success to upload {0} from local {1} to {2}@{3}:{4}' .format(
                                local_file, self.local_system, self.user, self.ip, remote_file))
                            return True
                        except Exception as e:
                            format_print('Fail to upload {0} from local {1} to {2}@{3}:{4}\n{5}' .format(
                                local_file, self.local_system, self.user, self.ip, remote_file, e))
                            logger.info('Fail to upload {0} from local {1} to {2}@{3}:{4}\n{5}' .format(
                                local_file, self.local_system, self.user, self.ip, remote_file, e))
                            m_exception = e
                            self.sftp_to_host()
                    else:
                        format_print(
                            '{0} does not exist at local {1}'.format(
                                local_file, self.local_system))
                        logger.error(
                            '{0} does not exist at local {1}'.format(
                                local_file, self.local_system))
                        return False
                else:
                    raise ValueError('{0} must be DL or UL'.format(direction))
            raise m_exception

    @staticmethod
    def svn_co_command(
            repository_url,
            dest_repository,
            user,
            password,
            version='HEAD',
            additions='--non-interactive --trust-server-cert'):
        if version == 'HEAD':
            svn_command = 'svn co {0} {1} --username {2} --password {3} {4}'\
                .format(repository_url, dest_repository, user, password, additions)
        else:
            svn_command = 'svn co {0} {1} -r {2} --username {3} --password {4} {5}' .format(
                repository_url, dest_repository, version, user, password, additions)
        return svn_command

    def svn_repository(
            self,
            isource_user,
            isource_password,
            repository_name,
            local=False):
        version = UTE_LIBS_VERSION[repository_name]
        if len(self.list_dir(repository_name, local)) is not 0:
            if version == 'HEAD':
                command = 'svn update {0} --non-interactive --trust-server-cert'.format(
                    repository_name)
            else:
                command = 'svn update {0} -r {1} --non-interactive --trust-server-cert'.format(
                    repository_name, version)
            if local is True:
                info = "It's about to update {0} to {1} at local {2}:{3}" .format(
                    repository_name, version, self.local_system, self.local_path)
            else:
                info = "It's about to update {0} to {1} at {2}@{3}:{4}" .format(
                    repository_name, version, self.user, self.ip, self.remote_path)
        else:
            command = SSHService.svn_co_command(
                UTE_LIBS_URL[repository_name],
                repository_name,
                isource_user,
                isource_password,
                version)
            if local is True:
                info = "It's about to checkout {0} to {1} at local {2}"\
                    .format(repository_name, version, self.local_system)
            else:
                info = "It's about to checkout {0} to {1} at {2}@{3}:{4}" .format(
                    repository_name, version, self.user, self.ip, self.remote_path)
        logger.info(info)
        self.execute_command(command, local, True)

    def svn_list(self, repository_url, local=False):
        std_out, std_err = self.execute_command(
            'svn list {0}'.format(repository_url), local, True)
        if std_err == '':
            result = []
            if local is True:
                out = std_out.split(self.local_linesep)
            else:
                out = std_out.split(self.remote_linesep)
            for line in out[:-1]:
                line = line.replace('_', '-')
                if 'hooks' != line[:-1]:
                    result.append(line[:-1])
        else:
            result = []
        return result

    def svn_info(self, repository_dir, processed=False, local=False):
        info_dict = {}
        info_str = ''
        if len(self.list_dir(repository_dir, local)) is 0:
            if local is True:
                err_msg = '{0} does not exist or is empty at local {1}:{2}'\
                    .format(repository_dir, self.local_system, self.local_path)
            else:
                err_msg = '{0} does not exist or is empty at {1}@{2}:{3}'\
                    .format(repository_dir, self.user, self.ip, self.remote_path)
            format_print(err_msg)
            logger.error(err_msg)
        else:
            std_out, std_err = self.execute_command(
                'svn info {}'.format(repository_dir), local, True)
            if std_err == '':
                if local is True:
                    out = std_out.split(self.local_linesep)
                    info_str = std_out
                else:
                    out = std_out.split(self.remote_linesep)
                    info_str = std_out.replace(
                        self.remote_linesep, self.local_linesep)
                for line in out[:-1]:
                    if ':' in line:
                        elem = line.split(':')
                        elem = list(map(lambda s: s.strip(), elem))
                        info_dict[elem[0]] = elem[1]
        if processed is True:
            return info_dict
        else:
            return info_str

    def get_system_type(self, local=False):
        if local is True:
            cmd = ['python', '-c', 'import platform;print platform.system()']
            child = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            std_out, std_err = child.communicate()
        else:
            cmd = 'python -c "import platform;print platform.system()"'
            std_out, std_err = self.ssh_run_command(cmd, True)
        if std_err == '':
            match = re.match(r'(\w+)', std_out)
            if match is None:
                format_print(
                    'Fail to get the type of the system from "{0}"'.format(std_out))
                logger.error(
                    'Fail to get the type of the system from "{0}"'.format(std_out))
                return None
            else:
                return match.group(1), std_out[len(match.group(1)):]
        else:
            format_print(std_err)
            logger.error(std_err)
            raise AssertionError(std_err)

    def pip_dict(self, lib_kw='', local=False):
        libs = {}
        std_out, std_err = self.execute_command('pip2 list', local)
        if std_err == '':
            if local is True:
                line_sep = self.local_linesep
            else:
                line_sep = self.remote_linesep
            std_out = std_out.split(line_sep)
            std_out.pop()
            for elem in std_out:
                match = re.match(
                    r'({0}[\w\.-]*)\s\((.+)\)'.format(lib_kw), elem)
                if match is not None:
                    lib_name = match.group(1)
                    lib_version = match.group(2)
                    if lib_name in libs:
                        format_print(
                            'There is another {0}, change its version from {1} to {2}' .format(
                                lib_name, libs[lib_name], lib_version))
                        logger.warn(
                            'There is another {0}, change its version from {1} to {2}' .format(
                                lib_name, libs[lib_name], lib_version))
                    libs[lib_name] = lib_version
        return libs

    @staticmethod
    def compare_version(version_one, version_two):
        version_one_list = version_one.split('.')
        version_two_list = version_two.split('.')
        if len(version_one_list) < len(version_two_list):
            version_one_list = version_one_list + \
                ['0'] * (len(version_two_list) - len(version_one_list))
        elif len(version_one_list) > len(version_one_list):
            version_two_list = version_two_list + \
                ['0'] * (len(version_one_list) - len(version_two_list))
        else:
            pass
        if version_one_list > version_two_list:
            return 1
        elif version_one_list < version_two_list:
            return -1
        else:
            return 0

    def get_ready(self):
        self.ssh_to_host()
        system_support = ['Linux', 'Windows']
        local_out = self.get_system_type(True)
        remote_out = self.get_system_type(False)
        if local_out is None:
            raise AssertionError('Fail to get the type of the system at local')
        else:
            if remote_out is None:
                raise AssertionError(
                    'Fail to get the type of the system at {0}@{1}'.format(
                        self.user, self.ip))
            else:
                if local_out[0] in system_support and remote_out[
                        0] in system_support:
                    self.local_system, self.local_linesep = local_out
                    self.remote_system, self.remote_linesep = remote_out
                    if self.local_system == 'Linux':
                        self.local_path = '/home/{}/'.format(
                            self.execute_command('whoami', True)[0][:-1])
                        self.local_sep = '/'
                    else:
                        self.local_path = UTE_SETUP_DIR
                        self.local_sep = '\\'
                    if os.path.exists(self.local_path) is False:
                        os.makedirs(self.local_path)
                        logger.info(
                            'Create directory {0} for UTE at local {1}' .format(
                                self.local_path, self.local_system))
                    else:
                        logger.info(
                            'Directory {0} for UTE at local {1} exists' .format(
                                self.local_path, self.local_system))
                    os.chdir(self.local_path)
                    if self.remote_system == 'Linux':
                        self.remote_path = '/home/{}/'.format(self.user)
                        self.remote_sep = '/'
                    else:
                        logger.error('Windows at remote is not supported!!!')
                        raise AssertionError(
                            'Windows at remote is not supported!!!')
                    std_out, std_err = self.ssh_run_command('hostname')
                    if std_err == '':
                        self.tl_name = std_out[:-1]
                    else:
                        format_print(
                            'Fail to get the hostname at {0}@{1}'.format(
                                self.user, self.ip))
                        logger.error(
                            'Fail to get the hostname at {0}@{1}'.format(
                                self.user, self.ip))
                    if self.ip in UTE_HOST_IP.values():
                        tls_update_result[self.tl_name] = 'FAIL'
                        tls_id_ip[self.tl_name] = self.ip
                else:
                    if local_out[0] not in system_support:
                        logger.error(
                            '{0} is not supported at local'.format(
                                local_out[0]))
                        raise AssertionError(
                            '{0} is not supported at local'.format(
                                local_out[0]))
                    else:
                        format_print(
                            'OS at local is: {0}'.format(
                                self.local_system))
                        logger.info(
                            'OS at local is: {0}'.format(
                                self.local_system))
                    if remote_out[0] not in system_support:
                        logger.error(
                            '{0} is not supported at {1}@{2}'.format(
                                remote_out[0], self.user, self.ip))
                        raise AssertionError(
                            '{0} is not supported at {1}@{2}' .format(
                                remote_out[0], self.user, self.ip))
                    else:
                        format_print(
                            'OS at {0}@{1} is: {2}'.format(
                                self.user, self.ip, self.remote_system))

    def prepare_to_install(self, wheel_server, local=False):
        if local is True:
            child = subprocess.Popen(
                ['pip2', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            std_out, std_err = child.communicate()
            error_msg = 'Unable to find pip2 at local {0}\n{1}'.format(
                self.local_system, std_err)
        else:
            std_out, std_err = self.ssh_run_command('pip2 -V', True)
            error_msg = 'Unable to find pip2 at {0}@{1}\n{2}'.format(
                self.user, self.ip, std_err)
        if std_err == '':
            match = re.match(r'.*\((.*)\)', std_out)
            if match is None:
                raise AssertionError(
                    'Fail to get the version of python for pip2 from "{0}"'.format(std_out))
            else:
                if match.group(1) == 'python 2.7':
                    to_install = []
                    self.pip_libs = self.pip_dict(local=local)
                    for lib in BASE_LIBS_VERSION:
                        if lib in self.pip_libs:
                            compare_result = SSHService.compare_version(
                                self.pip_libs[lib], BASE_LIBS_VERSION[lib])
                            if compare_result is -1:
                                to_install.append(lib)
                            else:
                                continue
                        else:
                            to_install.append(lib)
                    if len(to_install) is not 0:
                        if isinstance(
                                wheel_server,
                                SSHService) is True and hasattr(
                                wheel_server,
                                'get_wheels_for_libs') is True:
                            wheel_server.get_wheels_for_libs(
                                to_install, 'wheelsbase')
                            wheel_server.get_wheels_and_install_libs(
                                to_install, local, 'wheelsbase')
                else:
                    raise AssertionError(
                        'Please install Python 2.7 (https://www.python.org/downloads/)')
        else:
            format_print(error_msg)
            logger.error(error_msg)
            raise AssertionError(
                'Please install pip for Python 2.7 (https://pypi.python.org/pypi/pip)')

    def make_wheels(self, libs, wheel_home=WHEELS_HOME, local=False):
        make_yes = []
        make_no = []
        if self.is_dir(wheel_home, local) is True:
            self.remove(wheel_home, local)
        for lib in libs:
            std_out, std_err = self.execute_command(
                'pip2 wheel --wheel-dir={0}/{1} {1}'.format(wheel_home, lib), local)
            if std_err == '':
                make_yes.append(lib)
                logger.info(std_out)
            else:
                make_no.append(lib)
                logger.error(std_err)
        return make_yes, make_no

    def install_wheel_files(
            self,
            files_path,
            local=False,
            ignore_version=False):
        install_no = []
        install_yes = []
        file_pip = ''
        new_version = ''
        for file_path in files_path:
            if file_path.endswith('.whl') is True:
                if self.is_file(file_path, local) is True:
                    if ignore_version is False:
                        file_name = file_path.split(
                            self.local_sep if local is True else self.remote_sep)[-1]
                        new_version = SSHService.get_version_from_wheel_file(
                            file_name)
                        try:
                            file_pip = file_name[
                                :file_name.index('-')].replace('_', '-')
                        except Exception as e:
                            file_pip = ''
                            logger.debug(
                                'Fail to get the lib name from{0}\n{1}'.format(
                                    file_name, e))
                        if file_pip in self.pip_libs:
                            old_version = self.pip_libs[file_pip]
                        else:
                            old_version = '0.0.0'
                        version_compare = SSHService.compare_version(
                            new_version, old_version)
                        if version_compare is not 1:
                            logger.info(
                                'No need to update {0}, for the old version is {1} and the new version is {2} '
                                'from {3}'.format(
                                    file_pip, old_version, new_version, file_name))
                            continue
                    out = self.execute_command(
                        'pip2 install {0} --no-deps'.format(file_path), local)
                    if out[1] == '':
                        install_yes.append(files_path)
                        if file_pip != '' and new_version != '':
                            self.pip_libs[file_pip] = new_version
                    else:
                        install_no.append(files_path)
                else:
                    if local is True:
                        logger.error(
                            '{0} does not exists at local {1}'.format(
                                file_path, self.local_system))
                    else:
                        logger.error(
                            '{0} does not exists at {1}@{2}'.format(
                                file_path, self.user, self.ip))
            else:
                if local is True:
                    logger.error(
                        '{0} is not a wheel file at local {1}'.format(
                            file_path, self.local_system))
                else:
                    logger.error(
                        '{0} is not a wheel file at {1}@{2}'.format(
                            file_path, self.user, self.ip))
        return install_yes, install_no

    @staticmethod
    def get_version_from_wheel_file(wheel_name, keyword='.*'):
        match = re.match(r'{0}.*-([\d\.]+)-.*'.format(keyword), wheel_name)
        if match is None:
            format_print('Unable to get version from {0}'.format(wheel_name))
            logger.error('Unable to get version from {0}'.format(wheel_name))
            version = ''
        else:
            version = match.group(1)
        return version

    @staticmethod
    def wheel_for_system(wheel_name):
        if 'linux' in wheel_name:
            return 'Linux'
        elif 'win32' in wheel_name or 'win_amd64' in wheel_name:
            return 'Windows'
        else:
            return 'Any'

    def install_libs(self, libs, wheels_home=WHEELS_HOME, local=False):
        for lib in libs:
            if local is True:
                lib_home = self.local_path + wheels_home + self.local_sep + lib + self.local_sep
            else:
                lib_home = self.remote_path + wheels_home + \
                    self.remote_sep + lib + self.remote_sep
            wheels_for_lib = self.list_dir(lib_home, local)
            if len(wheels_for_lib) is 0:
                self.update_no[lib] = ([], [])
            else:
                wheels_support = []
                wheels_not_support = []
                lib_to_wheel = lib.replace('-', '_')
                lib_wheel = ''
                for wheel in wheels_for_lib:
                    wheel_system = self.wheel_for_system(wheel)
                    if lib_to_wheel in wheel:
                        if lib_wheel == '':
                            lib_wheel = wheel
                        else:
                            format_print(
                                'More than one wheel for {0} is found under {1}'.format(
                                    lib, lib_home))
                            logger.error(
                                'More than one wheel for {0} is found under {1}'.format(
                                    lib, lib_home))
                            lib_wheel = ''
                            break
                    if wheel_system == 'Any':
                        wheels_support.append(wheel)
                    else:
                        if local is True:
                            if self.local_system == wheel_system:
                                wheels_support.append(wheel)
                            else:
                                wheels_not_support.append(wheel)
                                logger.info(
                                    '{0} is for {1}, but the OS is {2} at local' .format(
                                        wheel, wheel_system, self.local_system))
                        else:
                            if self.remote_system == wheel_system:
                                wheels_support.append(wheel)
                            else:
                                wheels_not_support.append(wheel)
                                logger.info(
                                    '{0} is for {1}, but the OS is {2} at {3}@{4}' .format(
                                        wheel, wheel_system, self.local_system, self.user, self.ip))
                if lib_wheel == '':
                    self.update_no[lib] = ([], wheels_for_lib)
                else:
                    lib_version = self.get_version_from_wheel_file(
                        lib_wheel, lib_to_wheel)
                    if lib_version == '':
                        self.update_no[lib] = ([], wheels_for_lib)
                    else:
                        if lib in self.pip_libs:
                            old_version = self.pip_libs[lib]
                        else:
                            old_version = '0.0.0'
                        version_compare = self.compare_version(
                            lib_version, old_version)
                        if version_compare is 1:
                            info = 'Start to update {0}, for the old version is {1} and the new version is {2} ' \
                                   'from {3}'.format(lib, old_version, lib_version, lib_wheel)
                            format_print(info)
                            logger.info(info)
                            wheels_yes, wheels_no = self.install_wheel_files(
                                list(map(lambda s: lib_home + s, wheels_support)), local)
                            if len(wheels_no) is 0:
                                self.update_yes.append(lib)
                            else:
                                self.update_no[lib] = (
                                    wheels_yes, wheels_no, wheels_not_support)
                        else:
                            info = 'No need to update {0}, for the old version is {1} and the new version is {2} ' \
                                   'from {3}'.format(lib, old_version, lib_version, lib_wheel)
                            format_print(info)
                            logger.info(info)
                            self.remains.append(lib)

    def zip_files(self, path, zip_path):
        result = False
        if self.is_dir(path, local=False) is True:
            if self.is_file(zip_path, local=False) is True:
                self.remove(zip_path, local=False)
            out = self.ssh_run_command('zip -r {0} {1}'.format(zip_path, path))
            if out[1] == '':
                result = True
            else:
                logger.error(
                    'Fail to zip {0} to {1} at {2}@{3}'.format(
                        zip_path, zip_path, self.user, self.ip))
        else:
            logger.error(
                '{0} does not exist at {1}@{2}'.format(
                    path, self.user, self.ip))
        return result

    def unzip_files(self, zip_path, zip_name, local=False):
        result = False
        if self.is_file(zip_path, local) is True:
            if self.is_dir(zip_name, local) is True:
                self.remove(zip_name, local)
            if local is True:
                try:
                    unzip = zipfile.ZipFile(zip_path)
                    unzip.extractall()
                    result = True
                except Exception as e:
                    logger.error(
                        'Fail to unzip {0} at local {1}\n{2}'.format(
                            zip_path, self.local_system, e))
            else:
                out = self.ssh_run_command('unzip {0}'.format(zip_path))
                if out[1] == '':
                    result = True
                else:
                    logger.error(
                        'Fail to unzip {0} at {1}@{2}'.format(
                            zip_path, self.user, self.ip))
        else:
            if local is True:
                logger.error(
                    '{0} does not exist at local {1}'.format(
                        zip_path, self.local_system))
            else:
                logger.error(
                    '{0} does not exist at {1}@{2}'.format(
                        zip_path, self.user, self.ip))
        return result

    def get_robotlte(
            self,
            isource_user,
            isource_password,
            repository_name='robotlte',
            local=False):
        self.svn_repository(
            isource_user,
            isource_password,
            repository_name,
            local)
        if self.zip_files(repository_name, repository_name + '.zip') is True:
            self.sftp_transmit_files((repository_name + '.zip',), 'dl')
        else:
            logger.error(
                'Fail to zip {0} to {0}.zip at {1}@{2}'.format(
                    repository_name, self.user, self.ip))
            raise AssertionError(
                'Fail to zip {0} to {0}.zip at {1}@{2}'.format(
                    repository_name, self.user, self.ip))

    def install_robotlte(self, local=False):
        if local is False:
            self.sftp_transmit_files(('robotlte.zip',), 'ul')
        self.robotlte_ready = self.unzip_files(
            'robotlte.zip', 'robotlte', local)

    def get_wheels_for_libs(self, libs, wheels_home=WHEELS_HOME):
        self.make_wheels(libs, wheels_home)
        if self.zip_files(wheels_home, wheels_home + '.zip') is True:
            self.sftp_transmit_files((wheels_home + '.zip',), 'dl')

    def get_wheels_and_install_libs(
            self,
            libs,
            local=False,
            wheels_home=WHEELS_HOME):
        if local is False:
            self.sftp_transmit_files((wheels_home + '.zip',), 'ul')
        if self.unzip_files(wheels_home + '.zip', wheels_home, local) is True:
            self.install_libs(libs, wheels_home, local)

    def ute_setup(
            self,
            libs,
            wheel_server,
            tl_type='FSMF',
            update_robotlte=True,
            local=False,
            verbose=False):
        ute_setup_threads = []
        if local is True:
            tls_update_result.clear()
            tls_id_ip.clear()
            self.tl_name = 'Local {0}'.format(self.local_system)
            tls_update_result[self.tl_name] = 'FAIL'
            tls_id_ip[self.tl_name] = '127.0.0.1'
        if update_robotlte is True:
            robotlte_thread = threading.Thread(
                target=self.install_robotlte, args=(local,))
            robotlte_thread.start()
            logger.info('Thread: {0} starts'.format(robotlte_thread.name))
            logger.info('Thread: {0} calls function {1} with arguments {2}' .format(
                robotlte_thread.name, self.install_robotlte, (local,)))
            ute_setup_threads.append(robotlte_thread)
        if len(libs) is not 0:
            self.prepare_to_install(wheel_server, local)
            libs_thread = threading.Thread(
                target=self.get_wheels_and_install_libs, args=(
                    libs, local))
            libs_thread.start()
            logger.info('Thread {0} starts'.format(libs_thread.name))
            logger.info('Thread {0} calls function {1} with arguments {2}' .format(
                libs_thread.name, self.get_wheels_and_install_libs, (libs, local)))
            ute_setup_threads.append(libs_thread)
        for thread in ute_setup_threads:
            thread.join()
            logger.info('Thread {0} ends'.format(thread.name))
        self.complete(libs, tl_type, update_robotlte, local, verbose)

    def complete(
            self,
            libs,
            tl_type='FSMF',
            update_robotlte=True,
            local=False,
            verbose=False):
        if update_robotlte is True:
            if self.robotlte_ready is True:
                if local is False:
                    self.ssh_run_command(
                        'cd {0}robotlte/;python setup.py develop -U'.format(self.remote_path))
                    self.ssh_run_command(
                        'sed -i "s/Pdu Outlet Reset/# Pdu Outlet Reset/g" '
                        '{0}robotlte/resources/DevWro1/wts_related.robot'.format(
                            self.remote_path))
                    if self.tl_name is not None and self.tl_name not in UTE_HOST_IP:
                        host_name = self.tl_name.replace('-', '_')
                        host_config_dir = '{0}robotlte/config/Shanghai/{1}/'.format(
                            self.remote_path, host_name)
                        site_dir_init = '{0}robotlte/config/Shanghai/__init__.py'.format(
                            self.remote_path)
                        host_dir_init = '{0}robotlte/config/Shanghai/{1}/__init__.py'\
                            .format(self.remote_path, host_name)
                        if self.is_dir(host_config_dir) is False:
                            self.ssh_run_command(
                                'mkdir -p {0}'.format(host_config_dir))
                        else:
                            logger.info(
                                '{0} exists at {1}@{2}'.format(
                                    host_config_dir, self.user, self.ip))
                        if self.is_file(site_dir_init) is False:
                            self.ssh_run_command(
                                'touch {0}'.format(site_dir_init))
                        else:
                            logger.info(
                                '{0} exists at {1}@{2}'.format(
                                    site_dir_init, self.user, self.ip))
                        if self.is_file(host_dir_init) is False:
                            self.ssh_run_command(
                                'touch {0}'.format(host_dir_init))
                            for index, line in enumerate(
                                    CONFIGURATION_TO_INIT):
                                if index is 2:
                                    tl_type_config = line.format(tl_type)
                                    self.ssh_run_command(
                                        '''echo {0}>>{1}'''.format(
                                            tl_type_config, host_dir_init))
                                else:
                                    self.ssh_run_command(
                                        '''echo {0}>>{1}'''.format(
                                            line, host_dir_init))
                        else:
                            logger.info(
                                '{0} exists at {1}@{2}'.format(
                                    host_dir_init, self.user, self.ip))
                    else:
                        format_print(
                            'Hostname of {0}@{1} is Unknown'.format(
                                self.user, self.ip))
                        logger.error(
                            'Hostname of {0}@{1} is Unknown'.format(
                                self.user, self.ip))
                info = self.svn_info('robotlte', False, local)
                if info == '':
                    robotlte_report = 'Fail to get the svn info of robotlte'
                    format_print(robotlte_report)
                    logger.info(robotlte_report)
                else:
                    robotlte_report = info[:-4]
                    format_print(
                        'The robotlte:{0}{1}'.format(
                            self.local_linesep, info))
                    logger.info(
                        'The robotlte:{0}{1}'.format(
                            self.local_linesep, info))
            else:
                robotlte_report = 'Fail to install robotlte'
                format_print(robotlte_report)
                logger.info(robotlte_report)
        else:
            robotlte_report = 'No need to update robotlte'
            format_print(robotlte_report)
            logger.info(robotlte_report)
        if verbose is True:
            msg = 'The talibs & utelibs:{0}Require to update: {1} totally{0}{2}{0}Success to update: {3} totally{0}' \
                  '{4}{0}Remains: {5} totally{0}{6}{0}Fail to update: {7} totally'\
                .format(self.local_linesep, len(libs), ' '.join(libs), len(self.update_yes), ' '.join(self.update_yes),
                        len(self.remains), ' '.join(self.remains), len(self.update_no))
            for k, v in self.update_no.items():
                msg += self.local_linesep + k + ': {0}'.format(v)
        else:
            msg = 'The talibs & utelibs:{0}Require to update: {1}{0}Success to update: {2}{0}Remains: {4}{0}' \
                  'Fail to update: {3}'.format(self.local_linesep, ' '.join(libs), ' '.join(self.update_yes),
                                               ' '.join(self.update_no), ' '.join(self.remains))
        ta_ute_report = '{1:<20}{2}{0}{3:<20}{4}{0}{5:<20}{6}{0}{7:<20}{8}'\
            .format(self.local_linesep, 'Require to update:', '{} totally'.format(len(libs)),
                    'Success to update:', '{} totally'.format(len(self.update_yes)),
                    'Remains:', '{} totally'.format(len(self.remains)),
                    'Fail to update:', '{} totally'.format(len(self.update_no)))
        format_print(msg)
        logger.info(msg)
        if robotlte_report != 'Fail to install robotlte' and len(
                self.update_no) is 0:
            tls_update_result[self.tl_name] = 'PASS'
        if local is True:
            format_print(
                'Complete to setup UTE at local {0}'.format(
                    self.local_system))
            logger.info(
                'Complete to setup UTE at local'.format(
                    self.local_system))
        else:
            format_print(
                'Complete to setup UTE at {0}@{1}'.format(
                    self.user, self.ip))
            logger.info(
                'Complete to setup UTE at {0}@{1}'.format(
                    self.user, self.ip))
        tls_update_report[
            self.tl_name] = '{1:<25}{2:<25}{3}{0}{4:-^60}{0}{5}{0}{6:-^60}{0}{7}{0}{8:=^60}{0}' .format(
            os.linesep,
            self.tl_name,
            'IP: ' + (
                '127.0.0.1' if local is True else self.ip),
            '{:^10}',
            'Robotlte',
            robotlte_report,
            'Ta & Ute',
            ta_ute_report,
            '')
        for zip_file in [
            'robotlte.zip',
            WHEELS_HOME + '.zip',
                'wheelsbase' + '.zip']:
            if self.is_file(zip_file, local) is True:
                self.remove(zip_file, local)
        for wheel_dir in [WHEELS_HOME, 'wheelsbase']:
            if self.is_dir(wheel_dir, local) is True:
                self.remove(wheel_dir, local)

    @staticmethod
    def report(duration):
        report_body = ''
        report_head = '{1:=^60}{0}{2:^60}{0}{1:=^60}{0}'.format(
            os.linesep, '', 'UTE Setup Report')
        report_tail = '{1:<50}{2}{0}{3} testlines, {3} passed, {3} failed{0}{4:<15}{5}{0}{6:<15}{7}{0}{8:=^60}'\
            .format(os.linesep, 'Complete to setup UTE', '{:^10}', '{}', 'Log: ', UTE_SETUP_DIR + LOGGING_FILE,
                    'Elapsed time: ', duration, '')
        tl_pass, tl_fail = 0, 0
        for tl_name in tls_update_result:
            if tl_name in tls_update_report:
                tls_update_report[tl_name] = tls_update_report[
                    tl_name].format(tls_update_result[tl_name])
            else:
                tls_update_report[tl_name] = '{1:<25}{2:<25}{3:^10}{0}{4:-^60}{0}{5}{0}{6:-^60}{0}{7}{0}'\
                    .format(os.linesep, tl_name, 'IP: ' + tls_id_ip[tl_name], tls_update_result[tl_name],
                            'Robotlte', 'ERROR', 'Ta & Ute', 'ERROR')
        for result in tls_update_result.values():
            if 'PASS' == result:
                tl_pass += 1
            else:
                tl_fail += 1
        report_tail = report_tail.format(
            'PASS' if tl_fail is 0 else 'FAIL',
            len(tls_update_result),
            tl_pass,
            tl_fail)
        for tl_result in tls_update_report.values():
            report_body += tl_result
        full_report = report_head + report_body + report_tail
        print full_report
        logger.info(os.linesep + full_report)

    @staticmethod
    def start_thread(func, *args):
        thread = threading.Thread(target=func, args=args)
        thread.start()
        logger.info('Thread {0} starts'.format(thread.name))
        logger.info(
            'Thread {0} calls function {1} with arguments {2}'.format(
                thread.name, func, args))
        threads.append(thread)
        logger.debug('Thread: {0} starts'.format(thread.getName()))

    @staticmethod
    def wait_threads():
        for thread in threads:
            thread.join()
            logger.debug('Thread: {0} ends'.format(thread.getName()))


def main():
    parser = args_parser(
        sys.argv[0].rpartition('/')[2],
        description='Setup the UTE for ASB\nAuthor: Tangxing Zhou\nCompany: NSB\n'
        'E-mail: tangxing.zhou@alcatel-sbell.com.cn')
    if len(sys.argv) is 1:
        parser.print_help()
        sys.exit(1)
    else:
        pass
    args = parser.parse_args()
    m_linsee_ip = args.linsee_ip
    m_linsee_user = args.linsee_user
    m_linsee_password = args.linsee_password
    m_cloud_ip = args.cloud_ip
    m_cloud_password = args.cloud_password
    m_isource_user = args.isource_user
    m_isource_password = args.isource_password
    m_update_level = args.update_level
    m_local = args.local
    m_verbose = args.verbose
    start_time = datetime.datetime.now()
    linsee = SSHService(m_linsee_ip, m_linsee_user, m_linsee_password)
    wheels = SSHService(m_cloud_ip, UTE_USER, m_cloud_password)
    update_robotlte = False
    m_ute_ip = []
    ute_lib = linsee.svn_list(UTE_LIBS_URL['utelibs'])
    ta_lib = linsee.svn_list(UTE_LIBS_URL['talibs'])
    if m_update_level is 0:
        m_ute_libs = args.ute_lib
    elif m_update_level is 1:
        update_robotlte = True
        m_ute_libs = args.ute_lib
    elif m_update_level is 2:
        m_ute_libs = ute_lib + ta_lib
    else:
        update_robotlte = True
        m_ute_libs = ute_lib + ta_lib
    m_ute_libs = tuple(m_ute_libs)
    if m_local is True:
        m_ute_ip = []
    else:
        for tl_id in args.tl_id:
            m_ute_ip.append(UTE_HOST_IP[tl_id])
    args_info = 'Linsee IP: ' + m_linsee_ip + '\n' + \
                'Linsee User: ' + m_linsee_user + '\n' + \
                'Linsee Password: ' + m_linsee_password + '\n' + \
                'Cloud IP: ' + m_cloud_ip + '\n' + \
                'Cloud Password: ' + m_cloud_password + '\n' + \
                'iSource User: ' + m_isource_user + '\n' + \
                'iSource Password: ' + m_isource_password + '\n' + \
                'UTE IP: ' + '  '.join(m_ute_ip) + '\n' + \
                'Local: ' + str(m_local) + '\n' + \
                'Update Level: ' + str(m_update_level) + '\n' + \
                'UTE Libs: ' + '  '.join(m_ute_libs) + '\n'
    print args_info
    logger.info(args_info)
    if update_robotlte is True:
        linsee.start_thread(
            linsee.get_robotlte,
            m_isource_user,
            m_isource_password,
            'robotlte')
    if len(m_ute_libs) is not 0:
        wheels.start_thread(wheels.get_wheels_for_libs, m_ute_libs)
    SSHService.wait_threads()
    if m_local is True:
        linsee.start_thread(
            linsee.ute_setup,
            m_ute_libs,
            wheels,
            'FSMF',
            update_robotlte,
            m_local,
            m_verbose)
    else:
        for tl_id in args.tl_id:
            ip = UTE_HOST_IP[tl_id]
            ute = SSHService(ip, UTE_USER, UTE_PASSWORD, tl_id)
            ute.start_thread(
                ute.ute_setup,
                m_ute_libs,
                wheels,
                UTE_TESTLINE_TYPE[tl_id],
                update_robotlte,
                m_local,
                m_verbose)
    SSHService.wait_threads()
    end_time = datetime.datetime.now()
    SSHService.report('{}'.format(end_time - start_time))


if __name__ == '__main__':
    main()
