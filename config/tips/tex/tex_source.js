window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                        {
                        appId: 'tex-app',
                        inputId: 'tex-q',
                        countId: 'tex-count',
                        clearId: 'tex-clear',
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