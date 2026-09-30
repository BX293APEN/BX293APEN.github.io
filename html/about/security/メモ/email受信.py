#!/usr/bin/env python3

import base64, email, poplib, imaplib
from email.header import decode_header, make_header
# https://docs.python.jp/3/library/poplib.html

class POP3():
    def __init__(
        self, 
        account, 
        password, 
        host = "localhost", 
        port = 110
    ):
        self.popclient = poplib.POP3(host, port)
        self.popclient.user(account)
        self.popclient.pass_(password)
    
    def recv_mail(self):
        msgList = [] # 取得したMIMEメッセージを格納するリスト
        msgNum = self.popclient.stat()[0]  # POP3サーバに存在するメールの数を取得
        for i in range(msgNum):
            msgBytes = b""
            for line in self.popclient.retr(i+1)[1]:  # i+1から始まる
                msgBytes += line + b"\n"
            msgList.append(email.message_from_bytes(msgBytes))
        
        return msgList
    
    def del_mail(self, num = 0):
        self.popclient.dele(num + 1)
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.popclient.quit()

class IMAP4():
    def __init__(
        self, 
        account, 
        password, 
        host = "localhost", 
        port = 143
    ):
        self.imapclient = imaplib.IMAP4(host, port)
        self.imapclient.debug = 3  # 各命令をトレースする
        
        self.imapclient.login(account, password)
        self.sel_box()
    
    def sel_box(self, box = "INBOX"):
        self.imapclient.select(box) # メールボックスの選択
        
    def recv_mail(self):
        typ, data = self.imapclient.search(None, "ALL")  # data = [b"1 2 3 4 ..."]
        datas = data[0].split()
        fetchNum = len(datas)
        msgList = []  # 取得したMIMEメッセージを格納するリスト
        for num in datas:
            typ, data = self.imapclient.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            msgList.append(msg)
            
        return msgList
    
    def del_mail(self, num = 0):
        typ, data = self.imapclient.uid('search', None, 'ALL')
        datas = data[0].split()
        self.imapclient.uid('STORE', datas[num], '+FLAGS', '\\Deleted')
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.imapclient.close()
        self.imapclient.logout()
        
        
if __name__ == "__main__":
    mode = input("mode : pop/imap ")
    if mode == "pop":
        with POP3(
            account     = "pen",
            password    = "20011222",
            host        = "localhost"
        ) as emailRecv:
            msgList = emailRecv.recv_mail()
            # for i in range(len(msgList)):
            #     emailRecv.del_mail(i)
    else:
        with IMAP4(
            account     = "pen",
            password    = "20011222",
            host        = "localhost"
        ) as emailRecv:
            msgList = emailRecv.recv_mail()
            # for i in range(len(msgList)):
            #     emailRecv.del_mail(i)
            
    for iii, msg in enumerate(msgList):
        # ヘッダ
        fromAddr = str(make_header(decode_header(msg["From"])))
        subject = str(make_header(decode_header(msg["Subject"])))
        print(f"No.{iii}, From:{fromAddr}, Subject:{subject}")
        
        # 本文
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        if charset is not None:
            payload = payload.decode(charset, "ignore")
        print(payload)
        
        
