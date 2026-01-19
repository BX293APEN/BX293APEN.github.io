class LoadModel {
    constructor() {
        this.cache = new Map();
    }

    js_load(src) {
        if (this.cache.has(src)) {
            return this.cache.get(src);
        }

        const existing = document.querySelector(`script[src="${src}"]`);
        if (existing) {
            if (!("loaded" in existing.dataset)) { 
                existing.dataset.loaded = "0"; 
            }
            if (existing.dataset.loaded == "1") {
                const p = Promise.resolve();
                this.cache.set(src, p);
                return p;
            }

            const p = new Promise(
                (resolve, reject) => {
                    existing.addEventListener(
                        "load", () => {
                            existing.dataset.loaded = "1";
                            resolve();
                        }
                    );
                    existing.addEventListener("error", reject);
                    setTimeout(
                        () => { 
                            existing.dataset.loaded = "1"; 
                            resolve(); 
                        }, 
                        300
                    );
                }
            );

            this.cache.set(src, p);
            return p;
        }

        const promise = new Promise(
            (resolve, reject) => {
                const script = document.createElement("script");
                script.src = src;
                script.dataset.loaded = "0";

                script.onload = () => {
                    script.dataset.loaded = "1";
                    resolve();
                };
                script.onerror = reject;

                document.head.appendChild(script);
            }
        );

        this.cache.set(src, promise);
        return promise;
    }
}



class Model extends LoadModel {
    constructor(
        otherModels = ["/model/tips/tips.js"]
    ){
        super();
        this.loadJS     = otherModels
        this.init();
        
        Promise.all(
            this.loadJS.map(src => this.js_load(src))
        ).then(
            () => { 
                this.merge();
            }
        ).catch(
            error => console.error(
                "読み込みに失敗:", 
                error
            )
        );
    }
    init(){
        this.sitemap        = {
            "home" : {
                "href" : "/",
            },
            "tips" : {
                "href" : "/html/tips/index.html",
            },
            "apps" : {
                "href" : "/html/app/index.html",
            },
            "アプリ" : {
                "href" : "/html/app/index.html",
            },
            "game" : {
                "href" : "/html/app/index.html",
            },
            "ゲーム" : {
                "href" : "/html/app/index.html",
            },
            "ブログ" : {
                "href" : "/html/blog/index.html",
            },
            "blog" : {
                "href" : "/html/blog/index.html",
            },
            "dlc" : {
                "href" : "/html/download/index.html",
            },
            "Downloads" : {
                "href" : "/html/download/index.html",
            },
            "ダウンロード" : {
                "href" : "/html/download/index.html",
            },
            "about" : {
                "href" : "/html/welcome.html",
            },
            "bios" : {
                "href" : "/html/tips/UEFI.html",
            },
            "appbuild" : {
                "href" : "/html/tips/appbuild.html",
            },
            "文字コード表" : {
                "href" : "/html/tips/ascii-code.html",
            },
            "C++CPPCLANGGCC" : {
                "href" : "/html/tips/c.html",
            },
            "C言語" : {
                "href" : "/html/tips/c.html",
            },
            "msquic" : {
                "href" : "/html/tips/c-lang/msquic.html",
            },
            "ネットワーク" : {
                "href" : "/html/tips/linux/network.html",
            },
            "network" : {
                "href" : "/html/tips/linux/network.html",
            },
            "firewall" : {
                "href" : "/html/tips/linux/network.html",
            },
            "nat" : {
                "href" : "/html/tips/linux/network.html",
            },
            "iptablesnftables" : {
                "href" : "/html/tips/linux/network.html",
            },
            "nmtuinmcli" : {
                "href" : "/html/tips/linux/network.html",
            },
            "raspiraspipicoW" : {
                "href" : "/html/tips/linux/raspi.html",
            },
            "ラズパイ" : {
                "href" : "/html/tips/linux/raspi.html",
            },
            "Wine11.0" : {
                "href" : "/html/tips/linux/config.html",
            },
            "node-red" : {
                "href" : "/html/tips/linux/config.html",
            },
            "trim" : {
                "href" : "/html/tips/linux/config.html",
            },
            "daemon" : {
                "href" : "/html/tips/linux/daemon.html",
            },
            "自動起動" : {
                "href" : "/html/tips/linux/daemon.html",
            },
            "systemctl" : {
                "href" : "/html/tips/linux/daemon.html",
            },
            "format" : {
                "href" : "/html/tips/linux/format.html",
            },
            "wsl" : {
                "href" : "/html/tips/windows/wsl.html",
            },
            "emqxmqtt" : {
                "href" : "/html/tips/server.html",
            },
            "lanutprj45" : {
                "href" : "/html/tips/server.html",
            },
            "dnsbind9" : {
                "href" : "/html/tips/server/dns.html",
            },
            "vsftpdsmbnas" : {
                "href" : "/html/tips/server/ftp.html",
            },
            "nginxdjangocgihttp" : {
                "href" : "/html/tips/server/http.html",
            },
            "chronyntp" : {
                "href" : "/html/tips/server/ntp.html",
            },
            "vnc" : {
                "href" : "/html/tips/server/vnc.html",
            },
        }

        this.sitemapIndex = Object.keys(this.sitemap);
        this.sitemapIndex.sort();


        this.bookmarkData   = {
            "chatgpt" : {
                "href" : "https://chatgpt.com/", 
            },
            "gemini" : {
                "href" : "https://gemini.google.com/app?hl=ja", 
            },
            "Bluesky" : {
                "href" : "https://bsky.app/profile/bx293apen.bsky.social"
            },
            "Twitter" : { 
                "href" : "https://x.com/BX293A_PEN"
            },
            "X.com" : {
                "href" : "https://x.com/BX293A_PEN"
            },
            "ポミュ" : { 
                "href" : "https://ch.dlsite.com/pommu/profile/3945756"
            },
            "pommu" : {
                "href" : "https://ch.dlsite.com/pommu/profile/3945756"
            },
            "YouTube" : { 
                "href" : "https://www.youtube.com/"
            },
            "Abema" : { 
                "href" : "https://abema.tv/"
            },
            "radiko" : { 
                "href" : "https://radiko.jp/#!/timetable"
            },
            "Amazon" : { 
                "href" : "https://www.amazon.co.jp/"
            },
            "秋月電子通商" : {
                "href" : "https://akizukidenshi.com/catalog/default.aspx"
            },
            "価格.com" : { 
                "href" : "https://kakaku.com/"
            },
            "セキュリティソフト比較" : { 
                "href" : "https://www.av-comparatives.org/"
            },
            "CPU" : { 
                "href" : "https://pcfreebook.com/article/450856544.html"
            },
            "lCPU" : { 
                "href" : "https://pcfreebook.com/article/458775622.html"
            },
            "phone" : { 
                "href" : "https://pcfreebook.com/article/smartfone-cpu-list.html"
            },
            "GPU" : { 
                "href" : "https://pcfreebook.com/article/459993300.html"
            },
            'Gmail' : {
                "href" : "https://mail.google.com/mail/u/0/#inbox", 
            },
            'Google' : {
                "href" : "https://www.google.co.jp", 
            },
            '画像検索' : {
                "href" : "https://www.google.co.jp/imghp?hl=ja&tab=ri&authuser=0&ogbl", 
            },
            'Google翻訳' : {
                "href" : "https://translate.google.com/?lfhs=2", 
            },
            'Google map' : {
                "href" : "https://www.google.com/maps?force=tt&source=ttpwa", 
            },
            'Google Earth' : {
                "href" : "https://earth.google.com/web/?authuser=0", 
            },
            '回線速度測定' : {
                "href" : "https://fast.com/ja/#", 
            },
            'Yahoo finance' : {
                "href" : "https://finance.yahoo.com/", 
            },
            'TIMEIS' : {
                "href" : "https://time.is/ja/", 
            },
            "num" : {
                "href" : "https://ja.numberempire.com/9018421", 
            },
            "J-PlatPat" : {
                "href" : "https://www.j-platpat.inpit.go.jp/t0100", 
            },
            
        }

        this.bookmarkIndex = Object.keys(this.bookmarkData);
        this.bookmarkIndex.sort();

    }
    merge(){
        this.bookmarkData = {...tipsModel.tipsData, ...this.sitemap,...this.bookmarkData}
    }
}

let model = new Model();