class Polygon {
    constructor(
        { 
            place   = "cv", 
            n       = 3,
            time    = 5
        } = {}
    ) {
        this.fps    = 144
        this.time   = time
        this.cvs    = document.getElementById(place);
        this.ctx    = this.cvs.getContext("2d");
        this.r      = 200;
        this.n      = n;
        this.grad   = this.ctx.createLinearGradient(0, 0, 0, 600);
        this.grad.addColorStop(0,   'rgb(255, 255, 0)');
        this.grad.addColorStop(0.5, 'rgb(0, 255, 255)');
        this.grad.addColorStop(1,   'rgb(255, 0, 255)');
        this.draw();
        this.angle  = 0; // 回転角度
        this.animate();
    }

    draw() {
        this.ctx.clearRect(0, 0, 500, 500);
        this.ctx.beginPath();
        this.ctx.strokeStyle = this.grad;

        let theta = this.angle;
        let sides = Math.floor(this.n * 10000 + 0.5);
        for (let j = 0; j < 4 ; j++) {
            if (sides % 2 == 0) {
                sides = sides / 2;
            }
            if (sides % 5 == 0) {
                sides = sides / 5;
            }
        }

        this.ctx.moveTo(
            250 + this.r * Math.cos(theta),
            250 + this.r * Math.sin(theta)
        );

        for (let i = 0; i < sides + 1; i++) {
            theta += Math.PI * 2 / this.n;
            this.ctx.lineTo(
                250 + this.r * Math.cos(theta),
                250 + this.r * Math.sin(theta)
            );
        }

        this.ctx.stroke();
    }

    setN(num) {
        this.n = num;
        this.draw();
    }

    animate() {
        const delta = 2 * Math.PI / (this.fps * this.time);
        this.angle = (this.angle + delta) % (2 * Math.PI);

        // 1回転したかを判定
        if (this.prevAngle > this.angle) { // 角度が0に戻ったら1回転
            this.def_func()
        }
        this.prevAngle = this.angle;

        this.draw();
        requestAnimationFrame(() => this.animate());
    }

    def_func(){
        this.n = 2.5 + ((this.n + 0.1 - 2.5) % (50 - 2.5));
        console.clear();
        console.log(`${this.n}角形`)
    }
}