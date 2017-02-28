#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
import argparse
import sys
import os
import os.path
import logging
import datetime
from base_service import SSHService, format_print
from ute_infomation import UTE_HOST_IP, UTE_USER, UTE_PASSWORD, CLOUD_UTE_IP, \
    TTCN3_URL, CODEC_URL, PCMD_TTCN3_URL, PCMD_CODEC_URL


__author__ = 'Tangxing Zhou'
K3_SETUP_DIR = 'E:\\ute_setup\\k3\\'
K3_LOGGING_FILE = 'k3_update.log'


if os.path.exists(K3_SETUP_DIR) is False:
    os.makedirs(K3_SETUP_DIR)
    format_print('Create directory {0} for K3 setup'.format(K3_SETUP_DIR))
    if os.path.isfile(K3_SETUP_DIR + K3_LOGGING_FILE) is False:
        with open(K3_SETUP_DIR + K3_LOGGING_FILE, 'w') as fp:
            fp.close()
            format_print('Make file {0} for logging'.format(K3_SETUP_DIR + K3_LOGGING_FILE))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(filename)s [line:%(lineno)d] '
                           '(process:%(process)d thread:%(thread)d) %(levelname)s: %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=K3_SETUP_DIR + K3_LOGGING_FILE,
                    filemode='w')
logger = logging.getLogger('base')


def args_parser(name, description=None, usage='usage: %(prog)s [options] arg1 arg2', version='1.0'):
    parser = argparse.ArgumentParser(prog=name, description=description, usage=usage)
    parser.add_argument('--version', action='version', version='%(prog)s '+version)
    parser.add_argument('-c', '--cip', action='store', required=True, choices=CLOUD_UTE_IP, dest='cloud_ip',
                        help='The ip for cloud ute')
    parser.add_argument('-d', '--cpd', action='store', required=True, dest='cloud_password',
                        help='The password for cloud ute')
    parser.add_argument('-u', '--ute', action='store', required=True, choices=UTE_HOST_IP.keys(), nargs='+',
                        dest='tl_id', help='The ID for UTE testline')
    parser.add_argument('--all', action='store_true', required=False, default=False, dest='all',
                        help='Update all the K3 related files, partition is by default.')
    return parser


class K3(SSHService):

    def __init__(self, ip, user, password):
        super(K3, self).__init__(ip, user, password, windows_local_home=K3_SETUP_DIR)

    def execute_svn_export(self, src, dest, svn_user='ca_ute_test', svn_pass='utetest', local=True):
        cmd = 'svn --username {} --password {} --force --non-interactive --trust-server-cert export {} {}'\
            .format(svn_user, svn_pass, src, dest)
        self.execute_command(cmd, local)

    def svn_export_k3_files(self, local=True):
        ttcn3_dest = 'release{}ttcn3'.format(self.local_sep if local is True else self.remote_sep)
        codec_dest = 'release{}codec'.format(self.local_sep if local is True else self.remote_sep)
        if self.is_dir(ttcn3_dest) is False:
            self.create_dir(ttcn3_dest, local)
        if self.is_dir(codec_dest) is False:
            self.create_dir(codec_dest, local)
        self.execute_svn_export(TTCN3_URL, ttcn3_dest, local=local)
        self.execute_svn_export(CODEC_URL, codec_dest, local=local)
        self.execute_svn_export(PCMD_TTCN3_URL, ttcn3_dest, local=local)
        self.execute_svn_export(PCMD_CODEC_URL, codec_dest, local=local)

    def check_boost_and_gcc_exist(self):
        paths = []
        if self.is_dir('/opt/boost/') is False:
            paths.append('boost')
        if self.is_dir('/opt/gcc/') is False:
            paths.append('gcc')
        return paths

    def get_boost_and_gcc(self, paths):
        for path in paths:
            if self.zip_files('/opt/' + path, path + '.zip') is True:
                self.sftp_transmit_files((path + '.zip',), 'dl')

    def put_boost_and_gcc(self, zip_paths):
        for zip_path in zip_paths:
            if self.sftp_transmit_files((zip_path + '.zip',), 'ul') is True:
                if self.unzip_files(zip_path + '.zip', zip_path) is True:
                    self.execute_command('sudo mv {0}/opt/{0} /opt'.format(zip_path))
                    self.execute_command('sudo chown -R ute.ute /opt/{}'.format(zip_path))
                    self.execute_command('cd /opt/gcc/4.9.4/lib64/;'
                                         'rm -f libstdc++.so.6;'
                                         'ln -s libstdc++.so.6.0.20 libstdc++.so.6')
                    self.rm_dirs_and_zip_files(zip_paths)

    def rm_dirs_and_zip_files(self, paths):
        for path in paths:
            if self.is_file(path + '.zip') is True:
                self.remove(path + '.zip')
            if self.is_dir(path) is True:
                self.remove(path)

    def get_k3_home(self):
        out = self.execute_command('enb-depsel k3')
        if out[1] == '':
            if self.zip_files('/opt/k3', 'k3.zip') is True:
                self.sftp_transmit_files(('k3.zip',), 'dl')

    def put_k3_home(self):
        if self.sftp_transmit_files(('k3.zip',), 'ul') is True:
            if self.unzip_files('k3.zip', 'k3') is True:
                self.execute_command('sudo mv k3/opt/k3 /opt')
                self.execute_command('sudo chown -R ute.ute /opt/k3')
                self.execute_command('cd /opt/k3/lib64/;'
                                     'rm -f libk3-core.so libk3-core.so.1 libk3.so libk3.so.1')
                self.execute_command('cd /opt/k3/lib64/;'
                                     'ln -s libk3-core.so.1.13.1 libk3-core.so;'
                                     'ln -s libk3-core.so.1.13.1 libk3-core.so.1;'
                                     'ln -s libk3.so.1.13.1 libk3.so;'
                                     'ln -s libk3.so.1.13.1 libk3.so.1')
                self.rm_dirs_and_zip_files('k3')

    def update_k3_files(self, local=True):
        if self.zip_files('release', 'k3.zip', local) is True:
            if self.sftp_transmit_files(('k3.zip',), 'ul') is True:
                if self.unzip_files('k3.zip', 'k3') is True:
                    self.execute_command('chmod 755 k3/release/codec/*')
                    self.execute_command('chmod 644 k3/release/ttcn3/*')
                    self.execute_command('mv k3/release/codec/* /opt/k3/lib64')
                    self.execute_command('mv k3/release/ttcn3/* /opt/k3/lib64/k3/plugins/ttcn3/')
                    self.execute_command('sudo chown -R ute.ute /opt/k3')
                    self.rm_dirs_and_zip_files('k3')


def main():
    parser = args_parser(sys.argv[0].rpartition('/')[2],
                         description='Update the K3 for ASB\nAuthor: Tangxing Zhou\nCompany: NSB\n'
                                     'E-mail: tangxing.zhou@alcatel-sbell.com.cn')
    if len(sys.argv) is 1:
        parser.print_help()
        sys.exit(1)
    else:
        pass
    args = parser.parse_args()
    m_cloud_ip = args.cloud_ip
    m_cloud_password = args.cloud_password
    m_all = args.all
    start_time = datetime.datetime.now()
    for tl_id in args.tl_id:
        m_ute_ip = UTE_HOST_IP[tl_id]
        cloud = None
        ute = K3(m_ute_ip, UTE_USER, UTE_PASSWORD)
        m_paths = ute.check_boost_and_gcc_exist()
        if len(m_paths) is not 0:
            cloud = K3(m_cloud_ip, UTE_USER, m_cloud_password)
            cloud.get_boost_and_gcc(m_paths)
            ute.put_boost_and_gcc(m_paths)
        if m_all is True or ute.is_dir('/opt/k3') is False:
            cloud = K3(m_cloud_ip, UTE_USER, m_cloud_password) if cloud is None else cloud
            cloud.get_k3_home()
            ute.put_k3_home()
        else:
            ute.svn_export_k3_files()
            ute.update_k3_files()
    end_time = datetime.datetime.now()
    print 'Elapsed time: {0}'.format(end_time - start_time)
    logger.info('Elapsed time: {0}'.format(end_time - start_time))


if __name__ == '__main__':
    main()
