#!/usr/bin/env python
# -*- coding: utf-8 -*-

from excel import ExcelUtil
import os


if __name__ =='__main__':
    work_dir = 'E:\\Projects'
    excel = ExcelUtil(os.path.join(work_dir, 'test.xls'))
    #excel.write_cell(0, 7, 0, 'Lily', excel.set_bg_color_style('green'))
    #print(excel.read_column(0, 'a'))
    print(excel.get_bg_color(0, 6, 0))
