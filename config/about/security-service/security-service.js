/**
 * # security-service.js
 *
 * セキュリティサービス表用。関数 `createTableSearch` は `attack-script.js` を使い回す。
 * このファイルは `attack-script.js` より後に読み込むこと。
 *
 * | 引数 | 値 | 補足 |
 * |---|---|---|
 * | `rowSelector` | `'.scroller > table > tbody > tr'` | 説明セル内の入れ子の表の行を除き、表本体の行だけを対象にする |
 * | その他 | `security-` 付きの ID | `attack-app` 用の値と衝突しないようにしている |
 */
window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch({
                    appId: 'security-app',
                    inputId: 'security-q',
                    countId: 'security-count',
                    clearId: 'security-clear',
                    scrollerSelector: '.scroller',
                    headRowSelector: 'thead tr.r1',
                    rowSelector: '.scroller > table > tbody > tr',
                    tagAttr: 'data-tag',
                    rowTagsAttr: 'data-tags',
                });
            },
            300
        );
    }
);
