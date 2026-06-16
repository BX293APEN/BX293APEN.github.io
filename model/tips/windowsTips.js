class WindowsTipsModel { 
    constructor(){
        this.page =[
            {
                "page" : 1,
                "href" : "/html/tips/windows.html"
            },
            {
                "page" : 2,
                "href" : "/html/tips/windows/wsl.html"
            }
        ]

        this.regeditData = {
            "index" : ["キー", "変更位置"],
            "record" : [
                [
                    "<pre><code class='language-bash'>HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\Directory\\background\\shell</code></pre>",
                    "フォルダの背景部分での右クリック<br>ライブラリディレクトリの背景部分での右クリック"
                ],
                [
                    "<pre><code class='language-bash'>HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\LibraryFolder\\background\\shell</code></pre>",
                    "ライブラリディレクトリのサブフォルダの背景部分での右クリック"
                ],
            ]
        }
        this.treeData = [
            {
                text: "shell",
                icon: "fa fa-folder-open",
                nodes: [
                    { 
                        text: "キー1の名前", 
                        icon: "fa fa-folder-open",
                        nodes: [
                            {
                                text: "command",
                                icon: "fa fa-folder-open",
                                nodes: [
                                    { 
                                        text: "(既定)", 
                                        icon: "fa fa-file",
                                        nodes: [
                                            {
                                                text: "実行するコマンド",
                                                tags : ["%V で右クリックした対象を読み込む"],
                                            }
                                        ]
                                    }
                                    
                                ]
                            },
                            { 
                                text: "MUIVerb", 
                                icon: "fa fa-file",
                                nodes: [
                                    {
                                        text: "表示名"
                                    }
                                ]
                            },
                            { 
                                text: "icon", 
                                icon: "fa fa-file",
                                nodes: [
                                    {
                                        text: "アイコンファイル(.exe, .dll, .ico)"
                                    }
                                ]
                            },
                            { 
                                text: "position", 
                                icon: "fa fa-file",
                                tags : ["既定 : Middle"],
                                nodes: [
                                    {
                                        text: "Top / Middle / Bottom"
                                    }
                                ]
                            },
                            { 
                                text: "SeparatorBefore", 
                                icon: "fa fa-file",
                                tags : ["境界線を項目の前に追加"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                            { 
                                text: "SeparatorAfter", 
                                icon: "fa fa-file",
                                tags : ["境界線を項目の後に追加"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                            { 
                                text: "Extended", 
                                icon: "fa fa-file",
                                tags : ["Shift + 右クリック でのみ表示"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                        ]
                    },
                    { 
                        text: "キー2の名前", 
                        icon: "fa fa-folder-open",
                        nodes: [
                            {
                                text: "shell",
                                icon: "fa fa-folder-open",
                                nodes: [
                                    { 
                                        text: "オプションキー1の名前", 
                                        icon: "fa fa-folder-open",
                                        nodes: [
                                            {
                                                text: "command",
                                                icon: "fa fa-folder-open",
                                                nodes: [
                                                    { 
                                                        text: "(既定)", 
                                                        icon: "fa fa-file",
                                                        nodes: [
                                                            {
                                                                text: "実行するコマンド",
                                                                tags : ["%V で右クリックした対象を読み込む"],
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "MUIVerb", 
                                                icon: "fa fa-file",
                                                nodes: [
                                                    {
                                                        text: "表示名"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "icon", 
                                                icon: "fa fa-file",
                                                nodes: [
                                                    {
                                                        text: "アイコンファイル(.exe, .dll, .ico)"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "position", 
                                                icon: "fa fa-file",
                                                tags : ["既定 : Middle"],
                                                nodes: [
                                                    {
                                                        text: "Top / Middle / Bottom"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "SeparatorBefore", 
                                                icon: "fa fa-file",
                                                tags : ["境界線を項目の前に追加"],
                                                nodes: [
                                                    {
                                                        text: "(空白)"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "SeparatorAfter", 
                                                icon: "fa fa-file",
                                                tags : ["境界線を項目の後に追加"],
                                                nodes: [
                                                    {
                                                        text: "(空白)"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "Extended", 
                                                icon: "fa fa-file",
                                                tags : ["Shift + 右クリック でのみ表示"],
                                                nodes: [
                                                    {
                                                        text: "(空白)"
                                                    }
                                                ]
                                            },
                                        ]
                                    },
                                    { 
                                        text: "オプションキー2の名前", 
                                        icon: "fa fa-folder-open",
                                        nodes: [
                                            {
                                                text: "command",
                                                icon: "fa fa-folder-open",
                                                nodes: [
                                                    { 
                                                        text: "(既定)", 
                                                        icon: "fa fa-file",
                                                        nodes: [
                                                            {
                                                                text: "実行するコマンド",
                                                                tags : ["%V で右クリックした対象を読み込む"],
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "MUIVerb", 
                                                icon: "fa fa-file",
                                                nodes: [
                                                    {
                                                        text: "表示名"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "icon", 
                                                icon: "fa fa-file",
                                                nodes: [
                                                    {
                                                        text: "アイコンファイル(.exe, .dll, .ico)"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "position", 
                                                icon: "fa fa-file",
                                                tags : ["既定 : Middle"],
                                                nodes: [
                                                    {
                                                        text: "Top / Middle / Bottom"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "SeparatorBefore", 
                                                icon: "fa fa-file",
                                                tags : ["境界線を項目の前に追加"],
                                                nodes: [
                                                    {
                                                        text: "(空白)"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "SeparatorAfter", 
                                                icon: "fa fa-file",
                                                tags : ["境界線を項目の後に追加"],
                                                nodes: [
                                                    {
                                                        text: "(空白)"
                                                    }
                                                ]
                                            },
                                            { 
                                                text: "Extended", 
                                                icon: "fa fa-file",
                                                tags : ["Shift + 右クリック でのみ表示"],
                                                nodes: [
                                                    {
                                                        text: "(空白)"
                                                    }
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                            { 
                                text: "SubCommands", 
                                icon: "fa fa-file",
                                tags : ["サブメニューを追加"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                            { 
                                text: "MUIVerb", 
                                icon: "fa fa-file",
                                nodes: [
                                    {
                                        text: "表示名"
                                    }
                                ]
                            },
                            { 
                                text: "icon", 
                                icon: "fa fa-file",
                                nodes: [
                                    {
                                        text: "アイコンファイル(.exe, .dll, .ico)"
                                    }
                                ]
                            },
                            { 
                                text: "position", 
                                icon: "fa fa-file",
                                tags : ["既定 : Middle"],
                                nodes: [
                                    {
                                        text: "Top / Middle / Bottom"
                                    }
                                ]
                            },
                            { 
                                text: "SeparatorBefore", 
                                icon: "fa fa-file",
                                tags : ["境界線を項目の前に追加"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                            { 
                                text: "SeparatorAfter", 
                                icon: "fa fa-file",
                                tags : ["境界線を項目の後に追加"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                            { 
                                text: "Extended", 
                                icon: "fa fa-file",
                                tags : ["Shift + 右クリック でのみ表示"],
                                nodes: [
                                    {
                                        text: "(空白)"
                                    }
                                ]
                            },
                        ]
                    },
                ]
            }
        ];
    }
}

let windowsTipsModel = new WindowsTipsModel();