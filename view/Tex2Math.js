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
