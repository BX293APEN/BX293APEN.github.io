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

//new Search(model.bookmarkData);