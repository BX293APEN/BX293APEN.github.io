class ChangeFont{
    constructor(
        {
            queryPlace              = ".text-wrap", 
            letterClass             = "letter", 
            font1                   = "Arial", 
            font2                   = "sans-serif",
        } = {}
    ) {
        this.letters                = document.getElementsByClassName(letterClass);
        this.container              = document.querySelector(queryPlace);

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