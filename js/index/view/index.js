let quickSelectbox                      = document.querySelector('[name="typeselect"]');
let subMenuPlace                        = document.querySelector('.subtype');           /* quickSelectboxSubMenuを表示するspanタブの値を取得 */
let quickSelectboxSubMenu               = document.createElement('select');             /* quickSelectboxSubMenuをリストボックスと認識 */
let quickSelectSearchButton             = document.getElementById('search');            /* 検索ボタンの値を取得 */
let quickAccessPlace                    = document.getElementById('quickAccess');
let bookmarkSelectPlace                 = document.querySelector('.listbox1');
let bookSelect                          = document.createElement('select');
let bookmarkSearchButton                = document.getElementById('bookbutton');
let pageNumber                          = document.getElementById('page');
let searchQuery                         = document.getElementById("searchbox");
let bookQuery                           = document.getElementById("searchbox2");

quickSelectboxSubMenu.classList.add('subselectclass');                                  /* quickSelectboxSubMenuをクラス:subselectclassに属させる */
quickSelectSearchButton.style.display   = "none";                                       /* 検索ボタンを非表示 */
bookSelect.style.width                  = "70%";
bookSelect.classList.add('booklist');

bookmarkSearchButton.style.display      = "none";
pageNumber.style.display                = "none";
bookQuery.style.display                 = "none";

add_option(null, quickSelectbox, quickOptions);
add_img(quickAccessPlace, quickAccessList);

quickSelectbox.onchange = function(event){                                              /* メインセレクトボックスの変更を認識 */
    quickSelectbox.style.backgroundImage    = `url( icon/${quickSelectbox.value}.ico)`;
    quickSelectSearchButton.style.display   = "none";                                   /* 検索ボタンを一時的に非表示 */
    add_option(subMenuPlace, quickSelectboxSubMenu, bookmarkData[quickSelectbox.value]);
    quickSelectSearchButton.style.display   = "inline-block";                           /* 検索ボタンを表示 */
}

pageNumber.onchange = function(event){
    add_option(bookmarkSelectPlace, bookSelect, bookmarkData[`book${pageNumber.value}`]);
}

searchQuery.addEventListener('keydown', key_press);
function key_press(pressKey){
    if (pressKey.key === "Enter") {
        url_search(`https://www.google.com/search?q=${searchQuery.value}&udm=14`);
    }
}

bookQuery.addEventListener('keydown', key_press_book);
function key_press_book(pressKey){
    if (pressKey.key === "Enter") {
        for(let obj in bookmarkData){
            if (obj.indexOf("book") != -1 ){
                if ( bookmarkData[obj][0]["name"].toUpperCase().indexOf(document.getElementById("searchbox2").value.toUpperCase()) != -1) {
                    pageNumber.value = parseInt(obj.split("book")[1]);
                    add_option(bookmarkSelectPlace, bookSelect, bookmarkData[`book${pageNumber.value}`]);
                    break;
                }
            }
        }
    }
}

function lists(listname){
    if(bookmarkSearchButton.style.display == "none"){
        add_option(bookmarkSelectPlace, bookSelect, bookmarkData[`${listname}${pageNumber.value}`]);
        bookmarkSearchButton.style.display  = "inline-block";
        pageNumber.style.display            = "inline-block";
        bookSelect.style.display            = "inline-block";
        bookQuery.style.display             = "inline-block";
    }
    else{
        bookmarkSearchButton.style.display  = "none";
        pageNumber.style.display            = "none";
        bookSelect.style.display            = "none";
        bookQuery.style.display             = "none";
    }
}

function add_img(place, imgList){
    for(let imgValue of imgList){
        let imgElement          = document.createElement('img');
        imgElement.className    = 'img1';
        imgElement.title        = imgValue["title"];
        imgElement.src          = imgValue["src"];
        imgElement.style.height = imgValue["height"];
        imgElement.style.width  = imgValue["width"];
        imgElement.onclick = function(event){
            url_search(imgValue["value"]);
        };
        place.appendChild(imgElement);
    }
}

function add_option(place = null, menu, optionList){
    while(menu.length > 0){
        menu.remove(0);
    }
    for(let optionValue of optionList){
        let option          = document.createElement('option');
        option.value        = optionValue["value"];
        if(optionValue["value"] == ""){
            option.hidden = "hidden";
        }
        option.textContent  = optionValue["name"];
        menu.appendChild(option);
    }
    if (place != null){
        place.appendChild(menu); /* menuを表示 */
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