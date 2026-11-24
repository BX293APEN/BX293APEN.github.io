window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                    {
                        appId: 'crypt-app',
                        inputId: 'crypt-q',
                        countId: 'crypt-count',
                        clearId: 'crypt-clear',
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
