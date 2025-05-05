function active_nav(id = "home", time = 300){
    return function(){
        setTimeout(
            function() {
                let activeNav = document.getElementById(id);
                activeNav.classList.add('active');
                new Search(model.bookmarkData);
            }, 
            time
        );
    }
}
