class KatamariDamacyModel{
    constructor(){
        this.htmlStructure = {
            "easyButtonID"              : 'easyBtn',
            "normalButtonID"            : 'normalBtn',
            "hardButtonID"              : 'hardBtn',
            "cityButtonID"              : 'cityBtn',
            "parkButtonID"              : 'parkBtn',
            "tutorialCloseButtonID"     : 'tutorialCloseBtn',
            "tutorialID"                : 'tutorial',
            "resumeButtonID"            : 'resumeBtn',
            "pauseScreenID"             : 'pauseScreen',
            "helpButtonID"              : 'helpBtn',
            "nextLevelButtonID"         : 'nextLevelBtn',
            "minimapID"                 : 'minimap'
        }

        this.difficulty = {
            "easy" : {
                "name"                  : '🌱 イージー',
                "timeLimit"             : 600,          // 秒数
                "targetCount"           : 150,
                "sizeMultiplier"        : 1.2,
                "growthBonus"           : 1.3,
                "objects": {                            // オブジェクトの数を指定
                    "tiny"              : 80,           // 極小
                    "small"             : 60,           // 小
                    "medium"            : 40,           // 中
                    "large"             : 25,           // 大
                    "huge"              : 15,           // 超大
                    "moving"            : 10            // 動く
                }
            },
            "normal": {
                "name"                  : '⚖️ ノーマル',
                "timeLimit"             : 480,
                "targetCount"           : 200,
                "sizeMultiplier"        : 1.2,
                "growthBonus"           : 1.2,
                "objects": {                            // オブジェクトの数を指定
                    "tiny"              : 60,           // 極小
                    "small"             : 80,           // 小
                    "medium"            : 60,           // 中
                    "large"             : 25,           // 大
                    "huge"              : 15,           // 超大
                    "moving"            : 10            // 動く
                }
            },
            "hard" : {
                "name"                  : '🔥 ハード',
                "timeLimit"             : 360,
                "targetCount"           : 250,
                "sizeMultiplier"        : 1.2,
                "growthBonus"           : 1.1,
                "objects": {                            // オブジェクトの数を指定
                    "tiny"              : 20,           // 極小
                    "small"             : 80,           // 小
                    "medium"            : 70,           // 中
                    "large"             : 50,           // 大
                    "huge"              : 40,           // 超大
                    "moving"            : 10            // 動く
                }
            }
        }

        this.stages = {
            "city" : {
                "name"                  : '🏙️ 街',
                "skyColor"              : 0x87CEEB,
                "groundColor"           : 0x4A4A4A
            },
            "park" : {
                "name"                  : '🌳 公園',
                "skyColor"              : 0x87CEEB,
                "groundColor"           : 0x2D5016
            },
        }
    }
}