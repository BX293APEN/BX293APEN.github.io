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