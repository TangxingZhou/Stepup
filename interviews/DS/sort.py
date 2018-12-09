#!/usr/bin/env python
# -*- coding: utf-8 -*-


def bubble(l):
    print(l)
    if isinstance(l, (list, tuple)):
        for i in range(0, len(l) - 1):
            for j in range(0, len(l) - 1 - i):
                if l[j] > l[j+1]:
                    l[j], l[j+1] = l[j+1], l[j]
    else:
        print('ERROR: The type "{0}" is not supported.'.format(type(l)))
    return l


def bubble2(l):
    print(l)
    if isinstance(l, (list, tuple)):
        for i in range(0, len(l) - 1):
            for j in range(len(l) - 1, i, -1):
                if l[j] < l[j-1]:
                    l[j], l[j-1] = l[j-1], l[j]
    else:
        print('ERROR: The type "{0}" is not supported.'.format(type(l)))
    return l


if __name__ == '__main__':
    print(bubble([5, 7, 2, 12, 24, 3, 2, 15, 22, 9, 16]))
    print(bubble2([5, 7, 2, 12, 24, 3, 2, 15, 22, 9, 16]))
    print(bubble2(set([5, 7, 2, 12, 24, 3, 2, 15, 22, 9, 16])))
