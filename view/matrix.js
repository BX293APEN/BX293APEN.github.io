class MatrixDraw{ // マトリックス風にするキャンバスの設定
    constructor(
        {
            canvasName  = 'matrix',
            charSize    = 4,
            fontFamily  = "monospace",
            chars       =  ["0","1","2","3","4","5","6","7","8","9", "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],
            width,      // 省略時はブラウザの表示領域に追従
            height      // 省略時はブラウザの表示領域に追従
        } = {}
    ){
        this.charSize       = charSize;
        this.fontFamily     = fontFamily;
        this.chars          = chars;
        this.fixedWidth     = width;
        this.fixedHeight    = height;
        this.canvas         = document.getElementById(canvasName);
        this.ctx            = this.canvas.getContext('2d');
        this.columns        = [];
        this.resize();
        window.addEventListener('resize', this.resize.bind(this)); // 画面サイズ・ズーム変更に対応
        setInterval(this.update_matrix.bind(this), 33);// 一定間隔で更新
    }
    resize() { // キャンバスのサイズ調整
        const isFirst = this.columns.length === 0;
        this.canvas.width  = this.fixedWidth  ?? window.innerWidth;
        this.canvas.height = this.fixedHeight ?? window.innerHeight;

        // 列数を作り直す(既存の列の位置は引き継ぐ)
        const count = Math.ceil(this.canvas.width / this.charSize);
        this.columns = Array.from(
            { length: count }, 
            (_, i) => {
                if (i < this.columns.length) return this.columns[i];
                if (isFirst) return 1;
                // 増えた列はバラバラの高さから開始する
                return Math.floor(Math.random() * this.canvas.height / this.charSize) * this.charSize;
            }
        );

        // canvasのサイズを変えるとctxの設定がリセットされるので再設定
        this.ctx.font = `normal ${this.charSize}px ${this.fontFamily}`;
    }
    get_random_char() { // 乱数生成関数
        return this.chars[Math.floor(Math.random() * this.chars.length)];
        //String.fromCharCode(30000 + Math.random() * 33);
    }
    update_matrix() {// 更新処理
        // 背景を徐々に暗くする
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
        // 文字を描画
        this.ctx.fillStyle = '#0F0';
        this.columns.forEach((y, x) => {
            this.ctx.fillText(
                this.get_random_char(), 
                x * this.charSize, y
            );
            this.columns[x] = y > this.canvas.height + Math.random() * 10000 ? 0 : y + this.charSize;
        });
    }
}


// new MatrixDraw();
