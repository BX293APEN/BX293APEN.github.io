function element_disp(dispIDList=[], deleteIDList=[],time = 300){
    return function(){
        setTimeout(
            function() {
                for(let id of dispIDList){
                    document.getElementById(id).style.display = 'block'; 
                }
                for(let id of deleteIDList){
                    document.getElementById(id).style.display = 'none'; 
                }
            }, 
            time
        );
    }
}


window.addEventListener( //デフォルト状態を指定
    "load", 
    element_disp(
        [],
        ["githubTip", "vimTip", "rn4020Tip", "linuxTip", "pythonTip", "visualstudioTip"],
        250
    )
);