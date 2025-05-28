class DownloadView{
    constructor(model, id, tocID){
        this.position                       = document.getElementById(id);
        this.tocPosition                       = document.getElementById(tocID);
        for(let article of model.dlIndex){
            let articleTag                  = document.createElement("article");
            articleTag.classList.add("blog-post");
            articleTag.id                   = article;
            
            let h2Tag                       = document.createElement("h2");
            h2Tag.classList.add("pt-3", "mt-3", "border-bottom", "fw-bold");
            h2Tag.innerHTML                 = model.dlData[article]["title"];
            
            let pTag                        = document.createElement("p");
            pTag.innerHTML                  = model.dlData[article]["text"];
            
            if(model.dlData[article]["imgType"] != "none"){
                let figureTag               = document.createElement("figure");
                figureTag.classList.add("figure");

                let aTag                    = document.createElement("a");
                aTag.href                   = model.dlData[article]["href"];
                let imgTag                  = document.createElement("img");
                imgTag.src                  = model.dlData[article]["imgSrc"];
                if(model.dlData[article]["imgType"] == ".svg"){
                    imgTag.classList.add("figure-img", "img-fluid", "rounded", "w-25");
                }
                aTag.appendChild(imgTag);
                let aDLTag                  = document.createElement("a");
                aDLTag.href                 = model.dlData[article]["href"];
                let figcaptionTag           = document.createElement("figcaption");
                figcaptionTag.classList.add("btn", "btn-bd-primary", "figure-caption", "text-end");
                figcaptionTag.innerHTML     = "Download";
                aDLTag.appendChild(figcaptionTag);

                figureTag.appendChild(aTag);
                figureTag.appendChild(aDLTag);

                articleTag.appendChild(figureTag);
            }

            articleTag.appendChild(h2Tag);
            articleTag.appendChild(pTag);
            

            this.position.appendChild(articleTag);

            let liTOCTag                    = document.createElement("li");
            let aTOCTag                     = document.createElement("a");
            aTOCTag.href                    = `#${article}`;
            aTOCTag.innerHTML               = model.dlData[article]["title"];
            liTOCTag.appendChild(aTOCTag);
            this.tocPosition.appendChild(liTOCTag);
        }

    }
}