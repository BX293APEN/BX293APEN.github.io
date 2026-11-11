window.addEventListener(
    'load',
    () => {
        setTimeout(
            () => {
                createTableSearch(
                    {
                        appId: 'apptest-app',
                        inputId: 'q',
                        countId: 'count',
                        clearId: 'clear',
                        scrollerSelector: '.scroller',
                        headRowSelector: 'thead tr.r1',
                        rowSelector: 'tbody tr',
                        tagAttr: 'data-tag',
                        rowTagsAttr: 'data-tags',
                        selectId: 'situation',
                    }
                );
            },
            300
        );
    }
);
