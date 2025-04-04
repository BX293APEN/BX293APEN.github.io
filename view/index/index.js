let searchQuery                         = document.getElementById("searchbox");

searchQuery.addEventListener('keydown', key_press);
function key_press(pressKey){
    if (pressKey.key === "Enter") {
        let url = `https://www.google.com/search?q=${searchQuery.value}&udm=14`;
        for(let alias of bookmarkData){
            if ( alias["name"].toUpperCase().indexOf(searchQuery.value.toUpperCase()) != -1) {
                url = alias["value"];
                break;
            }
        }
        
        url_search(url);
    }
}

function url_search(targetURL){
    if(targetURL == ""){
        alert("選択してください");
    }
    else{
        window.location.href = targetURL;
    }
}