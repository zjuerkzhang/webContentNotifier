#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

g_mail_host="smtp.163.com"
g_mail_port = 25
g_mail_user="MAIL_USER"
g_mail_pass="MAIL_PASSWORD"

g_sender = 'SENDER@doamin.com'
g_receiver = "RECEIVER@doamin.com"

def send_163_mail(receivers, subject, content, attachment_pathes):
    message = MIMEMultipart()
    message['From'] = g_sender
    seperator = ";" 
    message['To'] =  seperator.join(receivers)
    message['Subject'] = Header(subject, 'utf-8')

    message.attach(MIMEText(content, 'plain', 'utf-8'))

    for path in attachment_pathes:
        att1 = MIMEText(open(path, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(path)
        message.attach(att1)

    try:
        smtpObj = smtplib.SMTP(g_mail_host, g_mail_port)
        smtpObj.login(g_mail_user, g_mail_pass)
        smtpObj.sendmail(g_sender, receivers, message.as_string())
    except smtplib.SMTPException:
        print("Error: Fail to send mail")

if __name__ == "__main__":
    subject = "empty subject"
    content = "empty content"
    if len(sys.argv) > 1:
        subject = sys.argv[1]
    if len(sys.argv) > 2:
        content = sys.argv[2]
    send_163_mail([g_receiver], subject, content, [])

