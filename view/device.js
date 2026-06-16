function switchDeviceView(
    {
        pcClass     = ".pc",
        mobileClass = ".sp",
        time        = 300
    } = {}
){
    return function(){
        setTimeout(
            function() {
                if (window.innerWidth >= 768) {
                    for (const el of document.querySelectorAll(pcClass)) {
                        el.style.display = 'block';
                    }
                    for (const el of document.querySelectorAll(mobileClass)) {
                        el.style.display = 'none';
                    }
                } 
                else {
                    for (const el of document.querySelectorAll(pcClass)) {
                        el.style.display = 'none';
                    }
                    for (const el of document.querySelectorAll(mobileClass)) {
                        el.style.display = 'block';
                    }
                }
            }, 
            time
        );
    }
}
