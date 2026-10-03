class LinuxModel{
    constructor(){
        this.page =[
            {
                "page" : 1,
                "href" : "/html/tips/linux.html"
            },
            {
                "page" : 2,
                "href" : "/html/tips/linux/network.html"
            },
            {
                "page" : 3,
                "href" : "/html/tips/linux/config.html"
            },
            {
                "page" : 4,
                "href" : "/html/tips/linux/raspi.html"
            },
            {
                "page" : 5,
                "href" : "/html/tips/linux/daemon.html"
            },
            {
                "page" : 6,
                "href" : "/html/tips/linux/format.html"
            },
            {
                "page" : 7,
                "href" : "/html/tips/linux/sh.html"
            },
        ]

        this.treeData = [
            {
                text: "/",
                icon: "fa fa-folder-open",
                nodes: [
                    { text: "すべてのファイルシステム階層の最上位", icon: "fa fa-file" },
                
                    {
                        text: "/bin",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "全ユーザーが使う必須コマンド(近年は/usr/binへのシンボリックリンクが主流)", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/sbin",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "管理者向けの必須コマンド", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/boot",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "ブートローダとカーネルイメージ", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/dev",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "ハードウェアや擬似デバイスへのインターフェース", icon: "fa fa-file" },
                            { text: "/dev/null",    icon: "fa-regular fa-file", nodes: [ { text: "書き込んだデータはすべて破棄。読み込むと即座にEOF", icon: "fa fa-file", tags: ["キャラクタデバイス"] } ] },
                            { text: "/dev/zero",    icon: "fa-regular fa-file", nodes: [ { text: "読み込むと無限に 0x00 を返す",                      icon: "fa fa-file", tags: ["キャラクタデバイス"] } ] },
                            { text: "/dev/random",  icon: "fa-regular fa-file", nodes: [ { text: "乱数を返す(カーネルの乱数生成器)",                  icon: "fa fa-file", tags: ["キャラクタデバイス"] } ] },
                            { text: "/dev/urandom", icon: "fa-regular fa-file", nodes: [ { text: "非ブロッキングの乱数を返す",                        icon: "fa fa-file", tags: ["キャラクタデバイス"] } ] },
                            { text: "/dev/full",    icon: "fa-regular fa-file", nodes: [ { text: "書き込むと常に ENOSPC(容量不足)エラー",            icon: "fa fa-file", tags: ["キャラクタデバイス"] } ] },
                            { text: "/dev/tty",     icon: "fa-regular fa-file", nodes: [ { text: "現在のプロセスの制御端末",                          icon: "fa fa-file", tags: ["キャラクタデバイス"] } ] },
                            { text: "/dev/stdin",   icon: "fa-regular fa-file", nodes: [ { text: "標準入力(/proc/self/fd/0)",                         icon: "fa fa-file", tags: ["シンボリックリンク"] } ] },
                            { text: "/dev/stdout",  icon: "fa-regular fa-file", nodes: [ { text: "標準出力(/proc/self/fd/1)",                         icon: "fa fa-file", tags: ["シンボリックリンク"] } ] },
                            { text: "/dev/stderr",  icon: "fa-regular fa-file", nodes: [ { text: "標準エラー出力(/proc/self/fd/2)",                   icon: "fa fa-file", tags: ["シンボリックリンク"] } ] },
                            { text: "/dev/sda",     icon: "fa-regular fa-file", nodes: [ { text: "1台目のSCSI/SATAディスク",                          icon: "fa fa-file", tags: ["ブロックデバイス"] } ] },
                            { text: "/dev/sda1",    icon: "fa-regular fa-file", nodes: [ { text: "1台目ディスクの第1パーティション",                  icon: "fa fa-file", tags: ["ブロックデバイス"] } ] },
                            { text: "/dev/nvme0n1", icon: "fa-regular fa-file", nodes: [ { text: "1台目のNVMe SSD",                                   icon: "fa fa-file", tags: ["ブロックデバイス"] } ] },
                            { text: "/dev/loop0",   icon: "fa-regular fa-file", nodes: [ { text: "ループバックデバイス",                              icon: "fa fa-file", tags: ["ブロックデバイス"] } ] }
                        ]
                    },
                    {
                        text: "/etc",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "システム全体の設定(静的なテキスト設定)", icon: "fa fa-file" },
                            { text: "/etc/passwd",      icon: "fa-regular fa-file", nodes: [ { text: "ユーザーアカウント情報",              icon: "fa fa-file" } ] },
                            { text: "/etc/shadow",      icon: "fa-regular fa-file", nodes: [ { text: "ハッシュ化されたパスワード(root専用)", icon: "fa fa-file" } ] },
                            { text: "/etc/group",       icon: "fa-regular fa-file", nodes: [ { text: "グループ情報",                        icon: "fa fa-file" } ] },
                            { text: "/etc/fstab",       icon: "fa-regular fa-file", nodes: [ { text: "起動時にマウントするファイルシステム", icon: "fa fa-file" } ] },
                            { text: "/etc/hosts",       icon: "fa-regular fa-file", nodes: [ { text: "ホスト名とIPアドレスの対応",          icon: "fa fa-file" } ] },
                            { text: "/etc/hostname",    icon: "fa-regular fa-file", nodes: [ { text: "ホスト名",                            icon: "fa fa-file" } ] },
                            { text: "/etc/resolv.conf", icon: "fa-regular fa-file", nodes: [ { text: "DNSリゾルバ設定",                     icon: "fa fa-file" } ] },
                            { text: "/etc/sudoers",     icon: "fa-regular fa-file", nodes: [ { text: "sudo の権限設定",                     icon: "fa fa-file" } ] },
                            {
                                text: "/etc/ssh/",
                                icon: "fa fa-folder-open",
                                nodes: [ { text: "SSHサーバ・クライアント設定", icon: "fa fa-file" } ]
                            },
                            {
                                text: "/etc/systemd/",
                                icon: "fa fa-folder-open",
                                nodes: [ { text: "systemd の設定", icon: "fa fa-file" } ]
                            },
                            { text: "/etc/crontab",     icon: "fa-regular fa-file", nodes: [ { text: "定期実行タスク",                      icon: "fa fa-file" } ] },
                            { text: "/etc/profile",     icon: "fa-regular fa-file", nodes: [ { text: "ログインシェルの共通設定",            icon: "fa fa-file" } ] }
                        ]
                    },
                    {
                        text: "/home",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "一般ユーザーの個人データと設定", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/root",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "スーパーユーザーのホームディレクトリ", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/lib",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "/bin, /sbin が必要とするライブラリ", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/lib64",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "64bit用の共有ライブラリ", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/media",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "USBやCD-ROMの自動マウントポイント", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/mnt",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "管理者が手動でマウントする場所", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/opt",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "独立した追加ソフトウェア", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/proc",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "カーネルとプロセスの仮想ファイルシステム", icon: "fa fa-file" },
                            { text: "/proc/cpuinfo", icon: "fa-regular fa-file", nodes: [ { text: "CPU情報",                   icon: "fa fa-file" } ] },
                            { text: "/proc/meminfo", icon: "fa-regular fa-file", nodes: [ { text: "メモリ使用状況",            icon: "fa fa-file" } ] },
                            { text: "/proc/version", icon: "fa-regular fa-file", nodes: [ { text: "カーネルバージョン",        icon: "fa fa-file" } ] },
                            { text: "/proc/uptime",  icon: "fa-regular fa-file", nodes: [ { text: "稼働時間",                  icon: "fa fa-file" } ] },
                            { text: "/proc/mounts",  icon: "fa-regular fa-file", nodes: [ { text: "マウント中のファイルシステム", icon: "fa fa-file" } ] },
                            {
                                text: "/proc/[PID]/",
                                icon: "fa fa-folder-open",
                                nodes: [ { text: "各プロセスの情報(cmdline, status, fd/)", icon: "fa fa-file" } ]
                            },
                            {
                                text: "/proc/sys/",
                                icon: "fa fa-folder-open",
                                nodes: [ { text: "カーネルパラメータ(sysctl)", icon: "fa fa-file" } ]
                            }
                        ]
                    },
                    {
                        text: "/sys",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "デバイスやドライバの仮想ファイルシステム", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/run",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "起動以降の一時的な実行時情報(tmpfs)", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/srv",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "サービスが提供するデータ", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/tmp",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "一時ファイル置き場(再起動で消える場合が多い)", icon: "fa fa-file" }
                        ]
                    },
                    {
                        text: "/usr",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "読み取り専用のプログラム・ライブラリ群", icon: "fa fa-file" },
                            { text: "/usr/bin",     icon: "fa fa-folder-open", nodes: [ { text: "一般ユーザー向けコマンド(大半のプログラム)",        icon: "fa fa-file" } ] },
                            { text: "/usr/sbin",    icon: "fa fa-folder-open", nodes: [ { text: "管理者向けコマンド(非必須)",                      icon: "fa fa-file" } ] },
                            { text: "/usr/lib",     icon: "fa fa-folder-open", nodes: [ { text: "/usr/bin 等のためのライブラリ",                   icon: "fa fa-file" } ] },
                            { text: "/usr/include", icon: "fa fa-folder-open", nodes: [ { text: "C/C++ のヘッダファイル",                          icon: "fa fa-file" } ] },
                            { text: "/usr/share",   icon: "fa fa-folder-open", nodes: [ { text: "アーキテクチャ非依存の共有データ(man, doc, locale)", icon: "fa fa-file" } ] },
                            { text: "/usr/local",   icon: "fa fa-folder-open", nodes: [ { text: "ローカルにインストールしたソフト(パッケージ管理外)", icon: "fa fa-file" } ] },
                            { text: "/usr/src",     icon: "fa fa-folder-open", nodes: [ { text: "ソースコード(カーネルソース等)",                  icon: "fa fa-file" } ] }
                        ]
                    },
                    {
                        text: "/var",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "動作中に内容が変化するデータ", icon: "fa fa-file" },
                            { text: "/var/log",   icon: "fa fa-folder-open", nodes: [ { text: "システムログ(syslog, messages, auth.log)",          icon: "fa fa-file" } ] },
                            { text: "/var/spool", icon: "fa fa-folder-open", nodes: [ { text: "処理待ちデータ(メール、印刷キュー、cron)",          icon: "fa fa-file" } ] },
                            { text: "/var/cache", icon: "fa fa-folder-open", nodes: [ { text: "アプリケーションのキャッシュ",                      icon: "fa fa-file" } ] },
                            { text: "/var/lib",   icon: "fa fa-folder-open", nodes: [ { text: "アプリケーションの状態データ(DB等)",                icon: "fa fa-file" } ] },
                            { text: "/var/tmp",   icon: "fa fa-folder-open", nodes: [ { text: "再起動後も残る一時ファイル",                        icon: "fa fa-file" } ] },
                            { text: "/var/run",   icon: "fa fa-folder-open", nodes: [ { text: "/run へのシンボリックリンク",                       icon: "fa fa-file" } ] },
                            { text: "/var/www",   icon: "fa fa-folder-open", nodes: [ { text: "Webサーバのドキュメントルート(ディストリビューション依存)", icon: "fa fa-file" } ] }
                        ]
                    },
                    {
                        text: "/lost+found",
                        icon: "fa fa-folder-open",
                        nodes: [
                            { text: "fsck が回収したファイル片の置き場", icon: "fa fa-file" }
                        ]
                    }
                ]
            }
        ];

    }
}

let linuxModel = new LinuxModel();