/**
 * @class AdCheck
 * 
 * @method run  
 * 実行方法 :  
 * ```JS
 *  (
 *      async () => { 
 *           await AdCheck.run();
 *      }
 *  )();
 * ```
 * @property (bool) AdCheck.adCheckFlag - 広告読み込み判定  
 * 広告読み込み成功 : true  
 * 広告読み込み失敗 : false
 * 
 */
class AdCheck {
    /**
     * @param {string} testUrl - 読み込みテストに使うスクリプトURL
     * @param {number} timeout - タイムアウト時間(ms)
     */
    constructor(
        testUrl = "https://example-ads-domain.invalid/ads.js", 
        timeout = 3000
    ) {
        this.testUrl        = testUrl;
        this.timeout        = timeout;
        this.adCheckFlag    = true;
    }

    async run() {
        const result        = await this.checkScriptLoad();
        if (!result) {
            this.adCheckFlag = false;
            console.log("広告がブロックされています");
        } 
        else {
            console.log("広告が正常に読み込まれました");
        }
    }

    checkScriptLoad() {
        return new Promise(
            (resolve) => {
                let resolved = false;
                const script = document.createElement("script");
                script.src = this.testUrl;

                script.onload = () => {
                    if (!resolved) {
                        resolved = true;
                        resolve(true);
                    }
                };
                script.onerror = () => {
                    if (!resolved) {
                        resolved = true;
                        resolve(false);
                    }
                };
                document.head.appendChild(script);
                // タイムアウト
                setTimeout(
                    () => {
                        if (!resolved) {
                            resolved = true;
                            resolve(false);
                        }
                    }, 
                    this.timeout
                );
            }
        );
    }
}