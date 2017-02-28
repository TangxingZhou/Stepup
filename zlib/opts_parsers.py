# -*- coding: utf-8 -*-
import sys
import optparse
import argparse


def opts_parser(description='This is the demo description', usage="usage: %prog [options] arg1 arg2"):
    parser = optparse.OptionParser(description=description,
                                   usage=usage,
                                   version="%prog 1.0"
                                   )
    parser.add_option('-i', '--ip',
                        action='store',
                        dest='ip_address',
                        default='192.168.255.20',
                        help='You can specify ip of FCT.'
                      )
    #if len(sys.argv) is 1:
        #parser.print_help()
    return parser.parse_args()


def args_parser(description='This is the demo description', usage="usage: %prog [options] arg1 arg2"):
    parser = argparse.ArgumentParser(description=description,
                                     usage=usage,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     version="%prog 1.0"
                                     )
    parser.add_argument('-i', '--ip',
                        action='store',
                        dest='ip_address',
                        default='192.168.255.20',
                        help='You can specify ip of FCT.'
                        )
    return parser.parse_args()

if len(sys.argv) is 1:
    pass
opts, args = opts_parser()
