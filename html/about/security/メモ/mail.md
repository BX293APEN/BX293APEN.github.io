# 検証環境用メールサーバの構築

> ⚠️ **検証環境専用の手順です。**
> 平文認証・TLS無効・全インターフェース待受を含むため、インターネットに公開するサーバでは使用しないこと。

## 構成

| 役割 | ソフトウェア | ポート |
|---|---|---|
| 送信サーバ (SMTP) | Postfix | 25 |
| 受信サーバ (POP3) | Dovecot | 110 |
| 受信サーバ (IMAP4) | Dovecot | 143 |

## 保存先の指定 (`MAIL_ROOT`)

メールの保存先は、Postfix と Dovecot の**両方で同じ値**にする。
ターミナルを開き直した場合は、変数を再度設定すること。

| `MAIL_ROOT` の値 | 保存先 |
|---|---|
| `""` (空) | 各ユーザの `~/Maildir/` |
| `"/Programs/mail"` | `/Programs/mail/<ユーザ名>/` |

## 事前準備: テスト用ユーザ

Dovecot は Ubuntu のユーザ認証 (PAM) を使う。メールを送受信するユーザを作成しておく。

```bash
sudo adduser [ユーザ名]
```

---

## 1. 送信サーバの設定 (Postfix)

### 1-1. インストール

```bash
sudo apt install postfix -y
```

インストール中に表示される **General mail configuration type** で、次の表から選択する。

| タイプ | 内容 |
|---|---|
| No configuration | 設定を一切行わない。`main.cf` などを手動で作成する場合に選ぶ |
| Internet Site | SMTP で直接メールを送受信する。インターネット上のサーバと直接やり取りする一般的な構成 |
| Internet with smarthost | 受信は直接 SMTP で行い、送信は外部のリレーサーバ (smarthost) 経由にする。ISP の SMTP サーバなどを経由する場合に使う |
| Satellite system | 送受信ともにすべて外部の smarthost に任せる。ローカルには配送しない端末向け |
| **Local only** | 同一マシン内のユーザ間のみメールを配送する。外部との送受信は行わない (**本手順で選択**) |

続けて **System mail name** を聞かれた場合は `nc.test` を入力する (1-2 の設定で上書きされるため、他の値でも可)。

<details>
<summary>対話なしでインストールする場合 (任意)</summary>

```bash
echo "postfix postfix/main_mailer_type select Local only" | sudo debconf-set-selections
echo "postfix postfix/mailname string nc.test" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt install postfix -y
```

</details>

### 1-2. 設定 (ターミナルで直接実行)

`main.cf` へ追記 (`tee -a`) すると、Local only 選択時に自動生成された行と**重複定義**になる。
`postconf -e` は「項目があれば置換、なければ追加」を 1 コマンドで行うため、何度実行しても重複しない。


```bash
# 変数の設定
MAIL_ROOT=""                        # ホーム配下 (~/Maildir/) に保存する場合
# MAIL_ROOT="/Programs/mail"        # 任意のフォルダに保存する場合は、この行を有効にする

"${MAIL_ROOT:=$HOME/Maildir/}"
HOST_SHORT=$(hostname -s)
DOMAIN="nc.test"

# 基本設定
# ' : $の展開防止
# default_transport / relay_transport : error → 外部への送信を拒否 : Local Only
# inet_interfaces
#   all : 全インターフェースで待ち受け
#   loopback-only : 自分のみ待ち受け
sudo postconf -e \
  "myhostname = $HOST_SHORT.$DOMAIN" \
  "mydomain = $DOMAIN" \
  'mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain' \
  "mynetworks = 127.0.0.0/8" \
  "inet_interfaces = all" \
  "inet_protocols = ipv4" \
  "default_transport = error" \
  "relay_transport = error" \
  "smtpd_recipient_restrictions = permit_mynetworks,reject_unauth_destination"

# メールの保存先

sudo mkdir -p "$MAIL_ROOT"
sudo chown root:mail "$MAIL_ROOT"
sudo chmod 1777 "$MAIL_ROOT"
sudo postconf -e "home_mailbox =" "mail_spool_directory = $MAIL_ROOT/"

sudo chmod 777 /var/mail    # 注意 : 775 に変更推奨


# 反映
sudo postfix check
sudo newaliases
sudo systemctl enable postfix
sudo systemctl restart postfix
```

---

## 2. 受信サーバの設定 (Dovecot)

### 2-1. インストール

```bash
sudo apt install dovecot-core dovecot-imapd dovecot-pop3d -y

# 設定フォルダ
cd /etc/dovecot

# メールの保存先 (MAIL_ROOT は 1-2 ① で設定した値と同じにする)
if [ -n "$MAIL_ROOT" ]; then LOC="maildir:$MAIL_ROOT/%u"; else LOC="maildir:~/Maildir"; fi

# 待受アドレス (閉じた環境以外では 127.0.0.1 推奨)
if grep -q "^listen *=" dovecot.conf; then sudo sed -i "s|^listen *=.*|listen = *|" dovecot.conf; else echo "listen = *" | sudo tee -a dovecot.conf; fi

# メールの保存先
if grep -q "^mail_location *=" conf.d/10-mail.conf; then sudo sed -i "s|^mail_location *=.*|mail_location = $LOC|" conf.d/10-mail.conf; else echo "mail_location = $LOC" | sudo tee -a conf.d/10-mail.conf; fi

# 平文認証を許可 (検証環境のみ : パスワードが平文で流れる)
if grep -q "^disable_plaintext_auth *=" conf.d/10-auth.conf; then sudo sed -i "s|^disable_plaintext_auth *=.*|disable_plaintext_auth = no|" conf.d/10-auth.conf; else echo "disable_plaintext_auth = no" | sudo tee -a conf.d/10-auth.conf; fi

# TLS を無効化 (検証環境のみ : 通信が暗号化されない)
if grep -q "^ssl *=" conf.d/10-ssl.conf; then sudo sed -i "s|^ssl *=.*|ssl = no|" conf.d/10-ssl.conf; else echo "ssl = no" | sudo tee -a conf.d/10-ssl.conf; fi

# 反映
sudo systemctl enable dovecot
sudo systemctl restart dovecot
sudo systemctl status dovecot
```

---

## 3. 受信コード `recv_mail.py`

```python
#!/usr/bin/env python3
"""
# recv_mail.py

POP3 / IMAP4 でメールを受信して表示する。

## クラス一覧

| クラス | プロトコル | 既定ポート |
|---|---|---|
| `POP3` | POP3 | 110 |
| `IMAP4` | IMAP4 | 143 |

参考 : https://docs.python.jp/3/library/poplib.html
"""

import email
import imaplib
import poplib
from email.header import decode_header, make_header
from email.message import Message


def decode_body(msg: Message) -> str:
    """
    ## decode_body

    メール本文 (テキスト) を文字列として取り出す。
    マルチパートの場合は、最初の `text/plain` (添付ファイルを除く) を返す。

    | 引数 | 型 | 内容 |
    |---|---|---|
    | `msg` | `Message` | 受信したメールメッセージ |

    | 戻り値 | 型 | 内容 |
    |---|---|---|
    | 本文 | `str` | デコード済みの本文。テキストが見つからない場合は空文字 |
    """
    part = msg
    if msg.is_multipart():
        part = next(
            (
                p for p in msg.walk()
                if p.get_content_type() == "text/plain"
                and p.get_content_disposition() != "attachment"
            ),
            None,
        )
        if part is None:
            return ""

    payload = part.get_payload(decode=True) or b""
    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, "ignore")


class POP3:
    """
    ## POP3

    POP3 でメールを受信する。`with` 文で使用する。

    | 属性 | 型 | 内容 |
    |---|---|---|
    | `popclient` | `poplib.POP3` | 接続済みの POP3 クライアント |
    """

    def __init__(
        self,
        account,
        password,
        host="localhost",
        port=110,
    ):
        """
        | 引数 | 型 | 既定値 | 内容 |
        |---|---|---|---|
        | `account` | `str` | (必須) | ユーザ名 |
        | `password` | `str` | (必須) | パスワード |
        | `host` | `str` | `"localhost"` | POP3 サーバのホスト |
        | `port` | `int` | `110` | POP3 サーバのポート |
        """
        self.popclient = poplib.POP3(host, port)
        self.popclient.user(account)
        self.popclient.pass_(password)

    def recv_mail(self) -> list[Message]:
        """
        ## recv_mail

        サーバ上のすべてのメールを取得する。

        | 戻り値 | 型 | 内容 |
        |---|---|---|
        | メール一覧 | `list[Message]` | 古い順のメッセージ。メールがなければ空リスト |
        """
        msgList = []  # 取得した MIME メッセージを格納するリスト
        msgNum = self.popclient.stat()[0]  # サーバ上のメール数
        for i in range(msgNum):
            lines = self.popclient.retr(i + 1)[1]  # 番号は 1 から始まる
            msgList.append(email.message_from_bytes(b"\n".join(lines)))

        return msgList

    def del_mail(self, num=0):
        """
        ## del_mail

        メールに削除マークを付ける。

        > POP3 では `quit()` (= `with` 文の終了時) に削除が確定する。
        > 番号は `quit()` まで変化しないため、ループで連続して呼び出しても番号はずれない。

        | 引数 | 型 | 既定値 | 内容 |
        |---|---|---|---|
        | `num` | `int` | `0` | 削除するメールの位置 (0 始まり) |
        """
        self.popclient.dele(num + 1)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.popclient.quit()


class IMAP4:
    """
    ## IMAP4

    IMAP4 でメールを受信する。`with` 文で使用する。
    メールの指定には**すべて UID を使用する** (連番と UID の混在を避けるため)。

    | 属性 | 型 | 内容 |
    |---|---|---|
    | `imapclient` | `imaplib.IMAP4` | 接続済みの IMAP4 クライアント |
    """

    def __init__(
        self,
        account,
        password,
        host="localhost",
        port=143,
        debug=0,
    ):
        """
        | 引数 | 型 | 既定値 | 内容 |
        |---|---|---|---|
        | `account` | `str` | (必須) | ユーザ名 |
        | `password` | `str` | (必須) | パスワード |
        | `host` | `str` | `"localhost"` | IMAP サーバのホスト |
        | `port` | `int` | `143` | IMAP サーバのポート |
        | `debug` | `int` | `0` | デバッグレベル (`0`: 出力なし / `3`: 各命令をトレース) |

        > ⚠️ `debug` を上げると、パスワードを含む通信内容が標準エラーに出力される。学習用途以外では `0` にすること。
        """
        self.imapclient = imaplib.IMAP4(host, port)
        self.imapclient.debug = debug

        self.imapclient.login(account, password)
        self.sel_box()

    def sel_box(self, box="INBOX"):
        """
        ## sel_box

        メールボックスを選択する。

        | 引数 | 型 | 既定値 | 内容 |
        |---|---|---|---|
        | `box` | `str` | `"INBOX"` | メールボックス名 |
        """
        self.imapclient.select(box)

    def recv_mail(self) -> list[Message]:
        """
        ## recv_mail

        選択中のメールボックスのすべてのメールを取得する。

        | 戻り値 | 型 | 内容 |
        |---|---|---|
        | メール一覧 | `list[Message]` | UID の昇順のメッセージ。メールがなければ空リスト |
        """
        typ, data = self.imapclient.uid("SEARCH", None, "ALL")  # data = [b"1 2 3 ..."]
        msgList = []  # 取得した MIME メッセージを格納するリスト
        for uid in data[0].split():
            typ, msgData = self.imapclient.uid("FETCH", uid, "(RFC822)")
            msgList.append(email.message_from_bytes(msgData[0][1]))

        return msgList

    def del_mail(self, num=0):
        """
        ## del_mail

        メールに `\\Deleted` フラグを付ける。

        > 削除の確定 (expunge) は `close()` (= `with` 文の終了時) に行われる。
        > 途中で確定しないため、ループで連続して呼び出しても位置はずれない。

        | 引数 | 型 | 既定値 | 内容 |
        |---|---|---|---|
        | `num` | `int` | `0` | 削除するメールの位置 (0 始まり、UID の昇順) |
        """
        typ, data = self.imapclient.uid("SEARCH", None, "ALL")
        uids = data[0].split()
        self.imapclient.uid("STORE", uids[num], "+FLAGS", "\\Deleted")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.imapclient.close()
        self.imapclient.logout()


if __name__ == "__main__":
    mode = input("mode : pop/imap ")
    if mode == "pop":
        with POP3(
            account     = "[ユーザ名]",
            password    = "[パスワード]",
            host        = "localhost"
        ) as emailRecv:
            msgList = emailRecv.recv_mail()
            # for i in range(len(msgList)):
            #     emailRecv.del_mail(i)
    else:
        with IMAP4(
            account     = "[ユーザ名]",
            password    = "[パスワード]",
            host        = "localhost"
        ) as emailRecv:
            msgList = emailRecv.recv_mail()
            # for i in range(len(msgList)):
            #     emailRecv.del_mail(i)

    for iii, msg in enumerate(msgList):
        # ヘッダ
        fromAddr = str(make_header(decode_header(msg.get("From", ""))))
        subject = str(make_header(decode_header(msg.get("Subject", ""))))
        print(f"No.{iii}, From:{fromAddr}, Subject:{subject}")

        # 本文
        print(decode_body(msg))
```

---

## 4. 送信コード `send_mail.py`

```python
#!/usr/bin/env python3
"""
# send_mail.py

SMTP でメールを送信する。

## 接続先の例

| 用途 | `server` | `port` | `account` |
|---|---|---|---|
| 本手順のローカル Postfix | `"localhost"` | `25` | 不要 (`None`) |
| Gmail | `"smtp.gmail.com"` | `587` | 必要 (アプリパスワード) |
"""

import smtplib
from email.mime.text import MIMEText


class SendMail:
    """
    ## SendMail

    SMTP でメールを送信する。`with` 文で使用する。

    | 属性 | 型 | 内容 |
    |---|---|---|
    | `smtpobj` | `smtplib.SMTP` | 接続済みの SMTP クライアント |
    """

    def __init__(
        self,
        account=None,
        password=None,
        server="smtp.gmail.com",
        port=587,
    ):
        """
        | 引数 | 型 | 既定値 | 内容 |
        |---|---|---|---|
        | `account` | `str \| None` | `None` | ログインするユーザ名。`None` の場合はログインしない |
        | `password` | `str \| None` | `None` | パスワード |
        | `server` | `str` | `"smtp.gmail.com"` | SMTP サーバのホスト |
        | `port` | `int` | `587` | SMTP サーバのポート |
        """
        self.smtpobj = smtplib.SMTP(server, port, timeout=10)  # SMTP オブジェクト作成
        self.smtpobj.ehlo()                                    # SMTP サーバとの接続を確立

        if self.smtpobj.has_extn("STARTTLS"):
            self.smtpobj.starttls()
            self.smtpobj.ehlo()

        if account is not None:
            self.smtpobj.login(account, password)  # SMTP サーバへログイン

    def __enter__(self):
        return self

    def send_mail(
        self,
        mail_from,
        mail_to,
        mail_subject,
        mail_body,
    ):
        """
        ## send_mail

        テキストメールを送信する。

        | 引数 | 型 | 内容 |
        |---|---|---|
        | `mail_from` | `str` | 送信元アドレス |
        | `mail_to` | `str \| list[str]` | 送信先アドレス。複数宛先はリストで指定 |
        | `mail_subject` | `str` | 件名 |
        | `mail_body` | `str` | 本文 (UTF-8) |

        | 戻り値 | 型 | 内容 |
        |---|---|---|
        | 結果 | `str` | 成功時は `"メール送信完了"`、失敗時は `"失敗 : <原因>"` |
        """
        recipients = [mail_to] if isinstance(mail_to, str) else list(mail_to)

        # メッセージのオブジェクト
        msg = MIMEText(mail_body, "plain", "utf-8")
        msg["Subject"] = mail_subject
        msg["From"] = mail_from
        msg["To"] = ", ".join(recipients)

        try:
            self.smtpobj.sendmail(mail_from, recipients, msg.as_string())
            return "メール送信完了"

        except Exception as e:
            return f"失敗 : {e}"

    def __exit__(self, *args):
        self.smtpobj.quit()


if __name__ == "__main__":  # 直接起動の場合はこちらを実行
    with SendMail(
        # account     = "[自分のメールアドレス]",
        # password    = "[パスワード]",
        server      = "localhost",
        port        = 25
    ) as sender:

        # メール設定
        mail_from       = "[ユーザ名]@localhost"    # 送信元アドレス ([ユーザ名] は Ubuntu のアカウント)
        mail_to         = "[ユーザ名]@localhost"    # 送信先アドレス ([ユーザ名] は Ubuntu のアカウント)
        mail_subject    = input("件名を入力 : ")    # メール件名
        mail_body       = input("本文を入力 : ")    # メール本文

        # send_mail 関数実行
        result = sender.send_mail(mail_from, mail_to, mail_subject, mail_body)
        print(result)
```

---

## 5. 動作確認

| 確認内容 | コマンド | 期待する結果 |
|---|---|---|
| Postfix の設定 | `postconf -n \| grep -E 'myhostname\|mydestination\|home_mailbox\|mail_spool_directory'` | 設定した値が 1 回ずつ表示される |
| Dovecot の設定 | `doveconf -n \| grep -E 'listen\|mail_location\|disable_plaintext_auth\|^ssl'` | `ssl = no` などが表示される |
| 待受ポート | `sudo ss -lntp \| grep -E ':(25\|110\|143) '` | 25 / 110 / 143 が LISTEN |
| 送信 | `python3 send_mail.py` | `メール送信完了` |
| 受信 | `python3 recv_mail.py` | 送信したメールの件名と本文が表示される |
| 保存先 | `ls ~/Maildir/new` (`MAIL_ROOT` 指定時は `ls /Programs/mail/[ユーザ名]/new`) | メールのファイルが存在する |

---

## 付録: 元の手順からの変更点

| 区分 | 元の手順 | 変更後 | 理由 |
|---|---|---|---|
| タイトル | メールサーバ | 検証環境用メールサーバの構築 | 用途の明確化 |
| 権限 | `chmod 777 /var/mail` | コメントアウトし、`775` を推奨と注記 | 全ユーザが他人のメールを読み書きできるため。Maildir 形式では不要 |
| 保存先 | `~/Maildir/` 固定 | `MAIL_ROOT` で `/Programs/mail` などに変更可能 | 保存先を選べるようにするため |
| 記述ミス | `dovecot-pop3d-y` | `dovecot-pop3d -y` | スペース抜けでパッケージが見つからない |
| 重複定義 | `tee -a` / `echo >>` で追記 | ターミナルで直接実行 + 条件分岐 (Postfix: `postconf -e` / Dovecot: `if grep ... sed ... else tee -a`) | 自動生成された行と重複するため |
| パス | `cd /etc/dovecot` 後に `10-mail.conf` などを指定 | `/etc/dovecot/conf.d/` を指定 | ファイルの場所が違い、設定が反映されない |
| TLS | `# ssl = yes` (コメントアウト) | `ssl = no` | コメントアウトでは既定値の `yes` に戻り、無効にならない |
| IMAP | 連番 (`search`) と UID (`uid search`) が混在 | UID に統一 | 番号体系の不一致を避けるため |
| IMAP | `debug = 3` 固定 | 引数 `debug` (既定 `0`) | パスワードが標準エラーに出力されるため |
| 受信 | `get_payload(decode=True)` の結果を直接 `decode` | `decode_body()` で分岐 | マルチパートで `None` になり例外が発生するため |
| 送信 | `except:` (全例外を握りつぶす) | `except Exception as e:` で原因を返す | 原因が分からず、`KeyboardInterrupt` も捕捉するため |
| 送信 | 単一宛先のみ | 複数宛先に対応 | `sendmail` にはリスト、`To` ヘッダにはカンマ区切りが必要なため |
| 送信 | 接続にタイムアウトなし | `timeout=10` | 接続できない場合に固まるのを防ぐため |
| コメント | 「XXXX は Ubuntu のアカウント」だが実際は `pen@...` | `[ユーザ名]@localhost` | コメントと実態の不一致 |
| コメント形式 | 通常のコメント | Markdown 形式 (引数・戻り値などは表) | ユーザ設定に合わせるため |
