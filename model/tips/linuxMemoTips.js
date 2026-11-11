class LinuxMemoModel{
    constructor(){
        this.page =[
            {
                "page" : 1,
                "href" : "/html/tips/linuxMemo.html"
            },
            {
                "page" : 2,
                "href" : "/html/tips/linuxMemo/repo.html"
            },
        ]
        this.dlData = {
            "Yocto" : {
                "href"      : "https://github.com/BX293APEN/Yocto_Docker",
                "imgSrc"    : "/img/linuxMemo/Yocto_Docker.png", 
                "title"     : "Yocto Linux 自動ビルド",
                "text"      : "&emsp;Docker上でYocto Linuxを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "imgType"   : ".png",
                "dltext"    : "Learn More"
            },
            "LFS" : {
                "href"      : "https://github.com/BX293APEN/LFS_Docker",
                "imgSrc"    : "/img/linuxMemo/LFS_Docker.png", 
                "title"     : "Linux From Scratch 自動ビルド",
                "text"      : "&emsp;Docker上でLinux From Scratchを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "imgType"   : ".png",
                "dltext"    : "Learn More"
            },
            "OpenWrt" : {
                "href"      : "https://github.com/BX293APEN/OpenWrt_Docker",
                "imgSrc"    : "/img/linuxMemo/OpenWrt_Docker.png", 
                "imgType"   : ".png",
                "title"     : "OpenWrt 自動ビルド",
                "text"      : "&emsp;Docker上でOpenWrtを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "dltext"    : "Learn More"
            },
            "Gentoo" : {
                "href"      : "https://github.com/BX293APEN/Gentoo_Docker",
                "imgSrc"    : "/img/linuxMemo/Gentoo_Docker.png", 
                "imgType"   : ".png",
                "title"     : "Gentoo Linux 自動ビルド",
                "text"      : "&emsp;Docker上でGentoo Linuxを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "dltext"    : "Learn More"
            },
            
        }
        this.dlIndex = Object.keys(this.dlData);
        this.dlIndex.sort();
    }
}

let linuxMemoModel = new LinuxMemoModel();