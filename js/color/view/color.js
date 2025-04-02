let colorTable = document.getElementById("colorPalette");
add_row(colorTable, config);

let colorNameTable = document.getElementById("colorNamePalette");
add_row(colorNameTable, nameConfig);

function add_row(place, rowConfig){
    for(let row of rowConfig["color"]){
        let rowColor                            = document.createElement('tr');
        rowColor.style.height                   = rowConfig["height"];
        let rowData                             = document.createElement('tr');
        rowData.style.height                    = rowConfig["height"];

        for (let field of row){
            let fieldColor                      = document.createElement('td');
            fieldColor.style.backgroundColor    = field.split("(")[0];
            rowColor.appendChild(fieldColor);
            
            let fieldData                       = document.createElement('td');
            fieldData.textContent               = field;
            rowData.appendChild(fieldData);
        }

        place.appendChild(rowColor);
        place.appendChild(rowData);
    }
}
