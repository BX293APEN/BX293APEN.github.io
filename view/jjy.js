class JJYGenerate {
    constructor(
        controlButton = "control-button", 
        jjyCanvas = "canvas", 
        nowtimeID = "time", 
        summerTimeID = "summer-time",
        freq = 13333
    ) {
        this.freq = freq;
        this.AudioContext = window.AudioContext || window.webkitAudioContext;
        this.array = [];
        this.plus_leapsecond_list = [new Date(2017, 0, 1, 9)];
        this.offset = 0;
        this.pa = 0;
        this.signal = null;
        this.ctx = null;
        this.summer_time_input = document.getElementById(summerTimeID);
        this.nowtime = document.getElementById(nowtimeID);
        this.intervalId = null;
        this.canvas = document.getElementById(jjyCanvas);
        this.ctx2d = this.canvas.getContext('2d');
        this.w = this.canvas.width;
        this.h = this.canvas.height;
        this.play_flag = false;
        this.control_button = document.getElementById(controlButton);

        this.control_button.addEventListener('click', () => {
            if (this.play_flag) {
                this.control_button.innerText = "Start";
                this.play_flag = false;
                this.jjy_control("stop");
            } 
            else {
                this.control_button.innerText = "Stop";
                this.play_flag = true;
                this.jjy_control("start");
            }
        });

        this.render();
    }

    marker(s) {
        this.array.push(0.2);
        let t = s + this.offset;
        if (t < 0) return;
        this.osc = this.ctx.createOscillator();
        this.osc.type = "square";
        this.osc.frequency.value = this.freq;
        this.osc.start(t);
        this.osc.stop(t + 0.2);
        this.osc.connect(this.ctx.destination);
    }

    getleapsecond() {
        this.now = Date.now();
        for (let i = 0; i < this.plus_leapsecond_list.length; i++) {
            let diff = this.plus_leapsecond_list[i] - this.now;
            if (diff > 0 && diff <= 31 * 24 * 60 * 60 * 1000) {
                return 1;
            }
        }
        return 0;
    }

    bit(s, value, weight) {
        let b = value >= weight;
        value -= b ? weight : 0;
        this.pa += b ? 1 : 0;
        this.array.push(b ? 0.5 : 0.8);
        let t = s + this.offset;
        if (t < 0) return value;
        this.osc = this.ctx.createOscillator();
        this.osc.type = "square";
        this.osc.frequency.value = this.freq;
        this.osc.start(t);
        this.osc.stop(t + (b ? 0.5 : 0.8));
        this.osc.connect(this.ctx.destination);
        return value;
    }

    schedule(date, summer_time) {
        this.now = Date.now();
        this.start = date.getTime();
        this.offset = (this.start - this.now) / 1000 + this.ctx.currentTime;
        this.minute = date.getMinutes();
        this.hour = date.getHours();
        this.fullyear = date.getFullYear();
        this.year = this.fullyear % 100;
        this.week_day = date.getDay();
        this.year_day = (new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime() - new Date(date.getFullYear(), 0, 1).getTime()) / (24*60*60*1000) + 1;
        this.array = [];
        this.leapsecond = this.getleapsecond();
        this.marker(0); // マーカー(M)
        // 分
        this.pa = 0;
        this.minute = this.bit(1, this.minute,  40);
        this.minute = this.bit(2, this.minute,  20);
        this.minute = this.bit(3, this.minute,  10);
        this.minute = this.bit(4, this.minute,  16);
        this.minute = this.bit(5, this.minute,  8);
        this.minute = this.bit(6, this.minute,  4);
        this.minute = this.bit(7, this.minute,  2);
        this.minute = this.bit(8, this.minute,  1);
        this.pa2 = this.pa;
        this.marker(9); // P1
        // 時
        this.pa = 0;
        this.hour = this.bit(10, this.hour, 80);
        this.hour = this.bit(11, this.hour, 40);
        this.hour = this.bit(12, this.hour, 20);
        this.hour = this.bit(13, this.hour, 10);
        this.hour = this.bit(14, this.hour, 16);
        this.hour = this.bit(15, this.hour, 8);
        this.hour = this.bit(16, this.hour, 4);
        this.hour = this.bit(17, this.hour, 2);
        this.hour = this.bit(18, this.hour, 1);
        this.pa1 = this.pa;
        this.marker(19); // P2
        // 1月1日からの通算日
        this.year_day = this.bit(20, this.year_day, 800);
        this.year_day = this.bit(21, this.year_day, 400);
        this.year_day = this.bit(22, this.year_day, 200);
        this.year_day = this.bit(23, this.year_day, 100);
        this.year_day = this.bit(24, this.year_day, 160);
        this.year_day = this.bit(25, this.year_day, 80);
        this.year_day = this.bit(26, this.year_day, 40);
        this.year_day = this.bit(27, this.year_day, 20);
        this.year_day = this.bit(28, this.year_day, 10);
        this.marker(29); // P3
        this.year_day = this.bit(30, this.year_day, 8);
        this.year_day = this.bit(31, this.year_day, 4);
        this.year_day = this.bit(32, this.year_day, 2);
        this.year_day = this.bit(33, this.year_day, 1);
        this.bit(34, 0, 1); // 0
        this.bit(35, 0, 1); // 0
        this.bit(36, this.pa1 % 2, 1);
        this.bit(37, this.pa2 % 2, 1);
        this.bit(38, 0, 1); // SU1
        this.marker(39); // P4
        // SU2
        if (summer_time) {
            this.bit(40, 1, 1);
        } else {
            // 夏時間実施中（６日以内に夏時間から通常時間への変更なし）
            this.bit(40, 0, 1);
        }
        // 年
       this.year = this.bit(41,this.year, 80);
       this.year = this.bit(42,this.year, 40);
       this.year = this.bit(43,this.year, 20);
       this.year = this.bit(44,this.year, 10);
       this.year = this.bit(45,this.year, 8);
       this.year = this.bit(46,this.year, 4);
       this.year = this.bit(47,this.year, 2);
       this.year = this.bit(48,this.year, 1);
       this.marker(49); // P5
        // 曜日
       this.week_day = this.bit(50,this.week_day, 4);
       this.week_day = this.bit(51,this.week_day, 2);
       this.week_day = this.bit(52,this.week_day, 1);
        // うるう秒
        if (this.leapsecond === 0) {
            // うるう秒なし
            this.bit(53, 0, 1); // 0
            this.bit(54, 0, 1); // 0
        } else if (this.leapsecond > 0) {
            // 正のうるう秒
            this.bit(53, 1, 1); // 1
            this.bit(54, 1, 1); // 1
        } else {
            // 負のうるう秒
            this.bit(53, 1, 1); // 1
            this.bit(54, 0, 1); // 0
        }
        this.bit(55, 0, 1); // 0
        this.bit(56, 0, 1); // 0
        this.bit(57, 0, 1); // 0
        this.bit(58, 0, 1); // 0
        this.marker(59); // P0
        return this.array;
    }

    jjy_control(mode) {
        if (mode === "start") {
            this.ctx = new this.AudioContext();
            this.now = Date.now();
            this.t = Math.floor(this.now / (60 * 1000)) * 60 * 1000;
            let next = this.t + 60 * 1000;
            let delay = next - this.now - 1000;

            if (delay < 0) {
                this.t = next;
                delay += 60 * 1000;
            }

            this.signal = this.schedule(new Date(this.t), this.summer_time_input.checked);

            this.intervalId = setTimeout(() => {
                    this.interval();
                    this.intervalId = setInterval(this.interval.bind(this), 60 * 1000);
                }, 
                delay
            );
        } 
        else {
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }
            if (this.ctx) {
                this.ctx.close();
                this.ctx = null;
            }
            this.signal = undefined;
        }
    }

    interval() {
        //this.summer_time_input = document.getElementById("summer-time"); //ガベージコレクション対策
        this.t += 60 * 1000;
        this.signal = this.schedule(new Date(this.t), this.summer_time_input.checked);
    }

    render() {
        let i;
        this.nowtime.innerText = new Date().toString();
        this.ctx2d.clearRect(0, 0, this.w, this.h);

        if (!this.signal) {
            requestAnimationFrame(this.render.bind(this));
            return;
        }

        let now = Math.floor(Date.now() / 1000) % 60;
        for (i = 0; i < this.signal.length; i++) {
            if (i == now) {
                if (this.signal[i] < 0.3) this.ctx2d.fillStyle = "#FF0000";
                else if (this.signal[i] < 0.7) this.ctx2d.fillStyle = "#FFFF00";
                else this.ctx2d.fillStyle = "#00FF00";
            } 
            else {
                if (this.signal[i] < 0.3) this.ctx2d.fillStyle = "#7F0000";
                else if (this.signal[i] < 0.7) this.ctx2d.fillStyle = "#7F7F00";
                else this.ctx2d.fillStyle = "#007F00";
            }
            this.ctx2d.fillRect((i%30)*30, Math.floor(i/30)*100, 30 * this.signal[i], 80);
        }
        requestAnimationFrame(this.render.bind(this));
    }
    
}


new JJYGenerate(undefined,"jjyCode");