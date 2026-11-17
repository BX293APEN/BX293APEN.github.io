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