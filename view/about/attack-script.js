/**
 * # attack-script.js
 *
 * 攻撃手法の表を、タグ・キーワードで絞り込む。
 *
 * ## 構成
 *
 * | 名前 | 種類 | 役割 |
 * |---|---|---|
 * | `createTableSearch` | 関数 | 絞り込みの機能を組み立てる(引数は下の表) |
 * | `window` の `load` イベント | 実行 | ページ読み込み後に `createTableSearch` を呼ぶ |
 */


/**
 * ## 表の絞り込み機能を組み立てる
 *
 * 引数は1つのオブジェクトで渡す。要素が見つからないときは、見つからなかった名前を示すエラーを出す。
 *
 * | 引数 | 型 | 例 | 説明 |
 * |---|---|---|---|
 * | `appId` | `string` | `'attack-app'` | 全体を囲む要素の ID。以降の検索はこの中だけで行う |
 * | `inputId` | `string` | `'q'` | キーワード入力欄の ID |
 * | `countId` | `string` | `'count'` | 件数を表示する要素の ID |
 * | `clearId` | `string` | `'clear'` | 絞り込み解除ボタンの ID |
 * | `scrollerSelector` | `string` | `'.scroller'` | スクロール領域のセレクタ。見出しの固定位置(`--r1h`)を設定する |
 * | `headRowSelector` | `string` | `'thead tr.r1'` | 見出し1段目の行のセレクタ。この高さを2段目の固定位置に使う |
 * | `rowSelector` | `string` | `'tbody tr'` | 絞り込み対象の行のセレクタ |
 * | `tagAttr` | `string` | `'data-tag'` | タグボタン(上部・表中)に付いている属性名 |
 * | `rowTagsAttr` | `string` | `'data-tags'` | 行に付いている属性名。値は `\|` 区切りのタグ一覧 |
 *
 * ## 動作
 *
 * | 操作 | 条件 |
 * |---|---|
 * | タグをクリック | 選択・解除を切り替える。複数選ぶと AND |
 * | キーワード入力 | 大文字小文字・全角半角を区別しない。空白区切りで AND |
 * | 解除ボタン | タグとキーワードを両方クリアする |
 */
function createTableSearch({
    appId,
    inputId,
    countId,
    clearId,
    scrollerSelector,
    headRowSelector,
    rowSelector,
    tagAttr,
    rowTagsAttr,
}) {
    /** ## 固定値(CSS・HTML 側の決まりと対応している) */
    const ACTIVE_CLASS = 'active';   // 選択中のタグに付けるクラス(attack-style.css の `.active`)
    const TAG_SEPARATOR = '|';       // 行のタグ一覧の区切り文字(build.py が `|` で連結している)
    const STICKY_VAR = '--r1h';      // 見出し2段目の固定位置を入れる CSS 変数

    const app = document.getElementById(appId);
    if (!app) throw new Error(`createTableSearch: #${appId} が見つかりません`);

    /** ## `app` の中から要素を1つ探す。なければ名前を示してエラーにする */
    const must = (selector) => {
        const el = app.querySelector(selector);
        if (!el) throw new Error(`createTableSearch: ${selector} が見つかりません`);
        return el;
    };

    const input = must(`#${inputId}`);
    const count = must(`#${countId}`);
    const clear = must(`#${clearId}`);
    const scroller = must(scrollerSelector);
    const headRow = must(headRowSelector);
    const rows = [...app.querySelectorAll(rowSelector)];
    const tagSelector = `[${tagAttr}]`;

    /** ## 検索用に正規化する(NFKC で全角半角をそろえ、小文字にする) */
    const norm = (s) => s.normalize('NFKC').toLowerCase();

    const selected = new Set();   // 選択中のタグ

    rows.forEach((tr) => {
        tr._text = norm(tr.textContent);
        tr._tags = (tr.getAttribute(rowTagsAttr) || '').split(TAG_SEPARATOR);
    });

    /** ## ヘッダ2段目の固定位置を、1段目の高さに合わせる */
    const fit = () => scroller.style.setProperty(STICKY_VAR, `${headRow.offsetHeight}px`);

    /** ## 選択中のタグとキーワードで行を絞り込み、件数とボタンの状態を更新する */
    const apply = () => {
        const words = norm(input.value).split(/\s+/).filter(Boolean);
        let shown = 0;
        rows.forEach((tr) => {
            const ok = [...selected].every((t) => tr._tags.includes(t))
                && words.every((w) => tr._text.includes(w));
            tr.hidden = !ok;
            if (ok) shown++;
        });
        count.textContent = `${shown} / ${rows.length} 件`;
        app.querySelectorAll(tagSelector).forEach((b) => {
            b.classList.toggle(ACTIVE_CLASS, selected.has(b.getAttribute(tagAttr)));
        });
    };

    app.addEventListener('click', (e) => {
        const b = e.target.closest(tagSelector);
        if (!b) return;
        e.preventDefault();
        const t = b.getAttribute(tagAttr);
        selected.has(t) ? selected.delete(t) : selected.add(t);
        apply();
    });
    input.addEventListener('input', apply);
    clear.addEventListener('click', () => {
        selected.clear();
        input.value = '';
        apply();
    });
    window.addEventListener('resize', fit);

    fit();
    apply();
}