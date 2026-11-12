window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                        {
                        appId: 'auth-app',
                        inputId: 'auth-q',
                        countId: 'count',
                        clearId: 'clear',
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