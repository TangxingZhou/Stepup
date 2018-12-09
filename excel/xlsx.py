#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xlrd
import xlwt
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (process:%(process)d thread:%(thread)d) %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logger = logging.getLogger(__file__)


class ExcelUtil(object):
    def __init__(self, filepath):
        self.file_path = filepath
        self.work_book = xlrd.open_workbook(filepath, formatting_info=True)
        logger.info('Read the excel file {}'.format(filepath))

    @classmethod
    def locate_cell(cls, work_book, sheet, row, column):
        if isinstance(row, int):
            row_id = row
            if isinstance(sheet, int):
                sheet_id = sheet
            elif isinstance(sheet, str):
                if isinstance(work_book, xlrd.Book):
                    try:
                        shee_id = work_book.sheet_names.index(sheet)
                    except ValueError:
                        logger.error('No sheet named {}'.format(sheet))
                        return ()
                elif isinstance(work_book, xlwt.Workbook):
                    shee_id = work_book.sheet_index(sheet)
                else:
                    logger.error('WorkBook should be an instance of xlrd.Book or xlwt.Workbook. But it\'s {}.'.
                                 format(type(work_book)))
                    return ()
            else:
                logger.error('Sheet should be int or str. But it\'s {}.'.format(type(sheet)))
                return ()
            if isinstance(column, int):
                column_id = column
            elif isinstance(column, str):
                from functools import reduce
                column_id = reduce(lambda x, y: 26 * x + y, map(lambda x: ord(x) - 64, column.upper())) - 1
            else:
                logger.error('Column should be int or str. But it\'s {}.'.format(type(column)))
                return ()
            logger.debug('The sheet, row and column indexes are {}, {}, {}'.format(*(sheet_id, row_id, column_id)))
            return (sheet_id, row_id, column_id)
        else:
            return ()

    def read_row(self, sheet, row, start=0, end=None):
        location = self.locate_cell(self.work_book, sheet, row, 0)
        if location == ():
            return ()
        else:
            return tuple(self.work_book.sheet_by_index(location[0]).row_values(location[1], start, end))

    def read_column(self, sheet, column, start=0, end=None):
        location = self.locate_cell(self.work_book, sheet, 0, column)
        if location == ():
            return ()
        else:
            return tuple(self.work_book.sheet_by_index(location[0]).col_values(location[2], start, end))

    def read_cell(self, sheet, row, column):
        location = self.locate_cell(self.work_book, sheet, row, column)
        if location == ():
            return ()
        else:
            return self.work_book.sheet_by_index(location[0]).cell(location[1], location[2]).value

    def get_bg_color(self, sheet, row, column):
        location = self.locate_cell(self.work_book, sheet, row, column)
        if location == ():
            return ''
        else:
            xf_index = self.work_book.sheet_by_index(location[0]).cell_xf_index(location[1], location[2])
            xf_style = self.work_book.xf_list[xf_index]
            xf_background = xf_style.background
            # fill_pattern = xf_background.fill_pattern
            pattern_colour_index = xf_background.pattern_colour_index
            # background_colour_index = xf_background.background_colour_index
            pattern_colour = self.work_book.colour_map[pattern_colour_index]
            # background_colour = self.work_book.colour_map[background_colour_index]
            # hex((pattern_colour[0] << 16) + (pattern_colour[1] << 8) + pattern_colour[2])
            import webcolors
            if pattern_colour is None:
                return webcolors.rgb_to_name((255, 255, 255))
            else:
                return webcolors.rgb_to_name(pattern_colour)

    def write_cell(self, sheet, row, column, value, style):
        from xlutils.copy import copy
        work_book = copy(self.work_book)
        location = self.locate_cell(work_book, sheet, row, column)
        if location != ():
            work_book.get_sheet(location[0]).write(location[1], location[2], value, style)
            work_book.save(self.file_path)

    @classmethod
    def set_bg_color_style(cls, color):
        from xlwt.Style import colour_map
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
        pattern.pattern_fore_colour = colour_map[color.lower()]
        style = xlwt.XFStyle()
        style.pattern = pattern
        return style
