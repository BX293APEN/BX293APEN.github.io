function url_search(targetURL){
    if(targetURL == ""){
        alert("選択してください");
    }
    else{
        window.location.href = targetURL;
    }
}

class Search{
    constructor (
        bookmarkData,
        queryPlace = "searchbox"
    ){
        this.searchQuery = document.getElementById(queryPlace);
        this.searchQuery.addEventListener(
            'keydown', 
            this.key_press.bind(this)
            
        );
        this.bookmarkData = bookmarkData;
    }
    key_press(pressKey){
        if (pressKey.key === "Enter") {
            let url = `https://www.google.com/search?q=${this.searchQuery.value}&udm=14`;
            for(let alias of this.bookmarkData){
                if ( alias["name"].toUpperCase().indexOf(this.searchQuery.value.toUpperCase()) != -1) {
                    url = alias["value"];
                    break;
                }
            }
            
            url_search(url);
        }
    }
}

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

new Search(model.bookmarkData);
new MermaidUML("drawUML", "sourceUML", "umlDownload", "uml");


