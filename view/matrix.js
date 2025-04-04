// キャンバスの設定
const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');
canvas.width = window.screen.width;
canvas.height = window.screen.height;

// 乱数生成関数
const getRandomChar = () => {
    //const chars = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9"];
    const chars = ["0","1","2","3","4","5","6","7","8","9", "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    return chars[Math.floor(Math.random() * chars.length)];
    //String.fromCharCode(30000 + Math.random() * 33);
};

// 配列の初期化
const columns = Array(256).fill(1);

// 更新処理
const update_matrix = () => {
    // 背景を徐々に暗くする
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 文字を描画
    ctx.fillStyle = '#0F0';
    columns.forEach((y, x) => {
        ctx.fillText(getRandomChar(), x * 10, y);
        columns[x] = y > 758 + Math.random() * 10000 ? 0 : y + 10;
    });
};

// 一定間隔で更新
setInterval(update_matrix, 33);
