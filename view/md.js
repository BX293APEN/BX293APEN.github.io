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
            if (element.tagName.toLowerCase() == "h1") {
                h1Count++;
                h2Count = 0;
                element.id = `article${h1Count}`;
            
            } 
            else if (element.tagName.toLowerCase() == "h2") {
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
                let preScriptTag = document.querySelector(`script[src="${src}"]`);

                if (preScriptTag) {
                    if(preScriptTag.dataset.loaded == "1"){
                        resolve();
                    }
                    else{
                        if (!("loaded" in preScriptTag.dataset)) {  // 直コード処理
                            preScriptTag.dataset.loaded = "0";
                        }

                        
                        preScriptTag.addEventListener(              // 読み込み終了まで待機
                            "load",
                            () => {
                                preScriptTag.dataset.loaded = "1";
                                resolve();
                            }
                        );

                        preScriptTag.addEventListener(
                            "error",
                            reject
                        );

                    }
                }
                else{
                    const scriptTag             = document.createElement("script");
                    scriptTag.dataset.loaded    = "0";
                    scriptTag.src               = src;
                    scriptTag.addEventListener(
                        "load", 
                        () => { 
                            scriptTag.dataset.loaded = "1"; 
                            resolve(); 
                        }
                    );
                    scriptTag.addEventListener(
                        "error", 
                        reject, 
                    );
                    document.head.appendChild(scriptTag);
                }
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
        option          = { gfm: true },
        mdInstance      = null,
    ) {
        super(id);      // 最初に親コンストラクタを実行

        this.mdFile     = mdFile
        this.loadJS     = loadJS
        this.option     = option

        if(mdInstance){
            mdInstance.waitForFlag(
                () => mdInstance.afterDecorateFlag == 1
            ).then(
                () => { 
                    this.init(); 
                }
            );
        }
        else{
            this.init(); 
        }
    }

    init(){
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
        option          = { gfm: true },
        mdInstance      = null,
    ) {
        super(id);      // 最初に親コンストラクタを実行
        
        this.loadJS     = loadJS
        this.option     = option

        if(mdInstance){
            mdInstance.waitForFlag(
                () => mdInstance.afterDecorateFlag == 1
            ).then(
                () => { 
                    this.init(); 
                }
            );
        }
        else{
            this.init(); 
        }
    }
    init(){
        // constructor の this に固定したい場合はアロー関数が必須 
        Promise.all(
            this.loadJS.map(src => this.jsLoad(src))
        ).then(
            () => { 
                const md                    = document.getElementById(this.id);
                const mdHTML                = marked.parse(this.md_format(md.innerHTML), this.option);
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

    md_format(mdText){
        let value = mdText.replace(/^&(gt|#62); /gm, ">");
        
        return value
    }
}

class MarkDownTOC {
    constructor(
        mdInstance      = null,
        id              = "toc",
        mdid            = "md-text",
    ) {
        if(mdInstance){
            mdInstance.waitForFlag(
                () => mdInstance.afterDecorateFlag == 1
            ).then(
                () => { 
                    this.build_toc(id, mdid); 
                }
            );
        }
    } 

    build_toc(id, mdid) {
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
            
            blockquote {
                border-left: 5px solid #d1d9e0;
                padding: 10px;
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
            if (tag == "h1") { 
                aTag.classList.add("toc-h1"); 
            } 
            else if (tag == "h2") { 
                aTag.classList.add("toc-h2"); 
            } 
            toc.appendChild(aTag); 
        }
    }
}