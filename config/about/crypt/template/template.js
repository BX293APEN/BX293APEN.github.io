window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                    {
                        appId: '__APP_ID__',
                        inputId: '__INPUT_ID__',
                        countId: '__COUNT_ID__',
                        clearId: '__CLEAR_ID__',
                        scrollerSelector: '.scroller',
                        headRowSelector: 'thead tr.r1',
                        rowSelector: '.scroller > table > tbody > tr',
                        tagAttr: 'data-tag',
                        rowTagsAttr: 'data-tags',
                        selectId: null,                                 // プルダウンは使わない(タグの絞り込みだけ)
                    }
                );
            },
            300
        );
    }
);
