# メール関連用語まとめ

## 1. 用語一覧

| 用語 | 正式名称 / 読み | 分類 | 概要 |
|---|---|---|---|
| S/MIME | Secure/Multipurpose Internet Mail Extensions | 暗号化・電子署名 | X.509証明書を用いてメール本文の暗号化と電子署名を行う規格。認証局(CA)による階層型PKIで信頼を担保する |
| PGP | Pretty Good Privacy | 暗号化・電子署名 | 公開鍵暗号によるメールの暗号化・署名方式。標準化仕様はOpenPGP、代表的実装はGnuPG。信頼モデルはWeb of Trust |
| DKIM | DomainKeys Identified Mail | 送信ドメイン認証 | 送信側MTAが電子署名をヘッダ(`DKIM-Signature`)に付与し、受信側がDNS上の公開鍵で検証する。送信元ドメインの正当性とヘッダ・本文の改ざんを検知できる |
| SMTP-AUTH | SMTP Service Extension for Authentication | 送信認証 | SMTPでユーザー認証を行う拡張。認証済みユーザーのみメール送信(中継)を許可する |
| POP before SMTP | ポップ ビフォア エスエムティーピー | 送信認証 | POP3認証に成功したクライアントのIPアドレスに対し、一定時間SMTP送信を許可する方式。現在は非推奨 |
| OP25B | Outbound Port 25 Blocking | 迷惑メール対策 | ISPが動的IP等から外部ネットワーク宛のポート25(SMTP)通信を遮断する施策。スパム送信ボット対策 |
| DMARC | Domain-based Message Authentication, Reporting, and Conformance | 送信ドメイン認証 | SPF/DKIMの認証結果と`From`ドメインの整合性(アライメント)を評価し、失敗時の扱い(ポリシー)と集計レポートを送信ドメイン側が指定できる仕組み |
| オープンリレー | Open Relay | 設定不備 / 脅威 | 第三者による任意宛先へのメール中継を許可しているSMTPサーバ。スパムの踏み台にされる |
| ベイジアンフィルタリング | Bayesian Filtering | 迷惑メール対策 | ベイズ理論(ナイーブベイズ)により、単語の出現頻度から迷惑メールらしさを確率で判定するフィルタ。学習により精度が向上する |

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

| 項目 | SMTP-AUTH | POP before SMTP |
|---|---|---|
| 認証対象 | ユーザー(ID/パスワード) | クライアントのIPアドレス |
| 認証のタイミング | SMTPセッション内 | 事前のPOP3認証 |
| 標準ポート | 587(サブミッション)、465(SMTPS) | 25 |
| 許可の持続 | セッション単位 | 一定時間(数分〜数十分) |
| 弱点 | 認証情報の漏洩対策が必要(TLS必須) | NAT配下の共有IPで他者にも許可が及ぶ |
| OP25Bとの相性 | 良い(587番を使用) | 悪い(25番を使用) |
| 現在の推奨度 | 推奨 | 非推奨 |

## 4. DMARCポリシー(`p=`タグ)

| 値 | 動作 | 用途 |
|---|---|---|
| `none` | 認証失敗でも何もしない(レポートのみ受け取る) | 導入初期の監視 |
| `quarantine` | 認証失敗メールを隔離する(迷惑メールフォルダ等) | 段階的な強化 |
| `reject` | 認証失敗メールを受信拒否する | 本格運用 |

## 5. メール送受信に関連する主なポート

| ポート | プロトコル | 用途 | 備考 |
|---|---|---|---|
| 25/TCP | SMTP | MTA間のメール転送 | OP25Bの対象 |
| 587/TCP | SMTP Submission | クライアントからのメール送信 | SMTP-AUTH + STARTTLS が基本 |
| 465/TCP | SMTPS | TLS接続でのメール送信 | 暗黙のTLS(Implicit TLS) |
| 110/TCP | POP3 | メール受信 | 平文(非推奨) |
| 995/TCP | POP3S | TLS接続でのメール受信 | |
| 143/TCP | IMAP | メール受信 | 平文またはSTARTTLS |
| 993/TCP | IMAPS | TLS接続でのメール受信 | |

## 6. 迷惑メール対策の分類

| 対策 | 分類 | 対応する用語 | 概要 |
|---|---|---|---|
| 送信ドメイン認証 | 送信元の検証 | DKIM、SPF、DMARC | 送信元ドメインの詐称を検知する |
| 送信ポート制限 | ネットワークレベル | OP25B | 迷惑メールの発信元となるボットの通信を遮断する |
| 送信時のユーザー認証 | 送信サーバ側 | SMTP-AUTH | 認証済みユーザー以外の送信を拒否する |
| 中継制限 | 送信サーバ側 | オープンリレーの防止 | 第三者中継を禁止する |
| 内容ベースの判定 | 受信側フィルタ | ベイジアンフィルタリング | メール内容の統計的特徴から判定する |

## 7. 関連用語(補足)

| 用語 | 概要 |
|---|---|
| SPF (Sender Policy Framework) | 送信元IPアドレスが、ドメインのDNS(TXTレコード)に登録された許可リストに含まれるかを検証する送信ドメイン認証 |
| STARTTLS | 平文の接続をTLS接続へ昇格させるコマンド。SMTP・POP3・IMAPで利用される |
| MTA (Mail Transfer Agent) | メールを中継・配送するサーバソフトウェア(Postfix、sendmail等) |
| MUA (Mail User Agent) | 利用者が使うメールクライアント(Outlook、Thunderbird等) |
| MSA (Mail Submission Agent) | クライアントからのメール送信を受け付けるサーバ(ポート587) |
| ARC (Authenticated Received Chain) | メーリングリスト等の転送経由で崩れるSPF/DKIM認証結果を、中継者が署名付きで引き継ぐ仕組み |
