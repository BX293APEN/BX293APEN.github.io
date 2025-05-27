class Pagination{
    constructor(
        page,
        model,
        placeID = "pagination"
    ){
        this.page           = page
        this.model          = model
        this.placeID        = placeID
        this.place          = document.getElementById(this.placeID);
        let navTag          = document.createElement("nav");
        navTag.ariaLabel    = "..."
        let ulTag           = document.createElement("ul");
        ulTag.classList.add("pagination", "justify-content-center");

        for(let pageItem of this.model){
            let liTag           = document.createElement("li");
            liTag.classList.add("page-item");

            let aTag            = document.createElement("a");
            aTag.classList.add("page-link");
            aTag.textContent    = pageItem["page"];

            if (page == pageItem["page"]){
                liTag.classList.add("active");
                aTag.href           = "#!";
            }
            else{
                aTag.href           = pageItem["href"];
            }

            liTag.appendChild(aTag);
            ulTag.appendChild(liTag);
        }
        navTag.appendChild(ulTag);
        this.place.appendChild(navTag);
        
    }
}