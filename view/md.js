class MarkDownLoader {
    constructor(
        id              = "md-text",
        mdFile          = "/DLC/TA%E6%83%85%E5%A0%B1%E6%BC%94%E7%BF%92.md", 
        loadJS          = ["/view/highlight.min.js", "/view/marked.min.js"]
    ) {
        this.id         = id
        this.mdFile     = mdFile
        this.loadJS     = loadJS
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
                const mdHTML = marked.parse(data); 
                document.getElementById(this.id).innerHTML = mdHTML; 
                const tables = document.getElementById(this.id).querySelectorAll("table"); 
                for (const table of tables) { 
                    table.classList.add("table-bordered"); 
                } 
                hljs.highlightAll(); 
            }
        ).catch(
            error => console.error(
                "読み込みに失敗:", 
                error
            )
        );
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
}

class MarkDownMaker {
    constructor(
        id              = "md-text",
        loadJS          = ["/view/highlight.min.js", "/view/marked.min.js"]
    ) {
        this.id         = id
        this.loadJS     = loadJS
        // constructor の this に固定したい場合はアロー関数が必須 
        Promise.all(
            this.loadJS.map(src => this.jsLoad(src))
        ).then(
            () => { 
                const md                    = document.getElementById(this.id)
                const mdHTML                = marked.parse(md.innerText);
                md.innerHTML                = mdHTML; 
                const tables                = md.querySelectorAll("table"); 
                for (const table of tables) { 
                    table.classList.add("table-bordered"); 
                } 
                hljs.highlightAll(); 

            }
        ).catch(
            error => console.error(
                "読み込みに失敗:", 
                error
            )
        );
    }

    jsLoad(src) {
        return new Promise(
            (resolve, reject) => {
                const scriptTag     = document.createElement("script");
                scriptTag.src       = src;
                scriptTag.onload    = resolve;
                scriptTag.onerror   = reject;
                document.head.appendChild(scriptTag);
            }
        );
    }
}