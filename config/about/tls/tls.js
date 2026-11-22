window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                    {
                        appId: 'tls-app',
                        inputId: 'tls-q',
                        countId: 'tls-count',
                        clearId: 'tls-clear',
                        scrollerSelector: '.scroller',
                        headRowSelector: 'thead tr.r1',
                        rowSelector: '.scroller > table > tbody > tr',
                        tagAttr: 'data-tag',
                        rowTagsAttr: 'data-tags',
                        selectId: 'tls-version-select',
                    }
                );
            },
            300
        );
    }
);
