window.addEventListener(
    "load", 
    function() {
        setTimeout(
            function() {
                document.getElementById("loadingScreen").style.display = "none";
            }, 
            1000
        );
    }
);


function load_script(src) {
    return new Promise(
        (resolve, reject) => {
            const script = document.createElement("script");
            script.src = src;
            script.onload = () => {
                console.log(`[Load] [Success] ${src}`);
                resolve(); // 読み込み完了を通知
            };
            script.onerror = () => reject(new Error(`[Load] [Fail] ${src}`));
            document.body.appendChild(script);
        }
    );
}