class TipsView{
    constructor(model, html, id, dispElement = []){
        let insertPosition                  = document.getElementById(id);
        if(html == "index"){
            for(let tipID of model.tipsIndex){
                let colTag                  = document.createElement("div");
                colTag.classList.add("col");
                colTag.id                   = tipID;

                let aTag                    = document.createElement("a");
                aTag.classList.add("link-body-emphasis", "text-decoration-none");
                aTag.href                   = model.tipsData[tipID]["href"];
                
                let divCoverTag             = document.createElement("div");
                divCoverTag.classList.add("card", "shadow-sm", "h-100");

                let imgTag                  = document.createElement("img");
                imgTag.src                  = model.tipsData[tipID]["imgSrc"];
                imgTag.classList.add("bd-placeholder-img");
                imgTag.ariaHidden           = "true";

                if (model.tipsData[tipID]["svg"]){
                    imgTag.width            = "100%";
                    imgTag.height           = 150;
                    imgTag.classList.add("card-img-top");
                }
                else{
                    imgTag.width            = 120;
                    imgTag.classList.add("mx-auto");
                }

                divCoverTag.appendChild(imgTag);

                let divTag                  = document.createElement("div");
                divTag.classList.add("card-body");

                let h6Tag                   = document.createElement("h6");
                h6Tag.innerHTML             = model.tipsData[tipID]["title"];
                h6Tag.classList.add("mb-0", "fw-bold");
                divTag.appendChild(h6Tag);

                let pTag                    = document.createElement("p");
                pTag.innerHTML              = model.tipsData[tipID]["text"];
                pTag.classList.add("card-text");
                divTag.appendChild(pTag);

                divCoverTag.appendChild(divTag);
                aTag.appendChild(divCoverTag);
                colTag.appendChild(aTag);
                insertPosition.appendChild(colTag);
            }
        }

        else{
            let coverTag                = document.createElement("div");
            coverTag.classList.add("p-2");
            let titleTag                = document.createElement("h4");
            titleTag.classList.add("fst-italic");
            titleTag.innerHTML          = "Tips";
            coverTag.appendChild(titleTag);

            let ulTag                   = document.createElement("ul");
            ulTag.classList.add("list-unstyled");

            for(let tipID of model.tipsIndex){
                if(dispElement.includes(tipID)){
                    let liTag                   = document.createElement("li");
                    liTag.id                    = tipID;

                    let aTag                    = document.createElement("a");
                    aTag.classList.add(
                        "d-flex", 
                        "flex-column", 
                        "flex-lg-row", 
                        "gap-3", 
                        "align-items-start", 
                        "align-items-lg-center", 
                        "py-3", 
                        "link-body-emphasis", 
                        "text-decoration-none", 
                        "border-top" 
                    );

                    aTag.href                   = model.tipsData[tipID]["href"];

                    let imgTag                  = document.createElement("img");
                    imgTag.src                  = model.tipsData[tipID]["imgSrc"];
                    imgTag.classList.add("bd-placeholder-img");
                    imgTag.ariaHidden           = "true";

                    if (model.tipsData[tipID]["svg"]){
                        imgTag.width            = 100;
                        imgTag.height           = 96;
                    }
                    else{
                        imgTag.width            = 100;
                        imgTag.classList.add("mx-auto");
                    }
                    aTag.appendChild(imgTag);

                    let divTag                  = document.createElement("div");
                    divTag.classList.add("col-lg-8");

                    let h6Tag                   = document.createElement("h6");
                    h6Tag.innerHTML             = model.tipsData[tipID]["title"];
                    h6Tag.classList.add("mb-0", "fw-bold");
                    divTag.appendChild(h6Tag);

                    let smallTag                    = document.createElement("small");
                    smallTag.innerHTML              = model.tipsData[tipID]["text"];
                    smallTag.classList.add("text-body-secondary");
                    divTag.appendChild(smallTag);

                    aTag.appendChild(divTag);
                    liTag.appendChild(aTag);
                    ulTag.appendChild(liTag);
                }
                
            }
            coverTag.appendChild(ulTag);
            insertPosition.appendChild(coverTag);
        }
        
    }
}
