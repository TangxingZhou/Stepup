#!C:\Python27\python.exe
# -*- coding: utf-8 -*-


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
UTE_USER = 'ute'
UTE_PASSWORD = 'ute'
UTE_LIBS_URL = {
    'robotlte': 'https://beisop70.china.nsn-net.net/isource/svnroot/robotlte/trunk/',
    'utelibs': 'https://beisop70.china.nsn-net.net/isource/svnroot/utelibs/',
    'talibs': 'https://beisop70.china.nsn-net.net/isource/svnroot/talibs/'}

# svn urls for K3 files
K3_SVN_ROOT = 'https://esisov70.emea.nsn-net.net/isource/svnroot'
TTCN3_URL = K3_SVN_ROOT + '/BTS_D_K3LTEASN1/trunk/C_Test/SC_K3LTEASN1/Include/ttcn3'
CODEC_URL = K3_SVN_ROOT + \
    '/BTS_D_K3LTEASN1/trunk/C_Test/SC_K3LTEASN1/Libraries/redhat64/release/'
PCMD_TTCN3_URL = K3_SVN_ROOT + \
    '/BTS_D_K3NSETAP_ASN1/tags/LATEST/include/ttcn3/PCMDmod.ttcn3'
PCMD_CODEC_URL = K3_SVN_ROOT + \
    '/BTS_D_K3NSETAP_ASN1/tags/LATEST/lib64/release/PCMDlib.so'
K3_URLS = (CODEC_URL, PCMD_CODEC_URL, TTCN3_URL, PCMD_TTCN3_URL)
