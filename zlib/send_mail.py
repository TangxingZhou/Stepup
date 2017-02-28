# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
import time
import smtplib


def send_mail(file):
    mail_from = 'zhoutangxing@126.com'
    password = 'zhou19891001'
    mail_to = 'zhoutangxing@126.com'
    with open(file, 'rb') as fp:
        mail_body = fp.read()
    msg = MIMEText(mail_body, _subtype='html', _charset='utf-8')
    msg['Subject'] = '测试报告'
    msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
    msg['from'] = mail_from
    msg['to'] = mail_to
    smtp = smtplib.SMTP()
    try:
        smtp.connect('smtp.126.com')
        smtp.login(mail_from, password)
        smtp.sendmail(mail_from, mail_to, msg.as_string())
    except Exception as e:
        print('Error: ', e)
    finally:
        smtp.quit()
    print('mail has been sent out successfully!')
