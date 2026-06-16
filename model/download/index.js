class DownloadModel {
    constructor(){
        this.dlData = {
            "makeDL" : {
                "href"      : "https://gnuwin32.sourceforge.net/packages/make.htm",
                "imgSrc"    : "/img/CMake-Dark.svg", 
                "title"     : "Make for Windows",
                "text"      : "&emsp;makefileを利用することで、簡単にビルドが出来るようになります",
                "imgType"   : ".svg"
            },
            "vscodeDL" : {
                "href"      : "https://code.visualstudio.com/",
                "imgSrc"    : "/img/VSCode-Dark.svg", 
                "title"     : "Visual Studio Code",
                "text"      : "&emsp;VSCodeを利用して、様々な言語のデバッグをしてみましょう！",
                "imgType"   : ".svg"
            },
            "cpplib_ioset" : {
                "imgType"   : "none",
                "title"     : "CPPヘッダ (ioset.cpp)",
                "text"      : "&emsp;C++を扱いやすくするヘッダを作ってみました。(C++17以上推奨)",
                "content"   : '<pre><code class="language-bash">curl -OL https://bx293apen.github.io/html/download/content/ioset.cpp</code></pre>',
                
            },
            "kali_key" : {
                "imgType"   : "none",
                "title"     : "Kali Linux のアーカイブキーをシステムに追加する",
                "text"      : "&emsp;Kali Linuxの更新に失敗した時に試してみてください",
                "content"   : '<pre><code class="language-bash">sudo wget https://archive.kali.org/archive-keyring.gpg -O /usr/share/keyrings/kali-archive-keyring.gpg\nsudo wget -q -O - https://archive.kali.org/archive-key.asc | sudo apt-key add # old</code></pre>',
                
            },
            "eb" : {
                "imgType"   : ".svg",
                "imgSrc"    : "/img/DLC/eb.png", 
                "title"     : "EaseUS Todo Backup(旧バージョン)",
                "text"      : "&emsp;最新バージョンでは動かないOS用",
                "href"      : "/DLC/download/easeus-todo-backup-free-12-0-0.exe",
                
            },
            "epm" : {
                "imgType"   : ".svg",
                "imgSrc"    : "/img/DLC/epm.png", 
                "title"     : "EaseUS Partition Master(旧バージョン)",
                "text"      : "&emsp;最新バージョンでは動かないOS用",
                "href"      : "/DLC/download/epm.exe",
                
            },
            "MakeMKV_Beta_Key" : {
                "imgType"   : "none",
                "title"     : "MakeMKV Beta Key",
                "text"      : "&emsp;MakeMKVのBeta版ライセンスキーを取得する",
                "content"   : '<a href="https://cable.ayra.ch/makemkv/"><figcaption class = "btn btn-bd-primary figure-caption text-end">Get Key</figcaption></a>',
            },
            "Windows11_uupdump" : {
                "imgType"   : "none",
                "title"     : "Windows11 ISO",
                "text"      : "&emsp;Windows11のイメージを取得する",
                "content"   : '<a href="https://uupdump.net/known.php"><figcaption class = "btn btn-bd-primary figure-caption text-end">Get</figcaption></a>',
            },
            "net28cheat" : {
                "imgType"   : "none",
                "title"     : "Net24 → Net28",
                "text"      : "&emsp;dnsmasqの設定を変更するスクリプトのサンプル",
                "content"   : '<pre><code class="language-bash">curl -OL https://bx293apen.github.io/html/download/content/net28cheat.sh</code></pre>',
                
            },
            "vCenter" : {
                "imgType"   : "none",
                "title"     : "VMware vCenter Converter",
                "text"      : "&emsp;実機を仮想コンピュータにする",
                "content"   : '<a href="https://github.com/BX293APEN/DLC/releases/download/Release/VMware-converter-en-5.1.0-1087880.exe"><figcaption class = "btn btn-bd-primary figure-caption text-end">ver. 5.1.0</figcaption></a> <a href="https://github.com/BX293APEN/DLC/releases/download/ver.6.6/VMware-converter-en-6.6.0-23265344.exe"><figcaption class = "btn btn-bd-primary figure-caption text-end">ver. 6.6.0</figcaption></a>',
            },
            "7zip" : {
                "imgType"   : "none",
                "title"     : "7-Zip",
                "text"      : "&emsp;7-Zipのインストールリンク",
                "content"   : '<a href="https://www.7-zip.org/"><figcaption class = "btn btn-bd-primary figure-caption text-end">7-Zip</figcaption></a><br><br> <a href="https://7-zip.opensource.jp/"><figcaption class = "btn btn-bd-primary figure-caption text-end">7-Zip 日本語サイト</figcaption></a>',
            },
        }
        this.dlIndex = Object.keys(this.dlData);
        this.dlIndex.sort();
    }
}

let dlModel = new DownloadModel();