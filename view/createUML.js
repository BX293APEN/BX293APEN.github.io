class MermaidUML{
    constructor (umlPlace, umlSource, dl, umlName){
        this.uml    = document.getElementById(umlPlace);
        this.src    = document.getElementById(umlSource);
        this.dl     = document.getElementById(dl);
        this.name   = umlName;
        this.src.addEventListener(
            'keydown', 
            this.key_press.bind(this)
        );
        mermaid.initialize(
            {
                startOnLoad     : true,
            }
        );
        this.draw();
        this.dl.addEventListener(
            'click', 
            () => {
                this.download_svg();
            }
            
        );
    }
    draw(){
        this.uml.removeAttribute('data-processed');
        this.uml.textContent = this.src.value;
        mermaid.init();
    }

    key_press(pressKey){
        if (pressKey.key === "Enter") {
            this.draw()
        }
    }
    download_svg() {
        // svg要素を取得
        let svgNode = this.uml.querySelector("svg");
        let svgText = new XMLSerializer().serializeToString(svgNode);
        let svgBlob = new Blob(
            [svgText], 
            { 
                type: 'image/svg+xml;charset=utf-8' 
            }
        );
        let svgUrl = URL.createObjectURL(svgBlob);
      
        // a要素を作ってダウンロード
        let a = document.createElement('a');
        a.href = svgUrl;
        a.download = `${this.name}.svg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(svgUrl);
    }
      
}

new MermaidUML("drawUML", "sourceUML", "umlDownload", "uml");