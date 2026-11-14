class LoadModel {
    constructor() {
        this.cache = new Map();
    }

    js_load(src) {
        if (this.cache.has(src)) {
            return this.cache.get(src);
        }

        const existing = document.querySelector(`script[src="${src}"]`);
        if (existing) {
            if (!("loaded" in existing.dataset)) { 
                existing.dataset.loaded = "0"; 
            }
            if (existing.dataset.loaded == "1") {
                const p = Promise.resolve();
                this.cache.set(src, p);
                return p;
            }

            const p = new Promise(
                (resolve, reject) => {
                    existing.addEventListener(
                        "load", () => {
                            existing.dataset.loaded = "1";
                            resolve();
                        }
                    );
                    existing.addEventListener("error", reject);
                    setTimeout(
                        () => { 
                            existing.dataset.loaded = "1"; 
                            resolve(); 
                        }, 
                        300
                    );
                }
            );

            this.cache.set(src, p);
            return p;
        }

        const promise = new Promise(
            (resolve, reject) => {
                const script = document.createElement("script");
                script.src = src;
                script.dataset.loaded = "0";

                script.onload = () => {
                    script.dataset.loaded = "1";
                    resolve();
                };
                script.onerror = reject;

                document.head.appendChild(script);
            }
        );

        this.cache.set(src, promise);
        return promise;
    }
}



class Model extends LoadModel {
    constructor(
        otherModels = ["/model/index/sitemap.js"]
    ){
        super();
        this.loadJS     = otherModels
        this.init();
        
        Promise.all(
            this.loadJS.map(src => this.js_load(src))
        ).then(
            () => { 
                this.merge();
            }
        ).catch(
            error => console.error(
                "読み込みに失敗:", 
                error
            )
        );
    }
    init(){
        
    }
    merge(){
        // this.bookmarkData = {...tipsModel.tipsData, ...this.sitemap,...this.bookmarkData}
        this.bookmarkData = sitemap;
    }
}

let model = new Model();