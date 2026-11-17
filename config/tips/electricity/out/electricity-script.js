window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                        {
                        appId: 'electricity-app',
                        inputId: 'electricity-q',
                        countId: 'electricity-count',
                        clearId: 'electricity-clear',
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