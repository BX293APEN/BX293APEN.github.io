class ChangeFont{
    constructor(
        {
            queryPlace              = ".text-wrap", 
            range                   = "letter-wrap",
            wordClass               = "word-wrap",
            letterClass             = "letter", 
            font1                   = "Arial", 
            font2                   = "sans-serif",
            space                   = "&ensp;"
        } = {}
    ) {
        this.queryPlace             = queryPlace
        this.range                  = range
        this.wordClass              = wordClass
        this.letterClass            = letterClass
        this.space                  = space

        const style = document.createElement("style");
        style.textContent = `
            .${this.wordClass} {
                display: inline-block;
                white-space: nowrap;
            }

            .${this.letterClass} {
                display: inline-block;
            }
        `
        document.head.appendChild(style);
        this.wrapLetters();

        this.letters                = document.getElementsByClassName(this.letterClass);
        this.container              = document.querySelector(this.queryPlace);

        this.container.addEventListener(
            'mouseleave', 
            () => {
                this.changeFont(font1, 50);
            }
        );

        this.container.addEventListener(
            'mouseenter', 
            () => {
                this.changeFont(font2, 50);
            }
        );

        this.changeFont(font1, 0);
    }
    wrapLetters() {
        /*
            <div id = "letter-wrap">
                KAWAISOU IS KAWAII
            </div> 
            ↓
            <div id = "letter-wrap">
                <span class = "word-wrap">
                    <span class="letter">K</span>
                    <span class="letter">A</span>
                    <span class="letter">W</span>
                    <span class="letter">A</span>
                    <span class="letter">I</span>
                    <span class="letter">S</span>
                    <span class="letter">O</span>
                    <span class="letter">U</span>
                    <span class="letter">&nbsp;</span>
                </span>
                <span class = "word-wrap">
                    <span class="letter">I</span>
                    <span class="letter">S</span>
                    <span class="letter">&nbsp;</span>
                </span>
                <span class = "word-wrap">
                    <span class="letter">K</span>
                    <span class="letter">A</span>
                    <span class="letter">W</span>
                    <span class="letter">A</span>
                    <span class="letter">I</span>
                    <span class="letter">I</span>
                </span>
            </div> 
        */
        const container = document.getElementById(this.range);
        const text = container.textContent.trim();
        const words = text.split(/\s+/); // 単語ごとに分割
        let newHTML = "";

        // 単語ごとにラップ
        for (let i = 0; i < words.length; i++) {
            const word = words[i];
            let lettersHTML = "";

            // 文字ごとにラップ
            for (const char of word) {
                lettersHTML += `<span class="${this.letterClass}">${char}</span>`;
            }

            newHTML += `<span class="${this.wordClass}">${lettersHTML}</span>`;

            // 単語間スペースも span でラップ
            if (i !== words.length - 1) {
                newHTML += `<span class="${this.letterClass}">${this.space}</span>`;
            }
        }

        container.innerHTML = newHTML;
    }

    changeFont(fontName, delay = 50) {
        let index = 0;
        for (const letter of this.letters) {
            setTimeout(
                () => {
                    letter.style.fontFamily = fontName;
                }, 
                index * delay
            );
            index++;
        }
    }
}