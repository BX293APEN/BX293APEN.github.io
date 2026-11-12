class MermaidUML{
    constructor (
        {
            umlPlace, 
            umlSource, 
            dl, 
            umlName
        }={}
    ){
        this.uml    = document.getElementById(umlPlace);
        this.src    = document.getElementById(umlSource);
        this.dl     = document.getElementById(dl);
        this.name   = umlName;
        this.src.addEventListener(
            'keydown', 
            this.key_press.bind(this)
        );
        mermaid.initialize(
            {
                startOnLoad     : true,
            }
        );
        this.draw();
        this.dl.addEventListener(
            'click', 
            () => {
                this.download_svg();
            }
            
        );
    }
    draw(){
        this.uml.removeAttribute('data-processed');
        this.uml.textContent = this.src.value;
        mermaid.init();
    }

    key_press(pressKey){
        if (pressKey.key === "Enter") {
            this.draw()
        }
    }
    download_svg() {
        // svg要素を取得
        let svgNode = this.uml.querySelector("svg");
        let svgText = new XMLSerializer().serializeToString(svgNode);
        let svgBlob = new Blob(
            [svgText], 
            { 
                type: 'image/svg+xml;charset=utf-8' 
            }
        );
        let svgUrl = URL.createObjectURL(svgBlob);
      
        // a要素を作ってダウンロード
        let a = document.createElement('a');
        a.href = svgUrl;
        a.download = `${this.name}.svg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(svgUrl);
    }
      
}

// new MermaidUML("drawUML", "sourceUML", "umlDownload", "uml");


/**
 * # MermaidUMLByClass
 *
 * 指定した HTML の class 名を持つ要素すべてについて、
 * 要素内の Mermaid 記法の文字列を UML(SVG) に変換するクラス。
 *
 * ## コンストラクタ引数 (オブジェクト)
 *
 * | 引数 | 型 | 既定値 | 説明 |
 * |------|----|--------|------|
 * | `className` | `string` | `"mermaid-src"` | 変換対象の class 名(`.` は付けない) |
 * | `root` | `ParentNode` | `document` | 検索範囲 |
 *
 * ## メンバ変数
 *
 * | 名前 | 型 | 説明 |
 * |------|----|------|
 * | `className` | `string` | 変換対象の class 名 |
 * | `root` | `ParentNode` | 検索範囲 |
 * | `nodes` | `HTMLElement[]` | 変換対象の要素一覧 |
 *
 * ## メソッド
 *
 * | 名前 | 引数 | 戻り値 | 説明 |
 * |------|------|--------|------|
 * | `draw()` | なし | `Promise<void>` | 対象要素を順に UML へ変換する |
 * | `redraw()` | なし | `Promise<void>` | 要素を再検索し、保存済みソースから描き直す |
 * | `uniqueMarkers(el)` | `HTMLElement` | `void` | 描いた図の矢印の先端(`<marker>`)の ID を、図ごとに重複しないよう付け替える |
 *
 * ## 補足
 *
 * - 元の文字列は `data-mermaid-src` 属性に保存される
 * - 対象 class に `mermaid` は使わないこと(`startOnLoad` による自動処理と競合する)
 * - Mermaid のバージョンによっては、シーケンス図の矢印の先端(`arrowhead` など)の ID が全図で同じになる。
 *   ID が重複すると、最初の図が `display: none`(絞り込みで行を隠す等)になったとき、他の図の矢印の先端も消える。
 *   そのため描画のたびに `uniqueMarkers` で ID を図ごとに付け替える
 *
 * ## 使用例
 *
 * ```html
 * <pre class="uml">
 * classDiagram
 *   Animal <|-- Dog
 * </pre>
 * <script>new MermaidUMLByClass({ className: "uml" });</script>
 * ```
 */
class MermaidUMLByClass{
    static svgSeq = 0;   // marker の ID の接頭辞に使う通し番号(インスタンスをまたいで重複させない)

    constructor (
        {
            className = "mermaid-src",
            root      = document
        } = {}
    ){
        this.className = className;
        this.root      = root;
        this.nodes     = [];
        mermaid.initialize(
            {
                startOnLoad : false,
            }
        );
        this.draw();
    }

    async draw(){
        this.nodes = Array.from(
            this.root.querySelectorAll(`.${this.className}`)
        );
        for (const el of this.nodes) {
            // 初回はソースを退避、再描画時は退避済みのソースを使う
            if (el.dataset.mermaidSrc === undefined) {
                el.dataset.mermaidSrc = el.textContent.trim();
            }
            const source = el.dataset.mermaidSrc;

            el.textContent = source;
            el.classList.add("mermaid");
            el.removeAttribute("data-processed");
            try {
                if (typeof mermaid.run === "function") {
                    await mermaid.run({ nodes: [el] });   // Mermaid v10 以降
                } else {
                    mermaid.init(undefined, el);          // Mermaid v9 以前
                }
                this.uniqueMarkers(el);
            } catch (err) {
                // 失敗した要素は元の文字列に戻して続行
                console.error("Mermaid の変換に失敗しました:", err, el);
                el.classList.remove("mermaid");
                el.textContent = source;
            }
        }
    }

    redraw(){
        return this.draw();
    }

    uniqueMarkers(el){
        el.querySelectorAll("svg").forEach((svg) => {
            const markers = svg.querySelectorAll("marker[id]");
            if (!markers.length) return;
            const prefix = `uml${++MermaidUMLByClass.svgSeq}-`;
            const ids    = new Map([...markers].map((m) => [m.id, prefix + m.id]));
            const rename = (s) => s.replace(
                /url\(\s*(['"]?)#([^'")\s]+)\1\s*\)/g,
                (all, q, id) => ids.has(id) ? `url(${q}#${ids.get(id)}${q})` : all
            );
            svg.querySelectorAll("*").forEach((node) => {
                ["marker-start", "marker-mid", "marker-end", "style"].forEach((a) => {
                    const v = node.getAttribute(a);
                    if (v && v.includes("url(")) node.setAttribute(a, rename(v));
                });
                if (node.tagName.toLowerCase() === "style") node.textContent = rename(node.textContent);
            });
            markers.forEach((m) => { m.id = ids.get(m.id); });
        });
    }
}

// new MermaidUMLByClass({ className: "mermaid-src" });