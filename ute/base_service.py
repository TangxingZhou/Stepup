#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
import logging
import subprocess
import paramiko
import os
import os.path
import shutil
import re
import zipfile
import datetime


logger = logging.getLogger('base.service')
WINDOWS_HOME = 'E:\\ute_setup\\'


def format_print(to_print):
    print datetime.datetime.now().strftime('%a %Y-%m-%d %H:%M:%S  ') + to_print


class SSHService(object):

    def __init__(self, ip, user, password, windows_local_home=WINDOWS_HOME):
        self.ssh_port = '22'
        self.ip = ip
        self.user = user
        self._password = password
        self.local_path = ''
        self.remote_path = ''
        self.ssh = None
        self.sftp = None
        self.local_windows_home = windows_local_home
        self.local_system = ''
        self.remote_system = ''
        self.local_linesep = ''
        self.local_sep = ''
        self.remote_linesep = ''
        self.remote_sep = ''
        self.get_ready()

    def ssh_to_host(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            format_print('Trying to connect to {0}@{1} via SSH...'.format(self.user, self.ip))
            logger.info('Trying to connect to {0}@{1} via SSH...'.format(self.user, self.ip))
            self.ssh.connect(self.ip, username=self.user, password=self._password, timeout=15)
            format_print('Success to login {0}@{1}'.format(self.user, self.ip))
            logger.info('Success to login {0}@{1}'.format(self.user, self.ip))
        except Exception, e:
            format_print('Fail to login {0}@{1}\n{2}'.format(self.user, self.ip, e))
            logger.error('Fail to login {0}@{1}\n{2}'.format(self.user, self.ip, e))

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
                    logger.info('Success to run command: {0} on {1}@{2}'.format(cmd, self.user, self.ip))
                    if verbose is True:
                        format_print('Success to run command: {0} on {1}@{2}'.format(cmd, self.user, self.ip))
                else:
                    logger.error('Find errors when running command: {0} on {1}@{2}\n{3}'
                                 .format(cmd, self.user, self.ip, std_err))
                    if verbose is True:
                        format_print('Find errors when running command: {0} on {1}@{2}\n{3}'
                                     .format(cmd, self.user, self.ip, std_err))
                return std_out, std_err
            except Exception, e:
                format_print('Fail to run command:{3} on {0}@{1}\n{2}'.format(self.user, self.ip, e, cmd))
                logger.error('Fail to run command: {3} on {0}@{1}\n{2}'.format(self.user, self.ip, e, cmd))
                m_exception = e
                self.ssh_to_host()
        raise m_exception

    def execute_command(self, command, local=False, verbose=True):
        cmd = command.strip().split(' ')
        if local is True:
            try:
                if self.local_system == 'Linux':
                    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                std_out, std_err = child.communicate()
                logger.debug(std_out)
                not_found_error = '{0}: command not found at local {1}\n{2}'.format(cmd[0], self.local_system, std_err)
                if std_err == '':
                    logger.info('Success to run command: {0} at local {1}\n'.format(command, self.local_system))
                    if verbose is True:
                        format_print('Success to run command: {0} at local {1}\n'.format(command, self.local_system))
                else:
                    logger.error('Find errors when running command: {0} at local {1}\n{2}'
                                 .format(command, self.local_system, std_err))
                    if verbose is True:
                        format_print('Find errors when running command: {0} at local {1}\n{2}'
                                     .format(command, self.local_system, std_err))
            except Exception, e:
                format_print('Fail to run command:{2} at local {0}\n{1}'.format(self.local_system, e, cmd))
                logger.error('Fail to run command:{2} at local {0}\n{1}'.format(self.local_system, e, cmd))
                raise e
        else:
            std_out, std_err = self.ssh_run_command(command, verbose)
            not_found_error = '{0}: command not found at {1}@{2}\n{3}'.format(cmd[0], self.user, self.ip, std_err)
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

    def list_dir(self, path, local=False, recursive=False):
        subs = []
        if recursive is True:
            self.ls_dir_recursively(subs, path, local)
            return subs
        else:
            return self.ls_dir(path, local)

    def ls_dir_recursively(self, subs, path, local=False):
        if path.endswith(self.local_sep if local is True else self.remote_sep):
            path = path[:-1]
        if self.is_dir(path, local) is True:
            path_subs = self.ls_dir(path, local)
            for sub in path_subs:
                sub_path = path + self.local_sep + sub if local is True else path + self.remote_sep + sub
                subs.append(sub_path)
                self.ls_dir_recursively(subs, sub_path, local)
        else:
            return

    def ls_dir(self, path, local=False):
        if local is True:
            if self.is_dir(path, local) is True:
                result = os.listdir(path)
            else:
                result = []
        else:
            result = self.ls(path)
        return result

    def create_dir(self, path, local=False):
        result = False
        if local is True:
            try:
                os.makedirs(path)
                logger.debug('{0} is created at local {1}'.format(path, self.local_system))
                result = True
            except Exception, e:
                logger.error('Fail to create {0} at local {1}\n{2}'.format(path, self.local_system, e))
        else:
            out = self.execute_command('mkdir -p {0}'.format(path))
            if out[1] == '':
                logger.debug('{0} is created at {1}@{2}'.format(path, self.user, self.ip))
                result = True
            else:
                logger.error('Fail to create {0} at {1}@{2}'.format(path, self.user, self.ip))
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
                    logger.debug('{0} is removed at local {1}'.format(path, self.local_system))
                    result = True
                except Exception, e:
                    logger.error('Fail to remove {0} at local {1}\n{2}'.format(path, self.local_system, e))
            else:
                out = self.ssh_run_command('rm -rf {0}'.format(path), True)
                if out[1] == '':
                    logger.debug('{0} is removed at {1}@{2}'.format(path, self.user, self.ip))
                    result = True
                else:
                    logger.error('Fail to remove {0} at {1}@{2}'.format(path, self.user, self.ip))
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
        std_out, std_err = self.ssh_run_command('ls -l {0}'.format(path), False)
        if std_err != '':
            logger.error('{0} does not exist at {1}@{2}:{3}'.format(path, self.user, self.ip, self.remote_path))
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
            format_print('Success to create SFTP session to {0}@{1}:{2}'.format(self.user, self.ip, self.remote_path))
            logger.info('Success to create SFTP session to {0}@{1}:{2}'.format(self.user, self.ip, self.remote_path))
        except Exception, e:
            format_print('Fail to create SFTP session to {0}@{1}: {2}'.format(self.user, self.ip, e))
            logger.error('Fail to create SFTP session to {0}@{1}: {2}'.format(self.user, self.ip, e))

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
                            format_print('Success to download {0} from {1}@{2} to {3} at local {4}'
                                         .format(remote_file, self.user, self.ip, local_file, self.local_system))
                            logger.info('Success to download {0} from {1}@{2} to {3} at local {4}'
                                        .format(remote_file, self.user, self.ip, local_file, self.local_system))
                            return True
                        except Exception, e:
                            format_print('Fail to download {0} from {1}@{2} to {3} at local {4}\n{5}'
                                         .format(remote_file, self.user, self.ip, local_file, self.local_system, e))
                            logger.error('Fail to download {0} from {1}@{2} to {3} at local {4}\n{5}'
                                         .format(remote_file, self.user, self.ip, local_file, self.local_system, e))
                            m_exception = e
                            self.sftp_to_host()
                    else:
                        format_print('{0} does not exist at {1}@{2}'.format(remote_file, self.user, self.ip))
                        logger.error('{0} does not exist at {1}@{2}'.format(remote_file, self.user, self.ip))
                        return False
                elif direction.lower() == 'ul':
                    if self.is_file(local_file, True) is True:
                        try:
                            self.sftp.put(local_file, file_name)
                            format_print('Success to upload {0} from local {1} to {2}@{3}:{4}'
                                         .format(local_file, self.local_system, self.user, self.ip, remote_file))
                            logger.info('Success to upload {0} from local {1} to {2}@{3}:{4}'
                                        .format(local_file, self.local_system, self.user, self.ip, remote_file))
                            return True
                        except Exception, e:
                            format_print('Fail to upload {0} from local {1} to {2}@{3}:{4}\n{5}'
                                         .format(local_file, self.local_system, self.user, self.ip, remote_file, e))
                            logger.info('Fail to upload {0} from local {1} to {2}@{3}:{4}\n{5}'
                                        .format(local_file, self.local_system, self.user, self.ip, remote_file, e))
                            m_exception = e
                            self.sftp_to_host()
                    else:
                        format_print('{0} does not exist at local {1}'.format(local_file, self.local_system))
                        logger.error('{0} does not exist at local {1}'.format(local_file, self.local_system))
                        return False
                else:
                    raise ValueError('{0} must be DL or UL'.format(direction))
            raise m_exception

    def get_system_type(self, local=False):
        if local is True:
            cmd = ['python', '-c', 'import platform;print platform.system()']
            child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            std_out, std_err = child.communicate()
        else:
            cmd = 'python -c "import platform;print platform.system()"'
            std_out, std_err = self.ssh_run_command(cmd, True)
        if std_err == '':
            match = re.match(r'(\w+)', std_out)
            if match is None:
                format_print('Fail to get the type of the system from "{0}"'.format(std_out))
                logger.error('Fail to get the type of the system from "{0}"'.format(std_out))
                return None
            else:
                return match.group(1), std_out[len(match.group(1)):]
        else:
            format_print(std_err)
            logger.error(std_err)
            raise AssertionError(std_err)

    def get_ready(self):
        self.ssh_to_host()
        system_support = ['Linux', 'Windows']
        local_out = self.get_system_type(True)
        remote_out = self.get_system_type(False)
        if local_out is None:
            raise AssertionError('Fail to get the type of the system at local')
        else:
            if remote_out is None:
                raise AssertionError('Fail to get the type of the system at {0}@{1}'.format(self.user, self.ip))
            else:
                if local_out[0] in system_support and remote_out[0] in system_support:
                    self.local_system, self.local_linesep = local_out
                    self.remote_system, self.remote_linesep = remote_out
                    if self.local_system == 'Linux':
                        self.local_path = '/home/{}/'.format(self.execute_command('whoami', True)[0][:-1])
                        self.local_sep = '/'
                    else:
                        self.local_path = self.local_windows_home
                        self.local_sep = '\\'
                    if os.path.exists(self.local_path) is False:
                        os.makedirs(self.local_path)
                        logger.info('Create directory {0} for UTE at local {1}'
                                    .format(self.local_path, self.local_system))
                    else:
                        logger.info('Directory {0} for UTE at local {1} exists'
                                    .format(self.local_path, self.local_system))
                    os.chdir(self.local_path)
                    if self.remote_system == 'Linux':
                        self.remote_path = '/home/{}/'.format(self.user)
                        self.remote_sep = '/'
                    else:
                        logger.error('Windows at remote is not supported!!!')
                        raise AssertionError('Windows at remote is not supported!!!')
                else:
                    if local_out[0] not in system_support:
                        logger.error('{0} is not supported at local'.format(local_out[0]))
                        raise AssertionError('{0} is not supported at local'.format(local_out[0]))
                    else:
                        format_print('OS at local is: {0}'.format(self.local_system))
                        logger.info('OS at local is: {0}'.format(self.local_system))
                    if remote_out[0] not in system_support:
                        logger.error('{0} is not supported at {1}@{2}'.format(remote_out[0], self.user, self.ip))
                        raise AssertionError('{0} is not supported at {1}@{2}'
                                             .format(remote_out[0], self.user, self.ip))
                    else:
                        format_print('OS at {0}@{1} is: {2}'.format(self.user, self.ip, self.remote_system))

    def zip_files(self, path, zip_path, local=False):
        result = False
        if self.is_dir(path, local) is True:
            if self.is_file(zip_path, local) is True:
                self.remove(zip_path, local)
            if local is True and self.local_system == 'Windows':
                try:
                    zip_files = zipfile.ZipFile(zip_path, 'w')
                    files_under_path = self.list_dir(path, local, True)
                    for file_under_path in files_under_path:
                        zip_files.write(file_under_path, file_under_path)
                    zip_files.close()
                    result = True
                except Exception, e:
                    logger.error('Fail to zip {0} to {1} at local {2}{3}{4}'
                                 .format(path, zip_path, self.local_system, self.local_linesep, e))
            else:
                out = self.execute_command('zip -r {0} {1}'.format(zip_path, path), local)
                if out[1] == '':
                    result = True
                else:
                    if local is True:
                        logger.error('Fail to zip {0} to {1} at local {2}{3}'
                                     .format(path, zip_path, self.local_system, self.local_linesep))
                    else:
                        logger.error('Fail to zip {0} to {1} at {2}@{3}'.format(zip_path, zip_path, self.user, self.ip))
        else:
            logger.error('{0} does not exist at {1}@{2}'.format(path, self.user, self.ip))
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
                    unzip.close()
                    result = True
                except Exception, e:
                    logger.error('Fail to unzip {0} at local {1}{2}{3}'
                                 .format(zip_path, self.local_system, self.local_linesep, e))
            else:
                out = self.ssh_run_command('unzip -d {0} {1}'.format(zip_name, zip_path))
                if out[1] == '':
                    result = True
                else:
                    logger.error('Fail to unzip {0} at {1}@{2}'.format(zip_path, self.user, self.ip))
        else:
            if local is True:
                logger.error('{0} does not exist at local {1}'.format(zip_path, self.local_system))
            else:
                logger.error('{0} does not exist at {1}@{2}'.format(zip_path, self.user, self.ip))
        return result
