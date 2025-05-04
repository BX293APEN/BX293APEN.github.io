class ConsoleText{
    constructor (
        canvasName          = 'consoleText',
        textList            = ["Hello World!"],
        cursorList          = ["_"],
        isLoop             = false,
        width               = 400,
        height              = 58,
        fontSize            = "20px",
        fontFamily          = "monospace",
        fontColor           = 'rgba(0, 255, 0, 1)',
        fontShadowColor     = 'rgba(0, 0, 0, .3)',
        bgColor             = "#101010",
        bgShadowColor       = "#191919",
        shadowColor         = '#3f3',
        changeInterval      = 800,
        changeTime          = 10,
    ){
        this.canvas                     = document.getElementById(canvasName);
        this.canvas.style.background    = bgColor;
        this.canvas.style.boxShadow     = `0 0 0 2px ${bgShadowColor}`;
        this.canvas.style.display       = "block";
        this.ctx                        = this.canvas.getContext('2d');
        this.canvas.width               = width;
        this.canvas.height              = height;
        this.ctx.font                   = `normal ${fontSize} ${fontFamily}`;
        this.ctx.textAlign              = 'left';
        this.ctx.textBaseline           = 'top';
        this.ctx.fillStyle              = fontColor;
        this.ctx.strokeStyle            = fontShadowColor;
        this.ctx.shadowColor            = shadowColor;
        this.messagesArray              = textList;
        this.totalMessages              = this.messagesArray.length-1;
        this.cursor                     = cursorList;
        this.page                       = 0;
        this.pointer                    = 0;
        this.typeTick                   = 0;
        this.typeTickMax                = 0;

        this.minTick                    = 5;
        this.maxTick                    = 10;
        this.typeResetTick              = 0;
        this.typeResetMax               = 15;
        this.text                       = [];      
        this.isLoop                     = isLoop
        this.isVisible                  = true;
        this.changeInterval             = changeInterval;
        this.changeTime                 = changeTime;
        this.timeoutID                  = undefined;

        this.setup();
        this.loop();
    }

    setup(){
        this.messageArray   = this.messagesArray[this.page].split('');
        this.messageLength  = this.messageArray.length;
        
    }


    renderMessage(){
        switch(this.cursor[this.page]){
            case "\n":   // ... NO ANIMATION
                this.text= this.messageArray.slice(0, this.messageLength);
                break;

            default:
                this.text = this.messageArray.slice(0, this.pointer);
                this.text[this.pointer] = this.cursor[this.page];
                break;
        }
        //this.ctx.shadowBlur = 9;
        this.ctx.fillText(this.text.join(''), 20, 20);
        //this.ctx.shadowBlur = 0;
    }

    renderLines(){
        this.ctx.beginPath();
        for(let i = 0; i < this.canvas.height/2; i += 1){    
            this.ctx.moveTo(0, (i*2) + .5);
            this.ctx.lineTo(this.canvas.width, (i*2) + .5);    
        } 
        this.ctx.stroke();
    }

    blinkingText(){
        let lastChar = this.cursor[this.page]
        if (lastChar != "\n"){
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillText(this.text.slice(0, -1).join(''), 20, 20);
            if (this.isVisible) {
                this.ctx.fillText(lastChar, 20 + this.ctx.measureText(this.text.slice(0, -1).join('')).width, 20);
            } 
            this.renderLines();
            this.isVisible = !this.isVisible;
            this.timeoutID = setTimeout(this.blinkingText.bind(this), this.isVisible ? 500 : 500);
        }
    }

    loop(){
        let changeTime = this.changeTime;
        if(this.pointer < this.messageLength){
            if(this.typeTick < this.typeTickMax){
                this.typeTick++;
            } 
            else {
                this.typeTick = 0;
                this.pointer++; 
                this.typeTickMax= Math.floor((Math.random()*this.maxTick)+this.minTick);
            
            }
        } 
        else {
            if(this.typeResetTick < this.typeResetMax){
                this.typeResetTick++;
            } 
            else { 
                this.typeResetTick = 0;
                this.typeTick = 0;
                this.pointer = 0;
           
                // ...change message... //      
                if(this.page<this.totalMessages)    this.page++;
                else if(this.isLoop)                this.page=0;
                else{
                    setTimeout(this.blinkingText.bind(this), 300);
                    return;
                }
                this.setup();
                changeTime += this.changeInterval;
       
            }
        }
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.renderMessage();
        this.renderLines();
        this.timeoutID = setTimeout(this.loop.bind(this), changeTime);
    }
}

//new ConsoleText();