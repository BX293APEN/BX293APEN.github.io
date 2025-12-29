class MarkDownParent {
    constructor(
        id                      = "md-text"
    ) {
        this.id                 = id;
        this.afterDecorateFlag  = 0
    }

    decorate() {
        const md = document.getElementById(this.id);
        for (const element of md.querySelectorAll("table")) {
            if (! element.parentElement.classList.contains('table-responsive')) { 
                const divTag = document.createElement('div'); 
                divTag.classList.add("table-responsive"); 
                element.parentNode.insertBefore(divTag, element); 
                divTag.appendChild(element);
            } 
            element.classList.add("table", "table-bordered");
        }

        for (const element of md.querySelectorAll("td")) {
            element.classList.add("text-nowrap");
        }

        let h1Count = 0;
        let h2Count = 0;
        for (const element of md.querySelectorAll("h1, h2")) {
            element.classList.add("border-bottom");
            if (element.tagName.toLowerCase() === "h1") {
                h1Count++;
                h2Count = 0;
                element.id = `h${h1Count}`;
            
            } 
            else if (element.tagName.toLowerCase() === "h2") {
                h2Count++;
                element.id = `${h1Count}-${h2Count}`;
            }
        }

        hljs.highlightAll();
        this.afterDecorateFlag = 1;
    }

    jsLoad(src) {
        return new Promise(
            (resolve, reject) => {
                const scriptTag = document.createElement("script");
                scriptTag.src = src;
                scriptTag.onload = resolve;
                scriptTag.onerror = reject;
                document.head.appendChild(scriptTag);
            }
        );
    }
    waitForFlag(flagGetter, interval = 50) { 
        return new Promise(
            resolve => { 
                const timer = setInterval(
                    () => { 
                        if (flagGetter()) { 
                            clearInterval(timer); 
                            resolve(); 
                        } 
                    }, 
                    interval
                ); 
            }
        ); 
    }
}



class MarkDownLoader extends MarkDownParent {
    constructor(
        id              = "md-text",
        mdFile          = "/DLC/TA%E6%83%85%E5%A0%B1%E6%BC%94%E7%BF%92.md", 
        loadJS          = ["/view/highlight.min.js", "/view/marked.min.js"],
        option          = { gfm: true }
    ) {
        super(id);      // 最初に親コンストラクタを実行

        this.mdFile     = mdFile
        this.loadJS     = loadJS
        this.option     = option

        // constructor の this に固定したい場合はアロー関数が必須 
        Promise.all(
            this.loadJS.map(src => this.jsLoad(src))
        ).then(
            () => { 
                return fetch(this.mdFile); 
            }
        ).then(
            response => response.text()
        ).then(
            data => { 
                const mdHTML                                = marked.parse(data, this.option); 
                document.getElementById(this.id).innerHTML  = mdHTML; 
                this.decorate();
            }
        ).catch(
            error => console.error(
                "読み込みに失敗:", 
                error
            )
        );
    }
}

class MarkDownMaker extends MarkDownParent {
    constructor(
        id              = "md-text",
        loadJS          = ["/view/highlight.min.js", "/view/marked.min.js"],
        option          = { gfm: true }
    ) {
        super(id);      // 最初に親コンストラクタを実行
        
        this.loadJS     = loadJS
        this.option     = option

        // constructor の this に固定したい場合はアロー関数が必須 
        Promise.all(
            this.loadJS.map(src => this.jsLoad(src))
        ).then(
            () => { 
                const md                    = document.getElementById(this.id);
                const mdHTML                = marked.parse(md.innerText, this.option);
                md.innerHTML                = mdHTML; 
                this.decorate();
            }
        ).catch(
            error => console.error(
                "読み込みに失敗:", 
                error
            )
        );
    }
}

class MarkDownTOC {
    constructor(
        mdInstance,
        id              = "toc",
        mdid            = "md-text",
    ) {
        mdInstance.waitForFlag(
            () => mdInstance.afterDecorateFlag === 1
        ).then(
            () => { 
                this.buildTOC(id, mdid); 
            }
        );
    } 

    buildTOC(id, mdid) {
        const style = document.createElement("style");
        style.textContent = `
            #toc a {
                display: block;
                padding: 4px 0;
                text-decoration: none;
            }

            #toc .toc-h1 {
                font-weight: bold;
                margin-left: 0;
            }

            #toc .toc-h2 {
                margin-left: 1rem;
                font-size: 0.9em;
            }
        `
        document.head.appendChild(style);
        
        const toc           = document.getElementById(id);
        toc.innerHTML       = ""; 
        const md            = document.getElementById(mdid);
        for (const element of md.querySelectorAll("h1, h2")) { 
            const tag = element.tagName.toLowerCase(); 
            const aTag = document.createElement("a"); 
            aTag.href = `#${element.id}`; 
            aTag.textContent = element.textContent.trim(); 
            if (tag === "h1") { 
                aTag.classList.add("toc-h1"); 
            } 
            else if (tag === "h2") { 
                aTag.classList.add("toc-h2"); 
            } 
            toc.appendChild(aTag); 
        }
    }
}