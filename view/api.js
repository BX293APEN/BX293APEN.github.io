const checkIfImageExists = (url) => {
    return new Promise(
        (resolve, reject) => {
            let img = new Image();
            img.src = url;
            img.onload = () => resolve(url);
            img.onerror = () => reject(url);
        }
    );
};


class GetWeather{
    constructor(place, dispStr, model, time = 5000){
        this.model      = model
        this.place      = document.getElementById(place);
        this.dispStr    = document.getElementById(dispStr);
        this.num        = 0;
        this.interval   = time
        this.changeImage();
        setInterval(
            this.changeImage.bind(this), 
            this.interval
        ); 
    }
    changeImage() {
        let id          = this.model.areaID[this.num]["id"];
        this.area       = this.model.areaID[this.num]["name"]
        this.get_weather(id);

        this.num = (this.num + 1) % 47;
    }
    get_weather(areaID = "130000"){
        let url = `https://www.jma.go.jp/bosai/forecast/data/forecast/${areaID}.json`;
        let imgURL = "https://www.jma.go.jp/bosai/forecast/img/";
        let weatherCode;
        fetch(url)
            .then(
                function(response) {
                    return response.json();
                }
            )
            .then(
                weather => {
                    let data = weather;
                    weatherCode = data[0]["timeSeries"][0]["areas"][0]["weatherCodes"][0];
                    let srcImage = `${imgURL}${weatherCode}.svg`

                    checkIfImageExists(srcImage)
                        .then(
                            (url) => {
                                this.place.src = srcImage;
                                this.dispStr.textContent = this.area;
                            }
                        )
                        .catch(
                            (url) => {
                                this.place.src = `${imgURL}100.svg`;
                                this.dispStr.textContent = " - ";
                            }
                        );
                }
            )
    }
}

//new GetWeather("weather", "weather-place");