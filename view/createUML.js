/**
 * # DownloadFile
 *
 * ボタンのクリックでファイルをダウンロードさせるクラス。
 *
 * ## コンストラクタ引数
 *
 * | 引数 | 型 | 既定値 | 説明 |
 * |------|----|--------|------|
 * | `placeID` | `string` | (必須) | クリックを受けるボタンの ID |
 * | `content` | `string \| (() => string)` | (必須) | ファイルの中身。関数ならクリックのたびに呼び出す |
 * | `fileName` | `string` | (必須) | 保存するファイル名 |
 * | `mimeType` | `string` | `"text/plain"` | MIME タイプ |
 *
 * ## メンバ変数
 *
 * | 名前 | 型 | 説明 |
 * |------|----|------|
 * | `btn` | `HTMLElement` | クリックを受けるボタン |
 * | `content` | `string \| (() => string)` | ファイルの中身、またはそれを返す関数 |
 * | `fileName` | `string` | 保存するファイル名 |
 * | `mimeType` | `string` | MIME タイプ |
 *
 * ## メソッド
 *
 * | 名前 | 引数 | 戻り値 | 説明 |
 * |------|------|--------|------|
 * | `download()` | なし | `void` | `File` を作ってダウンロードする |
 * | `static save(file)` | `File \| Blob` と `string`(任意) | `void` | 与えられた `File` / `Blob` をダウンロードさせる(PNG 保存でも使う) |
 */
class DownloadFile{
    constructor (
        placeID,
        content,
        fileName,
        mimeType = "text/plain"
    ){
        this.btn      = document.getElementById(placeID);
        this.content  = content;
        this.fileName = fileName;
        this.mimeType = mimeType;
        this.btn.addEventListener(
            "click", () => {
                this.download();
            }
        );
    }
    download(){
        // 関数なら、クリックした時点の内容を取得する
        const body = typeof this.content === "function"
            ? this.content()
            : this.content;
        const file = new File([body], this.fileName, { type: this.mimeType });
        DownloadFile.save(file);
    }
    static save(file, fileName = file.name){
        const url  = URL.createObjectURL(file);
        const a    = document.createElement("a");
        a.href     = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}


/**
 * # UMLClickAction
 *
 * UML(Mermaid の描画結果)を左クリック・右クリックした時の動作を決めるクラス。
 * 標準動作は、右クリックでコピー用メニューを表示(左クリックは誤操作防止のため何もしない)。
 *
 * ## コンストラクタ引数 (オブジェクト)
 *
 * | 引数 | 型 | 既定値 | 説明 |
 * |------|----|--------|------|
 * | `target` | `HTMLElement \| Document` | (必須) | クリックを受ける要素(UML の描画先)。`selector` を使う場合は、その親(`document` など) |
 * | `getSource` | `(el: HTMLElement) => string` | (必須) | クリック時点の Mermaid コードを返す関数。`el` はクリックされた UML の要素 |
 * | `selector` | `string \| null` | `null` | 指定すると `target` 内で一致する要素へのクリックだけを受ける(イベント委譲)。後から作り直された要素にも効く |
 * | `left` | `string \| function` | `"none"` | 左クリック時の動作(下表) |
 * | `right` | `string \| function` | `"menu"` | 右クリック時の動作(下表) |
 * | `menuItems` | `{label: string, run: (ctx) => void}[]` | `[]` | コンテキストメニューに追加する項目 |
 * | `notify` | `boolean` | `true` | コピー結果を画面右下に短く表示するか |
 * | `debug` | `boolean` | `false` | `true` にすると、クリックを受けた時・対象が見つからなかった時にコンソールへ出力する(原因調べ用) |
 *
 * ## `left` / `right` に指定できる値
 *
 * | 値 | 動作 |
 * |----|------|
 * | `"none"` | 何もしない(右クリックの場合はブラウザ標準のメニューを残す) |
 * | `"copy"` | Mermaid コードをそのままクリップボードにコピー |
 * | `"menu"` | コンテキストメニューを表示(標準項目は「Mermaid コードをコピー」) |
 * | `function(ctx)` | 独自処理。`ctx` は下表 |
 *
 * ## `ctx` の中身
 *
 * | 名前 | 型 | 説明 |
 * |------|----|------|
 * | `el` | `HTMLElement` | クリックされた UML の要素(`selector` 指定時は一致した要素) |
 * | `source` | `string` | クリック時点の Mermaid コード |
 * | `event` | `MouseEvent` | 元のイベント |
 * | `action` | `UMLClickAction` | このオブジェクト自身 |
 *
 * ## メンバ変数
 *
 * | 名前 | 型 | 説明 |
 * |------|----|------|
 * | `target` | `HTMLElement \| Document` | クリックを受ける要素 |
 * | `getSource` | `(el) => string` | Mermaid コードを返す関数 |
 * | `selector` | `string \| null` | 委譲用のセレクタ |
 * | `left` / `right` | `string \| function` | 左・右クリックの動作 |
 * | `menuItems` | `object[]` | 追加メニュー項目 |
 * | `notify` | `boolean` | 結果表示の有無 |
 *
 * ## メソッド
 *
 * | 名前 | 引数 | 戻り値 | 説明 |
 * |------|------|--------|------|
 * | `find(e)` | `MouseEvent` | `HTMLElement \| null` | クリックされた UML の要素を返す。対象外なら `null`(`composedPath()` をたどるので、深い階層や Shadow DOM の中でも探せる) |
 * | `copy(el)` | `HTMLElement`(省略時は `target`) | `Promise<boolean>` | Mermaid コードをコピーする。成功なら `true` |
 * | `showMenu(x, y, ctx)` | `number`, `number`, `object` | `void` | 画面座標 `(x, y)` にメニューを出す |
 * | `static copyText(text)` | `string` | `Promise<boolean>` | 文字列をクリップボードへ(非 HTTPS 環境用の代替手段付き) |
 * | `static hideMenu()` | なし | `void` | 表示中のメニューを閉じる |
 * | `static toast(message)` | `string` | `void` | 短いメッセージを表示する |
 *
 * ## 使用例
 *
 * ```js
 * new UMLClickAction({
 *     target    : document.getElementById("uml"),
 *     getSource : () => document.getElementById("src").value,
 *     left      : "copy",   // 左クリックで即コピー
 *     right     : "menu",   // 右クリックでメニュー
 * });
 * ```
 */
class UMLClickAction{
    static menuEl      = null;    // 表示中のメニュー
    static toastEl     = null;    // 表示中のメッセージ
    static toastTimer  = null;
    static listening   = false;   // メニューを閉じるための共通イベントを登録済みか

    constructor (
        {
            target,
            getSource,
            selector  = null,
            left      = "none",
            right     = "menu",
            menuItems = [],
            notify    = true,
            debug     = false
        } = {}
    ){
        this.debug     = debug;
        this.target    = target;
        this.getSource = getSource;
        this.selector  = selector;
        this.left      = left;
        this.right     = right;
        this.menuItems = menuItems;
        this.notify    = notify;

        // 途中で stopPropagation() されても受けられるよう、どちらもキャプチャ段階で受ける
        this.target.addEventListener("click", (e) => {
            const el = this.find(e);
            if (this.debug) console.log("[UMLClickAction] click", e.target, "->", el);
            if (el) this.run(this.left, e, el);
        }, true);
        // 他のスクリプトが contextmenu を止めていても受けられるよう、キャプチャ段階で受ける
        this.target.addEventListener("contextmenu", (e) => {
            if (this.right === "none") return;   // 標準のメニューを残す
            const el = this.find(e);
            if (this.debug) console.log("[UMLClickAction] contextmenu", e.target, "->", el);
            if (!el) return;                     // 対象外の場所では標準のメニューを残す
            e.preventDefault();
            this.run(this.right, e, el);
        }, true);
        UMLClickAction.listenClose();
    }

    find(e){
        if (!this.selector) return this.target;
        // 親を順にたどる(composedPath は Shadow DOM の内側も含む)
        const path = e.composedPath ? e.composedPath() : [e.target];
        for (const n of path) {
            if (n === this.target) break;
            if (n instanceof Element && n.matches(this.selector)) return n;
        }
        return null;
    }

    run(act, e, el){
        if (act === "none" || !act) return;
        const ctx = {
            el     : el,
            source : this.getSource(el),
            event  : e,
            action : this
        };
        if (typeof act === "function") {
            act(ctx);
        } else if (act === "copy") {
            this.copy(el);
        } else if (act === "menu") {
            this.showMenu(e.clientX, e.clientY, ctx);
        }
    }

    async copy(el = this.target){
        const ok = await UMLClickAction.copyText(this.getSource(el));
        if (this.notify) {
            UMLClickAction.toast(
                ok ? "Mermaid コードをコピーしました" : "コピーに失敗しました"
            );
        }
        return ok;
    }

    showMenu(x, y, ctx){
        UMLClickAction.hideMenu();
        const items = [
            {
                label : "Mermaid コードをコピー",
                run   : (c) => c.action.copy(c.el)
            },
            ...this.menuItems
        ];
        const menu = document.createElement("div");
        Object.assign(menu.style, {
            position     : "fixed",
            zIndex       : "99999",
            background   : "#fff",
            color        : "#222",
            border       : "1px solid #bbb",
            borderRadius : "6px",
            boxShadow    : "0 4px 12px rgba(0,0,0,.25)",
            padding      : "4px 0",
            font         : "14px sans-serif",
            minWidth     : "200px"
        });
        for (const item of items) {
            const row = document.createElement("div");
            row.textContent = item.label;
            Object.assign(row.style, { padding : "6px 14px", cursor : "pointer" });
            row.addEventListener("mouseenter", () => { row.style.background = "#e8f0fe"; });
            row.addEventListener("mouseleave", () => { row.style.background = ""; });
            row.addEventListener("click", () => {
                UMLClickAction.hideMenu();
                item.run(ctx);
            });
            menu.appendChild(row);
        }
        menu.style.left = `${x}px`;
        menu.style.top  = `${y}px`;
        document.body.appendChild(menu);
        // 画面外にはみ出す場合は寄せる
        const r = menu.getBoundingClientRect();
        if (r.right  > window.innerWidth)  menu.style.left = `${Math.max(0, x - r.width)}px`;
        if (r.bottom > window.innerHeight) menu.style.top  = `${Math.max(0, y - r.height)}px`;
        UMLClickAction.menuEl = menu;
    }

    static hideMenu(){
        if (UMLClickAction.menuEl) {
            UMLClickAction.menuEl.remove();
            UMLClickAction.menuEl = null;
        }
    }

    static listenClose(){
        if (UMLClickAction.listening) return;
        UMLClickAction.listening = true;
        document.addEventListener("mousedown", (e) => {
            if (UMLClickAction.menuEl && !UMLClickAction.menuEl.contains(e.target)) {
                UMLClickAction.hideMenu();
            }
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") UMLClickAction.hideMenu();
        });
        window.addEventListener("scroll", UMLClickAction.hideMenu, true);
        window.addEventListener("resize", UMLClickAction.hideMenu);
        window.addEventListener("blur",   UMLClickAction.hideMenu);
    }

    static async copyText(text){
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            }
        } catch (err) {
            // 下の代替手段へ
        }
        // 代替手段(file:// や http:// など navigator.clipboard が使えない環境用)
        const ta = document.createElement("textarea");
        ta.value = text;
        Object.assign(ta.style, { position : "fixed", left : "-9999px", top : "0" });
        document.body.appendChild(ta);
        ta.select();
        let ok = false;
        try {
            ok = document.execCommand("copy");
        } catch (err) {
            ok = false;
        }
        document.body.removeChild(ta);
        return ok;
    }

    static toast(message){
        if (!UMLClickAction.toastEl) {
            const t = document.createElement("div");
            Object.assign(t.style, {
                position      : "fixed",
                right         : "16px",
                bottom        : "16px",
                zIndex        : "99999",
                background    : "rgba(0,0,0,.8)",
                color         : "#fff",
                padding       : "8px 14px",
                borderRadius  : "6px",
                font          : "14px sans-serif",
                pointerEvents : "none",
                transition    : "opacity .3s"
            });
            document.body.appendChild(t);
            UMLClickAction.toastEl = t;
        }
        const t = UMLClickAction.toastEl;
        t.textContent   = message;
        t.style.opacity = "1";
        clearTimeout(UMLClickAction.toastTimer);
        UMLClickAction.toastTimer = setTimeout(() => { t.style.opacity = "0"; }, 1500);
    }
}


/**
 * # MermaidUML
 *
 * 入力欄(textarea 等)の Mermaid コードを、Enter キーで UML(SVG) に描画するクラス。
 * 描画結果を右クリックすると Mermaid コードをコピーできる(`UMLClickAction`)。
 *
 * ## コンストラクタ引数 (オブジェクト)
 *
 * | 引数 | 型 | 既定値 | 説明 |
 * |------|----|--------|------|
 * | `umlPlace` | `string` | (必須) | UML の出力欄の ID |
 * | `umlSource` | `string` | (必須) | Mermaid コードの入力欄の ID |
 * | `dl` | `string` | `undefined` | SVG 保存ボタンの ID。省略時は SVG 保存ボタンなし |
 * | `umlName` | `string` | `"uml"` | 保存ファイル名(拡張子なし) |
 * | `pngDl` | `string` | `undefined` | PNG 保存ボタンの ID。指定すると右クリックメニューにも「PNG として保存」が出る。省略時は PNG 保存なし |
 * | `pngScale` | `number` | `2` | PNG の拡大率(大きいほど高解像度) |
 * | `pngBackground` | `string` | `"#ffffff"` | PNG の背景色。`"transparent"` で透過 |
 * | `click` | `object` | `{}` | `UMLClickAction` に渡す設定(`left` / `right` / `menuItems` / `notify`) |
 *
 * ## メンバ変数
 *
 * | 名前 | 型 | 説明 |
 * |------|----|------|
 * | `uml` | `HTMLElement` | UML の出力欄 |
 * | `src` | `HTMLElement` | Mermaid コードの入力欄 |
 * | `name` | `string` | 保存ファイル名(拡張子なし) |
 * | `pngScale` | `number` | PNG の拡大率 |
 * | `pngBackground` | `string` | PNG の背景色 |
 * | `clickAction` | `UMLClickAction` | クリック動作を担当するオブジェクト |
 *
 * ## メソッド
 *
 * | 名前 | 引数 | 戻り値 | 説明 |
 * |------|------|--------|------|
 * | `draw()` | なし | `void` | 入力欄のコードで UML を描き直す |
 * | `key_press(pressKey)` | `KeyboardEvent` | `void` | Enter で `draw()` を呼ぶ |
 * | `get_svg_text()` | なし | `string` | 描画中の SVG をシリアライズした文字列 |
 * | `save_png()` | なし | `Promise<void>` | 描画中の SVG を PNG に変換して保存する |
 *
 * ## 補足
 *
 * - PNG は SVG を `<canvas>` に描いて作る。ブラウザによっては、
 *   図のラベルが `foreignObject`(HTML ラベル)の場合に canvas が汚染され保存に失敗することがある。
 *   その場合はコンソールにエラーを出し、画面には「PNG の保存に失敗しました」と表示する
 *
 * ## 使用例
 *
 * ```js
 * // 最小構成
 * new MermaidUML({ umlPlace: "drawUML", umlSource: "sourceUML" });
 *
 * // SVG・PNG 保存ボタン付き
 * new MermaidUML({
 *     umlPlace  : "drawUML",
 *     umlSource : "sourceUML",
 *     dl        : "umlDownload",
 *     pngDl     : "pngDownload",
 *     umlName   : "uml",
 * });
 * ```
 */
class MermaidUML{
    constructor (
        {
            umlPlace, 
            umlSource, 
            dl, 
            umlName = "uml",
            pngDl,
            pngScale      = 2,
            pngBackground = "#ffffff",
            click         = {}
        }={}
    ){
        this.uml           = document.getElementById(umlPlace);
        this.src           = document.getElementById(umlSource);
        this.name          = umlName;
        this.pngScale      = pngScale;
        this.pngBackground = pngBackground;
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

        // SVG 保存(dl 指定時のみ)
        if (dl) {
            new DownloadFile(
                dl,
                () => this.get_svg_text(),          // クリック時に最新の SVG を取得
                `${this.name}.svg`,
                "image/svg+xml;charset=utf-8"
            );
        }

        // PNG 保存(pngDl 指定時のみ)
        const menuItems = [...(click.menuItems || [])];
        if (pngDl) {
            const pngBtn = document.getElementById(pngDl);
            pngBtn.addEventListener("click", () => this.save_png());
            menuItems.push(
                {
                    label : "PNG として保存",
                    run   : () => this.save_png()
                }
            );
        }

        // 右クリック・左クリックの動作
        this.clickAction = new UMLClickAction(
            {
                ...click,
                target    : this.uml,
                getSource : () => this.src.value,   // クリック時点の入力欄の内容
                menuItems : menuItems
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

    /**
     * 現在描画されている SVG を文字列で返す。
     *
     * | 戻り値 | 説明 |
     * |--------|------|
     * | `string` | SVG のシリアライズ結果 |
     */
    get_svg_text() {
        return new XMLSerializer().serializeToString(
            this.uml.querySelector("svg")
        );
    }

    /**
     * 現在描画されている SVG を PNG にして保存する。
     *
     * | 戻り値 | 説明 |
     * |--------|------|
     * | `Promise<void>` | 保存の完了(失敗時はメッセージ表示のみで例外は投げない) |
     */
    async save_png() {
        const svg = this.uml.querySelector("svg");
        if (!svg) {
            UMLClickAction.toast("保存できる図がありません");
            return;
        }
        try {
            // 図の大きさ(viewBox 優先、なければ表示サイズ)
            const vb   = svg.viewBox && svg.viewBox.baseVal;
            const rect = svg.getBoundingClientRect();
            const w    = Math.ceil((vb && vb.width)  ? vb.width  : rect.width);
            const h    = Math.ceil((vb && vb.height) ? vb.height : rect.height);

            // width="100%" などだと画像化で大きさが決まらないため、数値で固定した複製を使う
            const clone = svg.cloneNode(true);
            clone.setAttribute("width",  w);
            clone.setAttribute("height", h);
            clone.style.maxWidth = "none";
            const text = new XMLSerializer().serializeToString(clone);

            const img = new Image();
            await new Promise((resolve, reject) => {
                img.onload  = resolve;
                img.onerror = reject;
                img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(text);
            });

            const canvas  = document.createElement("canvas");
            canvas.width  = Math.ceil(w * this.pngScale);
            canvas.height = Math.ceil(h * this.pngScale);
            const g = canvas.getContext("2d");
            if (this.pngBackground !== "transparent") {
                g.fillStyle = this.pngBackground;
                g.fillRect(0, 0, canvas.width, canvas.height);
            }
            g.drawImage(img, 0, 0, canvas.width, canvas.height);

            const blob = await new Promise((resolve, reject) => {
                canvas.toBlob(
                    (b) => b ? resolve(b) : reject(new Error("toBlob failed")),
                    "image/png"
                );
            });
            DownloadFile.save(blob, `${this.name}.png`);
        } catch (err) {
            console.error("PNG の保存に失敗しました:", err);
            UMLClickAction.toast("PNG の保存に失敗しました");
        }
    }
}

// new MermaidUML({ umlPlace: "drawUML", umlSource: "sourceUML", dl: "umlDownload", pngDl: "pngDownload", umlName: "uml" });


/**
 * # MermaidUMLByClass
 *
 * 指定した HTML の class 名を持つ要素すべてについて、
 * 要素内の Mermaid 記法の文字列を UML(SVG) に変換するクラス。
 * 描画結果を右クリックすると、その図の Mermaid コードをコピーできる(`UMLClickAction`)。
 *
 * ## コンストラクタ引数 (オブジェクト)
 *
 * | 引数 | 型 | 既定値 | 説明 |
 * |------|----|--------|------|
 * | `className` | `string` | `"mermaid-src"` | 変換対象の class 名(`.` は付けない) |
 * | `root` | `ParentNode` | `document` | 検索範囲 |
 * | `click` | `object` | `{}` | `UMLClickAction` に渡す設定(`left` / `right` / `menuItems` / `notify`) |
 *
 * ## メンバ変数
 *
 * | 名前 | 型 | 説明 |
 * |------|----|------|
 * | `className` | `string` | 変換対象の class 名 |
 * | `root` | `ParentNode` | 検索範囲 |
 * | `click` | `object` | `UMLClickAction` に渡す設定 |
 * | `nodes` | `HTMLElement[]` | 変換対象の要素一覧 |
 * | `clickAction` | `UMLClickAction` | クリック動作を担当するオブジェクト(`root` 全体で 1 つ。イベント委譲) |
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
 * - 元の文字列は `data-mermaid-src` 属性に保存される(コピーされるのもこの文字列)。
 *   クリックは `root` で一括して受け、クリック位置から `.className` の要素を探すので、
 *   要素が複製・作り直されたり、後から追加されたりしても効く
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
 *
 * 左クリックで即コピーしたい場合:
 *
 * ```js
 * new MermaidUMLByClass({ className: "uml", click: { left: "copy" } });
 * ```
 */
class MermaidUMLByClass{
    static svgSeq = 0;   // marker の ID の接頭辞に使う通し番号(インスタンスをまたいで重複させない)

    constructor (
        {
            className = "mermaid-src",
            root      = document,
            click     = {}
        } = {}
    ){
        this.className = className;
        this.root      = root;
        this.click     = click;
        this.nodes     = [];
        mermaid.initialize(
            {
                startOnLoad : false,
            }
        );

        // 右クリック・左クリックの動作(root 全体で 1 回だけ設定する)
        this.clickAction = new UMLClickAction(
            {
                ...this.click,
                target    : this.root,
                selector  : `.${this.className}`,
                getSource : (el) => el.dataset.mermaidSrc ?? el.textContent.trim()
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
