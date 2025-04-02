const quickOptions = [
    {
        "value":"", 
        "name" : "選択"
    },
    {
        "value":"settings", 
        "name" : "設定"
    },
    {
        "value":"raspi", 
        "name" : "Raspberry Pi"
    },
    {
        "value":"linux", 
        "name" : "Debian系Linux"
    },
    {
        "value":"centos", 
        "name" : "Red Hat系Linux"
    },
    {
        "value":"GitHub", 
        "name" : "GitHub"
    },
    {
        "value":"converter", 
        "name" : "ファイル変換"
    },
    {
        "value":"media", 
        "name" : "メディアツール"
    },
    {
        "value":"game", 
        "name" : "ゲーム"
    },
    {
        "value":"guide", 
        "name" : "ゲーム攻略"
    },
    {
        "value":"tools", 
        "name" : "ツール"
    },
    {
        "value":"cmd", 
        "name" : "コマンドプロンプト"
    },
    {
        "value":"DB", 
        "name" : "MySQL"
    },
    {
        "value":"regedit",
        "name" : "レジストリ"
    },
]

const quickAccessList = [
    {
        "src" : "icon/chrome.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"リモートデスクトップ", 
        "value" : "https://remotedesktop.google.com/"
    },
    {
        "src" : "icon/twitter.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Bluesky", 
        "value" : "https://bsky.app/profile/bx293apen.bsky.social"
    },
    {
        "src" : "icon/twitter.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Twitter", 
        "value" : "https://x.com/BX293A_PEN"
    },
    {
        "src" : "icon/twitter.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Twitter ブックマーク", 
        "value" : "https://x.com/i/bookmarks"
    },
    {
        "src" : "icon/twitterdev.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Twitter Dev", 
        "value" : "https://developer.twitter.com/en/portal/petition/essential/basic-info"
    },
    {
        "src" : "icon/game.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Discord Dev", 
        "value" : "https://discord.com/developers/applications/823545989616238632/information"
    },
    {
        "src" : "icon/game.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"IFTTT", 
        "value" : "https://ifttt.com/explore"},
    {
        "src" : "icon/IE.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"ログイン", 
        "value" : "https://kyomuportal.daido-it.ac.jp/uniprove_pt/"
    },
    {
        "src" : "icon/youtube.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"YouTube", 
        "value" : "https://www.youtube.com/"
    },
    {
        "src" : "icon/abema.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Abema", 
        "value" : "https://abema.tv/"
    },
    {
        "src" : "icon/win11.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Windows Insider Blog", 
        "value" : "https://blogs.windows.com/windows-insider?s=&submit=Search"
    },
    {
        "src" : "icon/windows.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Microsoft アカウント情報", 
        "value" : "https://account.microsoft.com/services/microsoft365/details?OCID=PROD_OFFICE_CONS_UNIPUX&refd=setup.office.com#"
    },
    {
        "src" : "icon/office.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Office", 
        "value" : "https://www.office.com/?auth=2"
    },
    {
        "src" : "icon/amazon.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"Amazon", 
        "value" : "https://www.amazon.co.jp/"
    },
    {
        "src" : "icon/amazon.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"価格.com", 
        "value" : "https://kakaku.com/"
    },
    {
        "src" : "icon/chrome.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"radiko(ラジコ)", 
        "value" : "https://radiko.jp/#!/timetable"
    },
    {
        "src" : "icon/avc.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"セキュリティソフト比較", 
        "value" : "https://www.av-comparatives.org/"
    },
    {
        "src" : "icon/cpu.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"デスクトップPC用CPU比較", 
        "value" : "https://pcfreebook.com/article/450856544.html"
    },
    {
        "src" : "icon/laptop.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"ノートPC用CPU比較", 
        "value" : "https://pcfreebook.com/article/458775622.html"
    },
    {
        "src" : "icon/wsa.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"スマホ用CPU比較", 
        "value" : "https://pcfreebook.com/article/smartfone-cpu-list.html"
    },
    {
        "src" : "icon/cpu.ico", 
        "height" :"32px", 
        "width" :"32px", 
        "title" :"GPU（グラフィックボード）性能比較表", 
        "value" : "https://pcfreebook.com/article/459993300.html"
    },
]