let searchQuery                         = document.getElementById("searchbox");

searchQuery.addEventListener('keydown', key_press);
function key_press(pressKey){
    if (pressKey.key === "Enter") {
        url_search(`https://www.google.com/search?q=${searchQuery.value}&udm=14`);
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