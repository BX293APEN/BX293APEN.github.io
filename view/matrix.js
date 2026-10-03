class MatrixDraw{ // マトリックス風にするキャンバスの設定
    constructor(
        {
            canvasName  = 'matrix',
            charSize    = 4,
            fontFamily  = "monospace",
            chars       =  ["0","1","2","3","4","5","6","7","8","9", "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],
            width       = window.innerWidth,
            height      = window.innerHeight
        } = {}
    ){
        this.charSize       = charSize
        this.canvas         = document.getElementById(canvasName);
        this.canvas.width = width;
        this.canvas.height = height;
        this.ctx            = this.canvas.getContext('2d');
        this.columns        = Array(Math.floor(this.canvas.width / this.charSize)).fill(1); // 配列の初期化
        this.chars          = chars;
        setInterval(this.update_matrix.bind(this), 33);// 一定間隔で更新
        this.ctx.font       = `normal ${this.charSize}px ${fontFamily}`
    }
    get_random_char() { // 乱数生成関数
        return this.chars[Math.floor(Math.random() * this.chars.length)];
        //String.fromCharCode(30000 + Math.random() * 33);
    };
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
    };
}


// new MatrixDraw();

