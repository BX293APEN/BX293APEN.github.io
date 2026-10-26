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
                "imgSrc"    : "https://github-readme-stats-private-eosin.vercel.app/api/pin/?username=BX293APEN&repo=Yocto_Docker", 
                "title"     : "Yocto Linux 自動ビルド",
                "text"      : "&emsp;Docker上でYocto Linuxを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "imgType"   : ".png",
                "dltext"    : "Learn More"
            },
            "LFS" : {
                "href"      : "https://github.com/BX293APEN/LFS_Docker",
                "imgSrc"    : "https://github-readme-stats-private-eosin.vercel.app/api/pin/?username=BX293APEN&repo=LFS_Docker", 
                "title"     : "Linux From Scratch 自動ビルド",
                "text"      : "&emsp;Docker上でLinux From Scratchを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "imgType"   : ".png",
                "dltext"    : "Learn More"
            },
            "OpenWrt" : {
                "href"      : "https://github.com/BX293APEN/OpenWrt_Docker",
                "imgSrc"    : "https://github-readme-stats-private-eosin.vercel.app/api/pin/?username=BX293APEN&repo=OpenWrt_Docker", 
                "imgType"   : ".png",
                "title"     : "OpenWrt 自動ビルド",
                "text"      : "&emsp;Docker上でOpenWrtを構築しUSBに焼くリポジトリです<br>リポジトリをクローンし、<code>docker compose up --build -d</code>を実行<br>寝ている間にrootfsが完成し、USBに焼けば起動できます",
                "dltext"    : "Learn More"
            },
            "Gentoo" : {
                "href"      : "https://github.com/BX293APEN/Gentoo_Docker",
                "imgSrc"    : "https://github-readme-stats-private-eosin.vercel.app/api/pin/?username=BX293APEN&repo=Gentoo_Docker", 
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