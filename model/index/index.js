class Model {
    constructor(){
        this.bookmarkData = {
            "GitHub" : {
                "href" : "https://github.com/BX293APEN",
            },
            "Bluesky" : {
                "href" : "https://bsky.app/profile/bx293apen.bsky.social"
            },
            "秋月電子通商" : {
                "href" : "https://akizukidenshi.com/catalog/default.aspx"
            },
            "Twitter" : { 
                "href" : "https://x.com/BX293A_PEN"
            },
            "X" : {
                "href" : "https://x.com/BX293A_PEN"
            },
            "YouTube" : { 
                "href" : "https://www.youtube.com/"
            },
            "Abema" : { 
                "href" : "https://abema.tv/"
            },
            "Amazon" : { 
                "href" : "https://www.amazon.co.jp/"
            },
            "価格.com" : { 
                "href" : "https://kakaku.com/"
            },
            "radiko" : { 
                "href" : "https://radiko.jp/#!/timetable"
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
            "chatgpt" : {
                "href" : "https://chatgpt.com/", 
            },
            "gemini" : {
                "href" : "https://gemini.google.com/app?hl=ja", 
            },
        }

        this.bookmarkIndex = Object.keys(this.bookmarkData);
        this.bookmarkIndex.sort();

    }
}

let model = new Model();