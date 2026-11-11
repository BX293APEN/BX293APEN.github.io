function embedded_html(file, id){
    fetch(file)  // `header.html`を取得
        .then(response => response.text()) // 取得した内容をテキストとして処理
        .then(data => document.getElementById(id).innerHTML = data) // `header-container`に挿入
        .catch(error => console.error('読み込みに失敗しました:', error));
}