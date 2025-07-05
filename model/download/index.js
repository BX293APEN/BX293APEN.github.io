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
                "text"      : "&emsp;",
                "content"   : '<pre><code class="language-bash">sudo wget https://archive.kali.org/archive-keyring.gpg -O /usr/share/keyrings/kali-archive-keyring.gpg\nwget -q -O - https://archive.kali.org/archive-key.asc | apt-key add # old</code></pre>',
                
            },
        }
        this.dlIndex = Object.keys(this.dlData);
        this.dlIndex.sort();
    }
}

let dlModel = new DownloadModel();