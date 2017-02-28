# -*- encoding = utf-8 -*-
from proboscis import TestProgram
from HTMLTestRunner import HTMLTestRunner
from send_mail import send_mail

PROJECT = 'WebWorm'
HTML_REPORT = PROJECT+'Report.html'
MAKE_REPORT = True


def run_test():

    import test_page, test_web
    test_program = TestProgram()
    if MAKE_REPORT is True:
        with open(HTML_REPORT, 'wb') as fp:
            html_runner = HTMLTestRunner(stream=fp, title='Reports for WebWorm',
                                         description='The HTML report for project {} is generated.\n'
                                                     'Test cases are sorted and suited by proboscis.'.format(PROJECT))
        html_runner.run(test_program.create_test_suite_from_entries(None, test_program.cases))
        send_mail(HTML_REPORT)
    else:
        test_program.run_and_exit()


if __name__ == '__main__':
    run_test()
