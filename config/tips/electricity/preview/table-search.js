/**
 * # table-search.js(確認用の簡易版)
 *
 * `createTableSearch` は、貼り付け先のサイトが持っている関数。
 * 単体で `preview.html` を開いても動作を確認できるよう、同じ引数を受け取る簡易版を置く。
 * **本番では使わない**(サイト側の関数と挙動が違う場合がある)。
 *
 * ## 挙動
 *
 * | 操作 | 動き |
 * |---|---|
 * | 検索欄に入力 | 空白区切りの全語を含む行だけ残す(大文字・小文字・全角半角を区別しない) |
 * | タグ(ボタン・表中のバッジ)をクリック | 選択 / 解除を切り替える。選んだタグを**すべて**持つ行だけ残す |
 * | 解除ボタン | 検索語とタグの選択をすべて外す |
 * | 件数 | `残った行数 / 全行数 件` を表示する |
 * | 見出しの高さ | `--r1h`(2段目の見出しを固定する位置)を、1段目の高さに合わせる |
 */

/**
 * ## 表の検索・タグ絞り込みを設定する
 *
 * | 引数(`opts` のキー) | 型 | 説明 |
 * |---|---|---|
 * | `appId` | `string` | 最外枠の `id` |
 * | `inputId` | `string` | 検索欄の `id` |
 * | `countId` | `string` | 件数表示の `id` |
 * | `clearId` | `string` | 解除ボタンの `id` |
 * | `scrollerSelector` | `string` | スクロール領域のセレクタ(`--r1h` を設定する先) |
 * | `headRowSelector` | `string` | 1段目の見出し行のセレクタ |
 * | `rowSelector` | `string` | 絞り込む行のセレクタ |
 * | `tagAttr` | `string` | タグ名を持つ属性(ボタン・バッジ側) |
 * | `rowTagsAttr` | `string` | 行がタグを `|` 区切りで持つ属性 |
 *
 * | 戻り値 | 説明 |
 * |---|---|
 * | なし | |
 */
function createTableSearch(opts) {
    const app = document.getElementById(opts.appId);
    if (!app) { console.warn('createTableSearch: #' + opts.appId + ' がありません'); return; }
    const input = document.getElementById(opts.inputId);
    const count = document.getElementById(opts.countId);
    const clear = document.getElementById(opts.clearId);
    const scroller = app.querySelector(opts.scrollerSelector);
    const headRow = app.querySelector(opts.headRowSelector);
    const rows = Array.from(app.querySelectorAll(opts.rowSelector));
    const tagEls = Array.from(app.querySelectorAll('[' + opts.tagAttr + ']'));
    const selected = new Set();

    // ## 検索用に正規化する(全角半角・大文字小文字をそろえる)
    const norm = (s) => s.normalize('NFKC').toLowerCase();
    const texts = rows.map((r) => norm(r.textContent));

    // ## 表示を更新する
    function update() {
        const words = norm(input ? input.value : '').split(/\s+/).filter(Boolean);
        let shown = 0;
        rows.forEach((r, i) => {
            const tags = (r.getAttribute(opts.rowTagsAttr) || '').split('|');
            const ok = words.every((w) => texts[i].includes(w))
                && Array.from(selected).every((t) => tags.includes(t));
            r.style.display = ok ? '' : 'none';
            if (ok) shown++;
        });
        tagEls.forEach((el) => el.classList.toggle('active', selected.has(el.getAttribute(opts.tagAttr))));
        if (count) count.textContent = shown + ' / ' + rows.length + ' 件';
    }

    tagEls.forEach((el) => el.addEventListener('click', () => {
        const t = el.getAttribute(opts.tagAttr);
        selected.has(t) ? selected.delete(t) : selected.add(t);
        update();
    }));
    if (input) input.addEventListener('input', update);
    if (clear) clear.addEventListener('click', () => {
        selected.clear();
        if (input) input.value = '';
        update();
    });
    if (scroller && headRow) scroller.style.setProperty('--r1h', headRow.offsetHeight + 'px');
    update();
}
