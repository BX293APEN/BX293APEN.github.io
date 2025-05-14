class TipsModel {
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
            }

        }
        this.tipsIndex = Object.keys(this.tipsData);
        this.tipsIndex.sort();
    }
}

tipsModel = new TipsModel();
