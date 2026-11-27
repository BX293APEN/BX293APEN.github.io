window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                        {
                        appId: 'boki-app',
                        inputId: 'boki-q',
                        countId: 'boki-count',
                        clearId: 'boki-clear',
                        scrollerSelector: '.scroller',
                        headRowSelector: 'thead tr.r1',
                        rowSelector: 'tbody tr[data-tags]',
                        tagAttr: 'data-tag',
                        rowTagsAttr: 'data-tags',
                    }
                );
            },
            300
        );
    }
);