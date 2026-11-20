/**
 * # Tex2Math
 *
 * LaTeX 構文を数式に変換するラッパークラス。
 * 数式変換エンジンには `tex.js` (MathJax 4 `tex-chtml` ビルド) を使う。
 * 変換する範囲は、コンストラクタの第1引数で **ページ全体** か **特定のクラスの要素だけ** かを選べる。
 *
 * ## 変換範囲の選び方
 *
 * | 第1引数 | 変換範囲 | 用途 |
 * | --- | --- | --- |
 * | `document` | ページ全体 | 従来の `tex.js` と同じ動作にしたい場合 |
 * | `"クラス名"` | そのクラスを持つ要素の内側のみ | 想定外の箇所を変換させたくない場合 |
 *
 * ## 使い方
 *
 * ```html
 * <script src="Tex2Math.js"></script>
 * <script>
 *     new Tex2Math("texClass");   // texClass の内側だけ変換
 *     // new Tex2Math(document);  // ページ全体を変換
 * </script>
 *
 * <p class="texClass">質量とエネルギーの関係は \( E = mc^2 \) です。</p>
 * <p>ここの \( E = mc^2 \) は変換されません。</p>
 * ```
 *
 * `tex.js` が別の場所にある場合は、第2引数で指定する。
 *
 * ```js
 * new Tex2Math("texClass", "/assets/js/tex.js");
 * ```
 *
 * ## 対応している区切り文字 (MathJax の標準設定)
 *
 * | 種別 | 書き方 |
 * | --- | --- |
 * | インライン数式 | `\( ... \)` |
 * | ディスプレイ数式 | `$$ ... $$` または `\[ ... \]` |
 *
 * `$ ... $` はインライン数式として扱われない (MathJax の標準動作)。
 *
 * ## ID の重複について
 *
 * 出力形式は CHTML (HTML + CSS) であり、SVG のようにグリフ定義の `id` を
 * ページに出力しないため、ID が重複する問題は起きない。
 * そのため連番 ID の自前管理は不要。
 *
 * ## 公開メンバ
 *
 * | メンバ | 種別 | 型 | 説明 |
 * | --- | --- | --- | --- |
 * | `target` | プロパティ | `HTMLElement \| string` | MathJax に渡す変換範囲。`document` なら `<body>`、クラス名なら CSS セレクタ (例: `.texClass`) |
 * | `src` | プロパティ | `string` | 読み込む `tex.js` の場所 |
 * | `ready` | プロパティ | `Promise<void>` | 最初の変換が完了すると解決される |
 * | `typeset()` | メソッド | `Promise<void>` | 変換範囲を再変換する |
 * | `Tex2Math.load_script()` | 静的メソッド | `Promise<void>` | MathJax を設定して読み込む。全インスタンスで1回だけ実行される |
 */
class Tex2Math {
    /**
     * ## 内部状態
     *
     * | 名前 | 型 | 説明 |
     * | --- | --- | --- |
     * | `#loader` | `Promise<void> \| null` | MathJax の読み込み状態。全インスタンスで共有する |
     * | `#baseUrl` | `string` | この `Tex2Math.js` の URL。`tex.js` の既定の場所の基準になる |
     */
    static #loader = null;
    static #baseUrl = document.currentScript?.src ?? location.href;

    /**
     * `tex.js` の既定の場所 (`Tex2Math.js` と同じ場所の `tex.js`)。
     * `TexText2Math` など、同じファイル内の他のクラスが参照する。
     */
    static get default_src() {
        return new URL("tex.js", Tex2Math.#baseUrl).href;
    }

    /**
     * ## コンストラクタ
     *
     * ### 引数
     *
     * | 引数 | 型 | 必須 | 既定値 | 説明 |
     * | --- | --- | --- | --- | --- |
     * | `target` | `Document \| string` | ○ | - | `document` でページ全体、文字列でそのクラス名の要素を変換する。クラス名は1つだけ指定し、`.` は付けない |
     * | `src` | `string` | - | `Tex2Math.js` と同じ場所の `tex.js` | `tex.js` の場所 (URL またはパス) |
     *
     * ### 例外
     *
     * | 例外 | 発生条件 |
     * | --- | --- |
     * | `TypeError` | `target` が `document` でも、空白を含まない空でない文字列でもない |
     *
     * @param {Document | string} target 変換範囲
     * @param {string} [src] `tex.js` の場所
     */
    constructor(target, src = new URL("tex.js", Tex2Math.#baseUrl).href) {
        if (target === document) {
            this.target = document.body;
        } else if (typeof target === "string" && target !== "" && !/\s/.test(target)) {
            this.target = "." + CSS.escape(target);
        } else {
            throw new TypeError("Tex2Math: 第1引数には document か、空白を含まないクラス名を指定してください");
        }

        this.src = src;
        this.ready = this.typeset();
    }

    /**
     * ## 変換範囲を数式に変換する
     *
     * MathJax が未読み込みなら読み込みを待ってから、`target` の内側を変換する。
     * 後から動的に追加した要素を変換したい場合は、このメソッドを再度呼ぶ。
     *
     * ### 戻り値
     *
     * | 型 | 説明 |
     * | --- | --- |
     * | `Promise<void>` | 変換が完了すると解決される。読み込みに失敗すると reject される |
     *
     * @returns {Promise<void>}
     */
    async typeset() {
        await Tex2Math.load_script(this.src);
        await window.MathJax.typesetPromise([this.target]);
    }

    /**
     * ## MathJax を設定して読み込む
     *
     * 次の順で処理する。読み込みは全インスタンスで1回だけで、2回目以降は同じ `Promise` を返す。
     *
     * | 順 | 処理 | 理由 |
     * | --- | --- | --- |
     * | 1 | すでに MathJax が動いていれば何もしない | 二重読み込みを避けるため |
     * | 2 | `window.MathJax` に「自動変換オフ」の設定を入れる | `tex.js` は読み込み直後にページ全体を変換してしまうため |
     * | 3 | `<script>` を `<body>` に追加して読み込む | - |
     * | 4 | MathJax の起動完了まで待つ | 起動前に変換を呼ぶと失敗するため |
     *
     * ### 引数
     *
     * | 引数 | 型 | 説明 |
     * | --- | --- | --- |
     * | `src` | `string` | `tex.js` の場所 |
     *
     * ### 戻り値
     *
     * | 型 | 説明 |
     * | --- | --- |
     * | `Promise<void>` | MathJax の起動が完了すると解決され、読み込みに失敗すると `Error` で reject される |
     *
     * @param {string} src
     * @returns {Promise<void>}
     */
    static load_script(src) {
        if (Tex2Math.#loader) {
            return Tex2Math.#loader;
        }

        const existing = window.MathJax;
        if (existing?.typesetPromise) {
            Tex2Math.#loader = Promise.resolve();
            return Tex2Math.#loader;
        }

        // ページ側で用意された MathJax の設定は残し、自動変換だけを無効にする
        window.MathJax = {
            ...existing,
            startup: { ...existing?.startup, typeset: false },
        };

        Tex2Math.#loader = new Promise(
            (resolve, reject) => {
                const script = document.createElement("script");
                script.src = src;
                script.onload = () => {
                    console.log(`[Load] [Success] ${src}`);
                    resolve(window.MathJax.startup.promise); // 起動完了を待って通知
                };
                script.onerror = () => {
                    Tex2Math.#loader = null; // 次の呼び出しで再試行できるようにする
                    reject(new Error(`[Load] [Fail] ${src}`));
                };
                document.body.appendChild(script);
            }
        );

        return Tex2Math.#loader;
    }
}


// new Tex2Math(document, "/view/tex.js"); // 従来どおりページ全体を変換する場合
// new Tex2Math("texClass", "/view/tex.js"); // tex.js の場所を指定する場合


/**
 * # TexText2Math
 *
 * テキストエリアに書いた Tex 文字列を、数式に変換して表示するクラス。
 * `createUML.js` の `MermaidUML` に相当する、Tex 版のクラス。
 * 表示には `Tex2Math` の仕組み (MathJax 4 `tex-chtml`) をそのまま使う。
 *
 * ## コンストラクタ引数 (オブジェクト)
 *
 * | 引数 | 型 | 既定値 | 説明 |
 * | --- | --- | --- | --- |
 * | `texPlace` | `string` | (必須) | 変換結果を表示する要素の ID |
 * | `texSource` | `string` | (必須) | Tex 文字列を入力する `<textarea>` の ID |
 * | `src` | `string` | `Tex2Math.js` と同じ場所の `tex.js` | `tex.js` の場所 |
 * | `live` | `boolean` | `true` | `true` なら入力のたびに自動で変換する |
 * | `delay` | `number` | `300` | `live` のとき、入力が止まってから変換するまでの待ち時間 (ms) |
 *
 * ## 変換のタイミング
 *
 * | 操作 | 動作 |
 * | --- | --- |
 * | 入力 (`live: true` のとき) | `delay` ミリ秒後に変換する |
 * | `Ctrl + Enter` / `Cmd + Enter` | すぐに変換する (`Enter` 単独は改行のまま) |
 * | `draw()` を呼ぶ | すぐに変換する |
 *
 * ## 書き方 (MathJax の標準)
 *
 * | 種別 | 書き方 |
 * | --- | --- |
 * | インライン数式 | `\( ... \)` |
 * | ディスプレイ数式 | `$$ ... $$` または `\[ ... \]` |
 * | 環境 (ディスプレイ数式) | `\begin{equation} ... \end{equation}` など。区切り文字は不要 |
 *
 * 上のどれにも当てはまらない部分は、ただの文字として表示される。
 * 改行は表示にも反映される (`white-space: pre-wrap`)。
 *
 * ## メンバ変数
 *
 * | 名前 | 型 | 説明 |
 * | --- | --- | --- |
 * | `place` | `HTMLElement` | 変換結果の表示先 |
 * | `source` | `HTMLTextAreaElement` | Tex 文字列の入力欄 |
 * | `src` | `string` | `tex.js` の場所 |
 * | `delay` | `number` | `live` の待ち時間 (ms) |
 * | `ready` | `Promise<void>` | 最初の変換が完了すると解決される |
 *
 * ## メソッド
 *
 * | 名前 | 引数 | 戻り値 | 説明 |
 * | --- | --- | --- | --- |
 * | `draw()` | なし | `Promise<void>` | 入力欄の内容を数式に変換して表示する。連続で呼んでも順番に処理される |
 *
 * ## 補足
 *
 * 入力は `textContent` で表示先に入れるため、`<script>` などを書いても HTML としては解釈されない。
 *
 * ## 使用例
 *
 * ```html
 * <textarea id="texSource">\( E = mc^2 \)</textarea>
 * <div id="texPlace"></div>
 * <script src="Tex2Math.js"></script>
 * <script>
 *     new TexText2Math({ texPlace: "texPlace", texSource: "texSource" });
 * </script>
 * ```
 */
class TexText2Math {
    /**
     * ## 内部状態
     *
     * | 名前 | 型 | 説明 |
     * | --- | --- | --- |
     * | `#queue` | `Promise<void>` | 変換の待ち行列。変換が重ならないよう、前の変換が終わってから次を始める |
     * | `#timer` | `number \| null` | `live` の待ち時間のタイマー ID |
     */
    #queue = Promise.resolve();
    #timer = null;

    constructor (
        {
            texPlace,
            texSource,
            src   = Tex2Math.default_src,
            live  = true,
            delay = 300
        } = {}
    ){
        this.place  = document.getElementById(texPlace);
        this.source = document.getElementById(texSource);
        if (!this.place || !this.source) {
            throw new Error(`TexText2Math: ID "${texPlace}" または "${texSource}" の要素が見つかりません`);
        }
        this.src   = src;
        this.delay = delay;

        // 入力欄の改行を表示にも反映する (指定済みなら上書きしない)
        this.place.style.whiteSpace = this.place.style.whiteSpace || "pre-wrap";

        this.source.addEventListener(
            "keydown", (e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    clearTimeout(this.#timer);
                    this.draw();
                }
            }
        );
        if (live) {
            this.source.addEventListener(
                "input", () => {
                    clearTimeout(this.#timer);
                    this.#timer = setTimeout(() => this.draw(), this.delay);
                }
            );
        }

        this.ready = this.draw();
    }

    /**
     * ## 入力欄の内容を数式に変換して表示する
     *
     * 呼ばれた順に1つずつ処理する。失敗してもコンソールに出すだけで、次の変換は続けられる。
     *
     * @returns {Promise<void>}
     */
    draw() {
        this.#queue = this.#queue
            .then(() => this.#render())
            .catch((err) => console.error("TexText2Math: 変換に失敗しました:", err));
        return this.#queue;
    }

    async #render() {
        await Tex2Math.load_script(this.src);
        const mj = window.MathJax;
        mj.typesetClear([this.place]);              // 前回の変換結果の管理情報を捨てる
        this.place.textContent = this.source.value; // 元の Tex 文字列に戻してから変換する
        await mj.typesetPromise([this.place]);
    }
}

// new TexText2Math({ texPlace: "texPlace", texSource: "texSource" });
