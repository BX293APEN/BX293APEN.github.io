function createTable(placeID, model, noWrap = false){
    let place = document.getElementById(placeID);
    let coverTag                = document.createElement("div");
    coverTag.classList.add("table-responsive");
    let tableTag                = document.createElement("table");
    tableTag.classList.add("table", "table-bordered", "w-100");
    let tbodyTag                = document.createElement("tbody");
    let trTag                   = document.createElement("tr");
    for(let c of model["index"]){
        let thTag               = document.createElement("th");
        if(noWrap){
            thTag.classList.add("text-nowrap");
        }
        thTag.innerHTML         = c;
        trTag.appendChild(thTag);
    }
    tbodyTag.appendChild(trTag);

    for(let row of model["record"]){
        let trTag               = document.createElement("tr");
        for(let c of row){
            let tdTag           = document.createElement("td");
            if(noWrap){
                tdTag.classList.add("text-nowrap");
            }
            tdTag.innerHTML     = c;
            trTag.appendChild(tdTag);
        }
        tbodyTag.appendChild(trTag);
    }
    tableTag.appendChild(tbodyTag);
    coverTag.appendChild(tableTag);
    place.appendChild(coverTag);
}