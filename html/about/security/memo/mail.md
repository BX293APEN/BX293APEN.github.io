# メール関連用語まとめ

## 1. 用語一覧

| 用語 | 正式名称 / 読み | 分類 | 概要 |
|---|---|---|---|
| S/MIME | Secure/Multipurpose Internet Mail Extensions | 暗号化・電子署名 | X.509証明書を用いてメール本文の暗号化と電子署名を行う規格。認証局(CA)による階層型PKIで信頼を担保する |
| PGP | Pretty Good Privacy | 暗号化・電子署名 | 公開鍵暗号によるメールの暗号化・署名方式。標準化仕様はOpenPGP、代表的実装はGnuPG。信頼モデルはWeb of Trust |

| オープンリレー | Open Relay | 設定不備 / 脅威 | 第三者による任意宛先へのメール中継を許可しているSMTPサーバ。スパムの踏み台にされる |


## 2. 暗号化・電子署名方式の比較 (S/MIME vs PGP)

| 項目 | S/MIME | PGP (OpenPGP) |
|---|---|---|
| 目的 | 本文の暗号化、電子署名 | 本文の暗号化、電子署名 |
| 鍵・証明書形式 | X.509証明書 | OpenPGP鍵 |
| 信頼モデル | 認証局(CA)による階層型PKI | Web of Trust(相互署名による信頼の輪) |
| 証明書の入手 | CAから発行(有償・無償) | 利用者が自分で鍵ペアを生成 |
| 主な標準 | RFC 8551 | RFC 4880 / RFC 9580 |
| メーラー対応 | Outlook、Thunderbird、Apple Mail等で標準対応が多い | GnuPG連携やプラグインが必要な場合が多い |
| 主な利用場面 | 企業・組織内、取引先間 | 個人間、技術者コミュニティ |

## 3. 送信認証方式の比較 (SMTP-AUTH vs POP before SMTP)



## 4. 

## 6. 
## 7. 関連用語(補足)

| 用語 | 概要 |
|---|---|
| SPF (Sender Policy Framework) | 送信元IPアドレスが、ドメインのDNS(TXTレコード)に登録された許可リストに含まれるかを検証する送信ドメイン認証 |
| STARTTLS | 平文の接続をTLS接続へ昇格させるコマンド。SMTP・POP3・IMAPで利用される |

| ARC (Authenticated Received Chain) | メーリングリスト等の転送経由で崩れるSPF/DKIM認証結果を、中継者が署名付きで引き継ぐ仕組み |
