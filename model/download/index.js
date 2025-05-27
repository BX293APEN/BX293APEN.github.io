class DownloadModel {
    constructor(){
        this.dlData = {
            "makeDL" : {
                "href"      : "https://gnuwin32.sourceforge.net/packages/make.htm",
                "imgSrc"    : "/img/CMake-Dark.svg", 
                "title"     : "Make for Windows",
                "text"      : "&emsp;makefileを利用することで、簡単にビルドが出来るようになります",
            },
            "vscodeDL" : {
                "href"      : "https://code.visualstudio.com/",
                "imgSrc"    : "/img/VSCode-Dark.svg", 
                "title"     : "Visual Studio Code",
                "text"      : "&emsp;VSCodeを利用して、様々な言語のデバッグをしてみましょう！",
            },
        }
        this.dlIndex = Object.keys(this.dlData);
        this.dlIndex.sort();
    }
}

let dlModel = new DownloadModel();