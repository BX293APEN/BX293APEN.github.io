/**
 * # FixSvgOverflow
 *
 * `<object>` で読み込んだ mermaid.js 製 SVG の文字見切れを補正するクラス。
 *
 * ## 動作
 *
 * | 順序 | 処理 | 適用条件 |
 * |------|------|----------|
 * | 1 | `overflow: visible` / フォント / 字間 / `fontSize` / プロポーショナル字詰め (`palt`) の補正 | `targetFonts` のいずれも端末に無い場合のみ |
 * | 2 | 1 でも枠からはみ出すラベルのフォントを個別に縮小 | 1 を適用した場合のみ |
 * | 3 | `scrollable` が `false` なら画面幅に合わせて縮小、`true` なら本来のサイズで親を横スクロール化 | 常に適用 |
 *
 * ## メンバ
 *
 * | メンバ | 型 | 説明 |
 * |--------|----|------|
 * | `className` | `string` | 対象 `<object>` のクラス名 |
 * | `fontSize` | `string` | 補正時の基本フォントサイズ |
 * | `letterSpacing` | `string` | 補正時の字間 |
 * | `targetFonts` | `string[]` | 端末での有無を判定するフォント名 |
 * | `scrollable` | `boolean` | `true`: 本来のサイズで横スクロール / `false`: 画面幅に合わせて縮小 |
 * | `fontAvailableCache` | `boolean \| null` | フォント判定結果のキャッシュ (未判定は `null`) |
 *
 * ## 使用例
 *
 * ```js
 * window.addEventListener('load', () => {
 *     new FixSvgOverflow('svgclass');
 * });
 * ```
 *
 * ## 注意
 *
 * - `file://` や別オリジンでは `contentDocument` が `null` になり適用できない。
 *   HTTP(S) の同一オリジンで配信すること。
 */
class FixSvgOverflow {

    /**
     * ## constructor
     *
     * 設定を保持し、対象の `<object>` すべてに補正を登録する。
     *
     * ### 引数
     *
     * | 引数 | 型 | 既定値 | 説明 |
     * |------|----|--------|------|
     * | `className` | `string` | `'svgclass'` | 対象 `<object>` のクラス名 |
     * | `fontSize` | `string` | `'75%'` | 補正時の基本フォントサイズ (元サイズに対する割合) |
     * | `letterSpacing` | `string` | `'-0.1em'` | 補正時の字間 |
     * | `targetFonts` | `string[]` | `['HGPGothicE', 'HGPゴシックE']` | 判定対象のフォント名 (どれか1つでもあれば補正しない) |
     * | `scrollable` | `boolean` | `false` | `true` なら本来のサイズで横スクロール(overflow-x-auto必要)、`false` なら画面幅に合わせて縮小 |
     */
    constructor(
        className = 'svgclass',
        fontSize = '75%',
        letterSpacing = '-0.1em',
        targetFonts = ['HGPGothicE', 'HGPゴシックE'],
        scrollable = false
    ) {
        this.className = className;
        this.fontSize = fontSize;
        this.letterSpacing = letterSpacing;
        this.targetFonts = targetFonts;
        this.scrollable = scrollable;
        this.fontAvailableCache = null;

        this.run();
    }

    /**
     * ## run
     *
     * 対象の `<object>` を探し、読み込み済みなら即適用、未読み込みなら `load` を待って適用する。
     *
     * ### 引数
     *
     * なし
     *
     * ### 戻り値
     *
     * | 型 | 説明 |
     * |----|------|
     * | `void` | なし |
     */
    run() {
        const targets = document.querySelectorAll(`object.${this.className}`);

        targets.forEach((obj) => {
            this.applySvgFix(obj);
            obj.addEventListener('load', () => this.applySvgFix(obj));
        });
    }

    /**
     * ## isFontAvailable
     *
     * canvas で文字幅を測り、`targetFonts` のいずれかが端末にあるか判定する。
     * 未インストールなら基準フォントにフォールバックして幅が一致する、という性質を利用する。
     * 結果は `fontAvailableCache` にキャッシュされる。
     *
     * ### 引数
     *
     * なし
     *
     * ### 戻り値
     *
     * | 型 | 説明 |
     * |----|------|
     * | `boolean` | いずれかのフォントが利用可能なら `true` |
     */
    isFontAvailable() {
        if (this.fontAvailableCache !== null) return this.fontAvailableCache;

        const ctx = document.createElement('canvas').getContext('2d');
        const text = 'あいうえお漢字ABCabc123mWi';
        const bases = ['monospace', 'sans-serif', 'serif'];

        const measure = (font) => {
            ctx.font = `72px ${font}`;
            return ctx.measureText(text).width;
        };

        // 基準フォントのどれか1つでも幅が変われば、そのフォントは存在する
        this.fontAvailableCache = this.targetFonts.some((name) =>
            bases.some((base) => measure(`"${name}", ${base}`) !== measure(base))
        );
        return this.fontAvailableCache;
    }

    /**
     * ## fitLabels
     *
     * 字間補正後も `foreignObject` の枠から横にはみ出すラベルを探し、
     * そのラベルだけフォントを縮小して収める。
     * 枠・文字幅とも画面上の寸法で測るので、SVG の拡大縮小の影響を受けない。
     *
     * ### 引数
     *
     * | 引数 | 型 | 説明 |
     * |------|----|------|
     * | `svgDoc` | `Document` | SVG のドキュメント (`obj.contentDocument`) |
     *
     * ### 戻り値
     *
     * | 型 | 説明 |
     * |----|------|
     * | `void` | なし |
     *
     * ### 縮小量の決め方
     *
     * | 状況 | 結果 |
     * |------|------|
     * | 枠に収まっている | 変更しない |
     * | はみ出している | 枠幅 / 文字幅 の比率で縮小 |
     */
    fitLabels(svgDoc) {
        const view = svgDoc.defaultView;

        svgDoc.querySelectorAll('foreignObject').forEach((fo) => {
            const label = fo.firstElementChild;
            if (!label) return;

            const boxWidth = fo.getBoundingClientRect().width;
            const range = svgDoc.createRange();
            range.selectNodeContents(label);
            const textWidth = range.getBoundingClientRect().width;

            // 収まっていれば何もしない (誤差 0.2px は許容)
            if (boxWidth <= 0 || textWidth <= boxWidth + 0.2) return;

            const current = parseFloat(view.getComputedStyle(label).fontSize);
            const next = current * (boxWidth / textWidth);

            label.style.setProperty('font-size', `${next}px`, 'important');
        });
    }

    /**
     * ## applySvgFix
     *
     * 1 つの `<object>` 内の SVG に補正を適用する。二重適用はしない。
     *
     * ### 引数
     *
     * | 引数 | 型 | 説明 |
     * |------|----|------|
     * | `obj` | `HTMLObjectElement` | 対象の `<object>` |
     *
     * ### 戻り値
     *
     * | 型 | 説明 |
     * |----|------|
     * | `boolean` | 適用できたら `true`、SVG 未読み込み等で適用できなければ `false` |
     */
    applySvgFix(obj) {
        const svgDoc = obj.contentDocument;
        const svg = svgDoc && svgDoc.documentElement;

        // 未読み込み時の about:blank (html要素) を除外する
        if (!svg || svg.localName !== 'svg') return false;

        // 対象フォントが無い環境でのみ文字の補正スタイルを適用する (二重適用も防ぐ)
        if (!this.isFontAvailable() && !svgDoc.getElementById('custom-mermaid-fix')) {
            // 名前空間は SVG 本来のもの (http://www.w3.org/2000/svg) を使う
            const style = svgDoc.createElementNS('http://www.w3.org/2000/svg', 'style');
            style.id = 'custom-mermaid-fix';
            // font-size は最外側の要素だけに指定する。
            // div / span の両方に % 指定すると 88% が入れ子で掛かり、実質 77% になるため。
            style.textContent = `
                foreignObject, foreignObject div, foreignObject span {
                    overflow: visible !important;
                }
                text, foreignObject div, foreignObject span, .nodeLabel, .label {
                    font-family: "HGPGothicE", "Roboto Condensed", "Noto Sans JP", sans-serif !important;
                    letter-spacing: ${this.letterSpacing} !important;
                    /* 仮名・記号の幅を詰める (HGP = プロポーショナルフォントに近づける) */
                    font-feature-settings: "palt" 1 !important;
                    font-kerning: normal !important;
                }
                text, foreignObject > div {
                    font-size: ${this.fontSize} !important;
                }
            `;
            svg.appendChild(style);

            // 字間・基本サイズの補正後も枠からはみ出すラベルだけ、さらに縮小する
            this.fitLabels(svgDoc);
        }

        // mermaid が付ける max-width を外し、本来のサイズで扱えるようにする
        svg.style.maxWidth = 'none';

        // viewBox から縦横比を取得し、<object> の高さを図に合わせる
        const vb = svg.viewBox && svg.viewBox.baseVal;
        if (vb && vb.width > 0 && vb.height > 0) {
            obj.style.aspectRatio = `${vb.width} / ${vb.height}`;
            obj.style.height = 'auto';

            if (this.scrollable) {
                // 本来のサイズを保ち、親を横スクロールコンテナにする
                // (Bootstrap 5.3 未満や flex / grid の子でも、親の枠から出さない)
                obj.style.minWidth = `${vb.width}px`;
                const wrap = obj.parentElement;
                if (wrap) {
                    wrap.style.overflowX = 'auto';
                    wrap.style.maxWidth = '100%';
                    wrap.style.minWidth = '0';
                }
            } else {
                // 画面幅に合わせて縮小する (viewBox により SVG の縮尺が追従する)
                obj.style.width = '100%';
                obj.style.maxWidth = '100%';
            }
        }

        return true;
    }
}
