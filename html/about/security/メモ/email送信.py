#!/usr/bin/env python3

import os
import smtplib
from email.mime.text import MIMEText

class SendMail():
    def __init__(
        self, 
        account = None, 
        password = None, 
        server = "smtp.gmail.com", 
        port = 587
    ):
        self.smtpobj = smtplib.SMTP(server, port)   # SMTPオブジェクト作成
        self.smtpobj.ehlo()                         # SMTPサーバとの接続を確立
        
        if self.smtpobj.has_extn('STARTTLS'):
            self.smtpobj.starttls()
            self.smtpobj.ehlo()
        
        if account is not None:
            self.smtpobj.login(account, password)       # SMTPサーバーへログイン
        
    def __enter__(self):
        return self
    
    def send_mail(
        self, 
        mail_from, 
        mail_to, 
        mail_subject, 
        mail_body
    ):
        """ メッセージのオブジェクト """
        msg = MIMEText(mail_body, "plain", "utf-8")
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = mail_to
        
        try:
            self.smtpobj.sendmail(mail_from, mail_to, msg.as_string())
            return "メール送信完了"
        
        except:
            return "失敗"
    
    def __exit__(self, *args):
        self.smtpobj.quit()
        
        
if __name__== "__main__": # 直接起動の場合はこちらの関数を実行
    with SendMail(
        #account     = "db21014@stumail.daido-it.ac.jp",
        #password    = "20011222",
        server      = 'localhost',
        port        = 25
    ) as email:
        
        """ メール設定 """
        mail_from       = "pen@localhost"       # 送信元アドレス XXXXはUbuntuのアカウント
        mail_to         = "pen@localhost"         # 送信先アドレス(To) XXXXはUbuntuのアカウント
        mail_subject    = input("件名を入力 : ")   # メール件名 　適当に変更
        mail_body       = input("本文を入力 : ")     # メール本文　適当に変更

        """ send_mail関数実行 """
        result = email.send_mail(mail_from, mail_to, mail_subject, mail_body)
        print(result)
