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

class GetCveScore {
    /**
     *
     * | 引数 | 型 | 説明 |
     * |------|----|------|
     * | `cve`  | `string` | 調べたい CVE の値 |
     * | `cvss` | `string` | CVSS を表示する要素の ID |
     * | `epss` | `string` | EPSS を表示する要素の ID |
     *
     */
    constructor(cve, cvss, epss) {
        this.cve    = String(cve).trim().toUpperCase();
        this.cvss   = document.getElementById(cvss);
        this.epss   = document.getElementById(epss);
        this.empty  = " - ";

        // CVE-YYYY-NNNN... 形式以外は API を呼ばずに失敗表示
        if (!/^CVE-\d{4}-\d{4,}$/.test(this.cve)) {
            this.show(this.cvss, this.empty);
            this.show(this.epss, this.empty);
            return;
        }

        // 更新は生成時の1回のみ
        this.getCvss();
        this.getEpss();
    }

    /**
     * | 引数 | 型 | 説明 |
     * |------|----|------|
     * | `elem` | `HTMLElement \| null` | 表示先の要素 |
     * | `text` | `string` | 表示する文字列 |
     */
    show(elem, text) {
        if (elem) {
            elem.textContent = text;
        }
    }
    
    /**
     * NVD API から CVSS の baseScore を取得して表示する
     */
    getCvss() { 
        let url = `https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=${encodeURIComponent(this.cve)}`;
        // 採用優先順位 (新しいバージョンを優先)
        let keys = ["cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"];

        fetch(url)
            .then(
                response => {
                    if (!response.ok) {
                        throw new Error(response.status);
                    }
                    return response.json();
                }
            )
            .then(
                data => {
                    let metrics = data["vulnerabilities"][0]["cve"]["metrics"];
                    let score   = null;

                    for (let key of keys) {
                        if (metrics[key] && metrics[key].length > 0) {
                            score = metrics[key][0]["cvssData"]["baseScore"];
                            break;
                        }
                    }

                    if (score === null) {
                        throw new Error("no cvss");
                    }
                    this.show(this.cvss, Number(score).toFixed(1));
                }
            )
            .catch(
                () => {
                    this.show(this.cvss, this.empty);
                }
            );
    }

    /**
     * FIRST の EPSS API から EPSS 値を取得して表示する。
     */
    getEpss() {
        let url = `https://api.first.org/data/v1/epss?cve=${encodeURIComponent(this.cve)}`;

        fetch(url)
            .then(
                response => {
                    if (!response.ok) {
                        throw new Error(response.status);
                    }
                    return response.json();
                }
            )
            .then(
                data => {
                    if (!data["data"] || data["data"].length === 0) {
                        throw new Error("no epss");
                    }
                    let epss = Number(data["data"][0]["epss"]);
                    this.show(this.epss, epss.toFixed(5));
                }
            )
            .catch(
                () => {
                    this.show(this.epss, this.empty);
                }
            );
    }
}

//new GetCveScore("CVE-2021-44228", "cvss-value", "epss-value");
