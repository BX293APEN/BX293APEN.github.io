class TipsModel { // img src="https://skillicons.dev/icons?i=github"
    constructor(){
        this.tipsData = {
            "githubTip" : {
                "href"      : "/BX293APEN/github.html",
                "imgSrc"    : "/img/Github-Dark.svg", 
                "title"     : "GitHub",
                "text"      : "&emsp;Summary: How to use GitHub",
                "svg"       : true
                
            },
            "vimTip" : {
                "href"      : "/BX293APEN/vim.html",
                "imgSrc"    : "/img/VIM-Dark.svg", 
                "title"     : "Vim",
                "text"      : "&emsp;Want to learn Vim? <br>&emsp;This guide will help you understand.",
                "svg"       : true

            },
            "rn4020Tip" : {
                "href"      : "/html/tips/RN4020.html",
                "imgSrc"    : "/img/RN4020_design.jpg", 
                "title"     : "RN4020の簡易マニュアル",
                "text"      : "&emsp;RN4020は、マイクロチップ社によって開発されたBluetooth Low Energy(BLE)通信モジュールです",
                "svg"       : false

            },
            "linuxTip" : {
                "href"      : "/html/tips/linux.html",
                "imgSrc"    : "/img/Ubuntu-Dark.svg", 
                "title"     : "Debian系Linuxセットアップガイド",
                "text"      : "&emsp;Linuxを利用する上で、環境構築は非常に重要です",
                "svg"       : true

            },
            "pythonTip" : {
                "href"      : "/html/tips/python.html",
                "imgSrc"    : "/img/Python-Dark.svg", 
                "title"     : "Pythonの環境構築",
                "text"      : "&emsp;Pythonをセットアップし、より快適なプログラミング環境を試してみましょう！",
                "svg"       : true

            },
            "visualstudioTip" : {
                "href"      : "/html/tips/visualstudio.html",
                "imgSrc"    : "/img/VisualStudio-Dark.svg", 
                "title"     : "Visual Studioの利用方法",
                "text"      : "&emsp;フレームワークを利用することにより、大規模なソースコードの管理を容易にしましょう！",
                "svg"       : true

            },
            "cTip" :{
                "href"      : "/html/tips/c.html",
                "imgSrc"    : "/img/C.svg", 
                "title"     : "C/C++ Notes",
                "text"      : "&emsp;C言語を学ぶことで、コンピュータの深淵を覗くことが出来ます。",
                "svg"       : true
            },
            "asciiCodeTip" :{
                "href"      : "/html/tips/ascii-code.html",
                "imgSrc"    : "/img/bin.svg", 
                "title"     : "文字コード",
                "text"      : "&emsp;ASCIIコード表",
                "svg"       : true
            },
            "opencvTip" :{
                "href"      : "/BX293APEN/opencv.html",
                "imgSrc"    : "/img/OpenCV-Dark.svg", 
                "title"     : "OpenCV",
                "text"      : "&emsp;OpenCVを利用し、画像処理を行ってみましょう！",
                "svg"       : true
            },
            "windowsTip" :{
                "href"      : "/html/tips/windows.html",
                "imgSrc"    : "/img/Windows-Dark.svg", 
                "title"     : "Windows便利機能集",
                "text"      : "&emsp;Windowsの設定を変えて扱いやすくしましょう！",
                "svg"       : true
            },
            "serverTip" : {
                "href"      : "/html/tips/server.html",
                "imgSrc"    : "/img/RaspberryPi-Dark.svg", 
                "title"     : "サーバの構築",
                "text"      : "&emsp;インターネットを利用した便利なサービスを自分で実現してみましょう",
                "svg"       : true
            },
            "dockerTip" : {
                "href"      : "/html/tips/docker.html",
                "imgSrc"    : "/img/Docker.svg", 
                "title"     : "Dockerの使い方ガイド",
                "text"      : "&emsp;コンテナを利用し、仮想環境での開発に挑戦してみましょう！",
                "svg"       : true
            },
            "teratermTip" : {
                "href"      : "/html/tips/teraterm.html",
                "imgSrc"    : "/img/teraterm.png", 
                "title"     : "Tera Termのマクロについて",
                "text"      : "&emsp;マクロを利用することにより、高速なセットアップが可能となります",
                "svg"       : false
            },
            "UEFITip" : {
                "href"      : "/html/tips/UEFI.html",
                "imgSrc"    : "/img/asus-rog-1-logo.svg", 
                "title"     : "UEFI (AMD用)",
                "text"      : "&emsp;UEFI (BIOS)の設定を変更することで、最適なパフォーマンスでパソコンを動作させることが出来ます",
                "svg"       : true
            },
            "appTip" : {
                "href"      : "/html/tips/appbuild.html",
                "imgSrc"    : "/img/chrome.svg", 
                "title"     : "アプリのビルド",
                "text"      : "&emsp;オープンソースアプリを書き換え、独自のアプリケーションを作成してみましょう",
                "svg"       : true
            }

        }
        this.tipsIndex = Object.keys(this.tipsData);
        this.tipsIndex.sort();
    }
}

let tipsModel = new TipsModel();
model.bookmarkData = {...tipsModel.tipsData, ...model.bookmarkData}