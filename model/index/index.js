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
            "unv" :  {
                "href" : "https://kyomuportal.daido-it.ac.jp/uniprove_pt/"
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
        }

        this.bookmarkIndex = Object.keys(this.bookmarkData);
        this.bookmarkIndex.sort();

        this.areaID = [
            {"name" : "北海道", "id" : "016000"},
            {"name" : "青森県", "id" : "020000"},
            {"name" : "秋田県", "id" : "050000"},
            {"name" : "岩手県", "id" : "030000"},
            {"name" : "宮城県", "id" : "040000"},
            {"name" : "山形県", "id" : "060000"},
            {"name" : "福島県", "id" : "070000"},
            {"name" : "茨城県", "id" : "080000"},
            {"name" : "栃木県", "id" : "090000"},
            {"name" : "群馬県", "id" : "100000"},
            {"name" : "埼玉県", "id" : "110000"},
            {"name" : "東京都", "id" : "130000"},
            {"name" : "千葉県", "id" : "120000"},
            {"name" : "神奈川県", "id" : "140000"},
            {"name" : "長野県", "id" : "200000"},
            {"name" : "山梨県", "id" : "190000"},
            {"name" : "静岡県", "id" : "220000"},
            {"name" : "愛知県", "id" : "230000"},
            {"name" : "岐阜県", "id" : "210000"},
            {"name" : "三重県", "id" : "240000"},
            {"name" : "新潟県", "id" : "150000"},
            {"name" : "富山県", "id" : "160000"},
            {"name" : "石川県", "id" : "170000"},
            {"name" : "福井県", "id" : "180000"},
            {"name" : "滋賀県", "id" : "250000"},
            {"name" : "京都府", "id" : "260000"},
            {"name" : "大阪府", "id" : "270000"},
            {"name" : "兵庫県", "id" : "280000"},
            {"name" : "奈良県", "id" : "290000"},
            {"name" : "和歌山県", "id" : "300000"},
            {"name" : "岡山県", "id" : "330000"},
            {"name" : "広島県", "id" : "340000"},
            {"name" : "島根県", "id" : "320000"},
            {"name" : "鳥取県", "id" : "310000"},
            {"name" : "徳島県", "id" : "360000"},
            {"name" : "香川県", "id" : "370000"},
            {"name" : "愛媛県", "id" : "380000"},
            {"name" : "高知県", "id" : "390000"},
            {"name" : "山口県", "id" : "350000"},
            {"name" : "福岡県", "id" : "400000"},
            {"name" : "大分県", "id" : "440000"},
            {"name" : "長崎県", "id" : "420000"},
            {"name" : "佐賀県", "id" : "410000"},
            {"name" : "熊本県", "id" : "430000"},
            {"name" : "宮崎県", "id" : "450000"},
            {"name" : "鹿児島県", "id" : "460100"},
            {"name" : "沖縄県", "id" : "471000"},
        ]
    }
}

model = new Model();

   