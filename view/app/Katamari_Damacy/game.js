class KatamariDamacy {
    constructor(
        {
            htmlStructure = {
                "easyButtonID"              : 'easyBtn',
                "normalButtonID"            : 'normalBtn',
                "hardButtonID"              : 'hardBtn',
                "cityButtonID"              : 'cityBtn',
                "parkButtonID"              : 'parkBtn',
                "tutorialCloseButtonID"     : 'tutorialCloseBtn',
                "tutorialID"                : 'tutorial',
                "resumeButtonID"            : 'resumeBtn',
                "pauseScreenID"             : 'pauseScreen',
                "helpButtonID"              : 'helpBtn',
                "nextLevelButtonID"         : 'nextLevelBtn',
                "minimapID"                 : 'minimap'

            },
            difficulty = {
                "easy" : {
                    "name"                  : '🌱 イージー',
                    "timeLimit"             : 600,          // 秒数
                    "targetCount"           : 150,
                    "sizeMultiplier"        : 1.15,
                    "growthBonus"           : 1.2,
                    "objects": {                            // オブジェクトの数を指定
                        "tiny"              : 80,           // 極小
                        "small"             : 60,           // 小
                        "medium"            : 40,           // 中
                        "large"             : 25,           // 大
                        "huge"              : 15,           // 超大
                        "moving"            : 10            // 動く
                    }
                },
                "normal": {
                    "name"                  : '⚖️ ノーマル',
                    "timeLimit"             : 480,
                    "targetCount"           : 200,
                    "sizeMultiplier"        : 1.3,
                    "growthBonus"           : 1.0,
                    "objects": {                            // オブジェクトの数を指定
                        "tiny"              : 80,           // 極小
                        "small"             : 60,           // 小
                        "medium"            : 40,           // 中
                        "large"             : 25,           // 大
                        "huge"              : 15,           // 超大
                        "moving"            : 10            // 動く
                    }
                },
                "hard" : {
                    "name"                  : '🔥 ハード',
                    "timeLimit"             : 360,
                    "targetCount"           : 250,
                    "sizeMultiplier"        : 1.5,
                    "growthBonus"           : 0.8,
                    "objects": {                            // オブジェクトの数を指定
                        "tiny"              : 80,           // 極小
                        "small"             : 60,           // 小
                        "medium"            : 40,           // 中
                        "large"             : 25,           // 大
                        "huge"              : 15,           // 超大
                        "moving"            : 10            // 動く
                    }
                }
            },
            stages = {
                "city" : {
                    "name"                  : '🏙️ 街',
                    "skyColor"              : 0x87CEEB,
                    "groundColor"           : 0x4A4A4A
                },
                "park" : {
                    "name"                  : '🌳 公園',
                    "skyColor"              : 0x87CEEB,
                    "groundColor"           : 0x2D5016
                },
            },
        }={}
    ){
        this.difficulty     = difficulty;
        this.stages         = stages;
        this.htmlStructure  = htmlStructure;
        this.config =   {
            "features" : {
                "pause"                     : true,
                "highScore"                 : true,
                "tutorial"                  : true,
                "movingObjects"             : true,
                "stageSelect"               : true,
                "comboSystem"               : true,
                "cameraSwitch"              : true,
                "minimap"                   : true
            },
            "sound" : {
                "baseFreq"                  : 440,
                "comboFreqBoost"            : 50,
                "volume"                    : 0.3
            },
            "visuals" : {
                "fogEnabled"                : true,
                "shadowQuality"             : 'medium',
                "particleCount"             : 30,
                "irregularBall"             : true,
                "cameraFov"                 : 60
            },
            "ball" : {
                "shape" : {                                 // 初期値設定
                    "size"                  : 0.5,
                    "color"                 : 0xFF69B4,
                    "mass"                  : 1.5,
                    "glow"                  : 0.3,          // 光り方
                },
                "grow" : {
                    "enable"                : true,
                    "raito"                 : 0.8,
                    "collectionRange"       : 1.5
                },
                "rotation" : {
                    "angularDamping"        : 0.02,         // 角速度減衰（0〜1、小さいほどよく回る）
                    "irregularity"          : 1.0,          // 回転のいびつさ（0〜1）
                    "spinBoost"             : 5.0           // 巻き込み時の回転ブースト
                },
            },
            "control" : {
                "speed" : 35,
                "jump"  : 12
            },
            
        }

        this.cameraModes = ['三人称視点', '肩越し視点', '一人称視点', '俯瞰視点']
        this.gameState = {
            ballSize: this.config["ball"]["shape"]["size"],
            collectedCount: 0,
            score: 0,
            objects: [],
            gameTime: 180,
            goalCount: 30,
            isGameOver: false,
            combo: 0,
            comboTimer: null,
            particles: []
        }
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.ballSize = [
            { min: 0, max: 50, name: '🐜 極小' },
            { min: 50, max: 150, name: '🎾 小' },
            { min: 150, max: 300, name: '⚽ 普通' },
            { min: 300, max: 600, name: '🚗 大' },
            { min: 600, max: 1200, name: '🏠 特大' },
            { min: 1200, max: Infinity, name: '🏙️ 巨大' }
        ];
        this.cameraMode = 0;
        this.currentDifficulty = null
        this.currentStage = null
        this.isPaused = false;

        this.keys = {};
        window.addEventListener(
            'keydown', 
            (e) => {
                this.keys[e.key] = true;

                if ((e.key === 'c' || e.key === 'C') && this.config["features"]["cameraSwitch"]) {
                    this.cameraMode = (this.cameraMode + 1) % 4;
                    document.getElementById('cameraMode').textContent = this.cameraModes[this.cameraMode];
                }
            
                if ((e.key === 'p' || e.key === 'P') && this.config["features"]["pause"]) {
                    if (!this.isPaused && !this.gameState.isGameOver) {
                        this.isPaused = true;
                        document.getElementById(this.htmlStructure["pauseScreenID"]).style.display = 'flex';
                    } 
                    else if (this.isPaused) {
                        this.isPaused = false;
                        document.getElementById(this.htmlStructure["pauseScreenID"]).style.display = 'none';
                    }
                }
            }
        );

        window.addEventListener(
            'keyup', 
            (e) => { 
                this.keys[e.key] = false; 
            }
        );

        window.addEventListener(
            'resize', 
            () => {
                if (this.camera) {
                    this.camera.aspect = window.innerWidth / window.innerHeight;
                    this.camera.updateProjectionMatrix();
                }
                if (this.renderer) {
                    this.renderer.setSize(window.innerWidth, window.innerHeight);
                }
            }
        );
        // イベントリスナー
        document.getElementById(this.htmlStructure["easyButtonID"]).onclick = () => this.selectDifficulty('easy');
        document.getElementById(this.htmlStructure["normalButtonID"]).onclick = () => this.selectDifficulty('normal');
        document.getElementById(this.htmlStructure["hardButtonID"]).onclick = () => this.selectDifficulty('hard');
        document.getElementById(this.htmlStructure["cityButtonID"]).onclick = () => this.selectStage('city');
        document.getElementById(this.htmlStructure["parkButtonID"]).onclick = () => this.selectStage('park');
        document.getElementById(this.htmlStructure["tutorialCloseButtonID"]).onclick = () => {
            document.getElementById(this.htmlStructure["tutorialID"]).style.display = 'none';
            this.startGame();
        };
        document.getElementById(this.htmlStructure["resumeButtonID"]).onclick = () => {
            this.isPaused = false;
            document.getElementById(this.htmlStructure["pauseScreenID"]).style.display = 'none';
        };
        document.getElementById(this.htmlStructure["helpButtonID"]).onclick = () => {
            document.getElementById(this.htmlStructure["tutorialID"]).style.display = 'flex';
            this.isPaused = true;
        };
        document.getElementById(this.htmlStructure["nextLevelButtonID"]).onclick = () => location.reload();

    }

    sounds_collect(frequency) {
        let osc = this.audioContext.createOscillator();
        let gain = this.audioContext.createGain();
        osc.connect(gain);
        gain.connect(this.audioContext.destination);
        osc.frequency.value = frequency;
        osc.type = 'sine';
        gain.gain.setValueAtTime(this.config["sound"]["volume"], this.audioContext.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
        osc.start();
        osc.stop(this.audioContext.currentTime + 0.3);
    }
    sounds_bigCollect() {
        let osc = this.audioContext.createOscillator();
        let gain = this.audioContext.createGain();
        osc.connect(gain);
        gain.connect(this.audioContext.destination);
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, this.audioContext.currentTime);
        osc.frequency.exponentialRampToValueAtTime(220, this.audioContext.currentTime + 0.5);
        gain.gain.setValueAtTime(this.config["sound"]["volume"] + 0.1, this.audioContext.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
        osc.start();
        osc.stop(this.audioContext.currentTime + 0.5);
    }
    save(score) {
        if (!this.config["features"]["highScore"]) return false;
        const current = this.get_score();
        if (score > current) {
            localStorage.setItem('katamariHighScore', score);
            return true;
        }
        return false;
    }
    get_score() {
        if (!this.config["features"]["highScore"]) return 0;
        return parseInt(localStorage.getItem('katamariHighScore') || '0');
    }
    display() {
        if (!this.config["features"]["highScore"]) return;
        document.getElementById('highScore').textContent = this.get_score().toLocaleString();
    }

    selectDifficulty(diff) {
        this.currentDifficulty = this.difficulty[diff];
        document.getElementById('difficultySelect').style.display = 'none';
        if (this.config["features"]["stageSelect"]) {
            document.getElementById('stageSelect').style.display = 'flex';
        } 
        else {
            this.currentStage = this.stages["city"];
            if (this.config["features"]["tutorial"] && !localStorage.getItem('katamariTutorialShown')) {
                document.getElementById(this.htmlStructure["tutorialID"]).style.display = 'flex';
            } 
            else {
                this.startGame();
            }
        }
    }
    selectStage(stage) {
        this.currentStage = this.stages[stage];
        document.getElementById('stageSelect').style.display = 'none';
        if (this.config["features"]["tutorial"] && !localStorage.getItem('katamariTutorialShown')) {
            document.getElementById(this.htmlStructure["tutorialID"]).style.display = 'flex';
        } 
        else {
            this.startGame();
        }
    }
    startGame() {
        if (this.config["features"]["tutorial"]) {
            localStorage.setItem('katamariTutorialShown', 'true');
        }
        this.gameState.gameTime = this.currentDifficulty["timeLimit"];
        this.gameState.goalCount = this.currentDifficulty["targetCount"];
        document.getElementById('goal').textContent = this.currentDifficulty["targetCount"];
        document.getElementById('difficultyLabel').textContent = this.currentDifficulty["name"];
        document.getElementById('stageLabel').textContent = this.currentStage["name"];
        this.display();

        this.initGame();
    }

    initGame() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.currentStage["skyColor"]);
  
        if (this.config["visuals"]["fogEnabled"]) {
            this.scene.fog = new THREE.Fog(this.currentStage["skyColor"], 50, 250);
        }
  
        this.camera = new THREE.PerspectiveCamera(this.config["visuals"]["cameraFov"], window.innerWidth / window.innerHeight, 0.1, 500);
        this.camera.position.set(0, 15, 25);
  
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);
  
        this.controls = {
            mouseDown: false,
            mouseX: 0,
            mouseY: 0,
            rotateX: 0.3,  // ★初期角度を調整★
            rotateY: 0
        };
  
        this.renderer.domElement.addEventListener(
            'mousedown', 
            (e) => {
                this.controls.mouseDown = true;
                this.controls.mouseX    = e.clientX;
                this.controls.mouseY    = e.clientY;
            }
        );
  
        this.renderer.domElement.addEventListener(
            'mouseup', 
            () => {
                this.controls.mouseDown = false;
            }
        );
  
        this.renderer.domElement.addEventListener(
            'mousemove', 
            (e) => {
                if (this.controls.mouseDown && this.cameraMode === 0) {
                    const deltaX = e.clientX - this.controls.mouseX;
                    const deltaY = e.clientY - this.controls.mouseY;
                    this.controls.rotateX -= deltaY * 0.005;
                    this.controls.rotateY -= deltaX * 0.005;
                    this.controls.rotateX = Math.max(0.1, Math.min(Math.PI / 2.5, this.controls.rotateX));
                    this.controls.mouseX = e.clientX;
                    this.controls.mouseY = e.clientY;
                }
            }
        );
  
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
  
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(50, 100, 50);
        this.scene.add(dirLight);
  
        const pointLight = new THREE.PointLight(this.config["ball"]["shape"]["color"], 1, 50);
        pointLight.position.set(0, 10, 0);
        this.scene.add(pointLight);
  
        this.world = new CANNON.World();
        this.world.gravity.set(0, -20, 0);
  
        const groundShape = new CANNON.Plane();
        const groundBody = new CANNON.Body(
            { 
                mass: 0 
            }
        );

        groundBody.addShape(groundShape);
        groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
        this.world.add(groundBody);
  
        const groundGeometry = new THREE.PlaneGeometry(300, 300);
        const groundMaterial = new THREE.MeshStandardMaterial({ color: this.currentStage["groundColor"] });
        const groundMesh = new THREE.Mesh(groundGeometry, groundMaterial);
        groundMesh.rotation.x = -Math.PI / 2;
        this.scene.add(groundMesh);
  
        this.ballRadius = this.gameState.ballSize;
        this.ballBody = new CANNON.Body(
            {
                mass: this.config["ball"]["shape"]["mass"],
                position: new CANNON.Vec3(0, this.ballRadius + 2, 0),
                linearDamping: 0.3,
                angularDamping: this.config["ball"]["rotation"]["angularDamping"]
            }
        );
        this.ballBody.addShape(new CANNON.Sphere(this.ballRadius));
        this.world.add(this.ballBody);
  
        const ballGeometry = new THREE.SphereGeometry(this.ballRadius, 32, 32);
        const ballMaterial = new THREE.MeshStandardMaterial(
            {
                color               : this.config["ball"]["shape"]["color"],
                emissive            : this.config["ball"]["shape"]["color"],
                emissiveIntensity   : this.config["ball"]["glow"],
                transparent         : true,
                opacity             : 0.4
            }
        );
        this.ballMesh = new THREE.Mesh(ballGeometry, ballMaterial);
        this.scene.add(this.ballMesh);

        this.attachedGroup = new THREE.Group();
        this.scene.add(this.attachedGroup);
  
        this.spawnObjects();
        this.animate();
        this.updateTimer();
        this.updateSizeClass();  // ★初期化時に呼ぶ★


        setInterval(
            () => {
                if (this.gameState.gameTime > 0 && !this.gameState.isGameOver && !this.isPaused) {
                    this.gameState.gameTime--;
                    this.updateTimer();
                }
                if (this.gameState.gameTime <= 0 && !this.gameState.isGameOver) this.endGame();
            }, 
            1000
        );
    }
    spawnObjects() {
        for (let i = 0; i < this.currentDifficulty["objects"]["tiny"]; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = 5 + Math.random() * 15;
            this.createObject(Math.cos(angle) * radius, Math.sin(angle) * radius, 0.2 + Math.random() * 0.15);
        }

        for (let i = 0; i < this.currentDifficulty["objects"]["small"]; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = 15 + Math.random() * 20;
            this.createObject(Math.cos(angle) * radius, Math.sin(angle) * radius, 0.4 + Math.random() * 0.4);
        }

        for (let i = 0; i < this.currentDifficulty["objects"]["medium"]; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = 35 + Math.random() * 25;
            this.createObject(Math.cos(angle) * radius, Math.sin(angle) * radius, 0.8 + Math.random() * 1.0);
        }

        for (let i = 0; i < this.currentDifficulty["objects"]["large"]; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = 60 + Math.random() * 25;
            this.createObject(Math.cos(angle) * radius, Math.sin(angle) * radius, 2.5 + Math.random() * 2.5);
        }

        for (let i = 0; i < this.currentDifficulty["objects"]["huge"]; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = 90 + Math.random() * 30;
            this.createObject(Math.cos(angle) * radius, Math.sin(angle) * radius, 6.0 + Math.random() * 4.0);
        }
    }   

    createObject(x, z, size) {
        const geometry = new THREE.BoxGeometry(size, size, size);
        const material = new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff });
        const mesh = new THREE.Mesh(geometry, material);
        this.scene.add(mesh);
        
        const body = new CANNON.Body(
            { 
                mass: size * 0.5, 
                position: new CANNON.Vec3(x, size/2 + 0.5, z) 
            }
        );

        body.addShape(new CANNON.Box(new CANNON.Vec3(size/2, size/2, size/2)));
        this.world.add(body);
        
        this.gameState.objects.push(
            { 
                mesh, 
                body, 
                size, 
                collected: false, 
                points: Math.floor(size * 50) 
            }
        );
    }

    addCombo() {
        if (!this.config["features"]["comboSystem"]) return;
        this.gameState.combo++;
        document.getElementById('comboCount').textContent = this.gameState.combo;
        document.getElementById('combo').style.display = 'block';
        clearTimeout(this.gameState.comboTimer);
        this.gameState.comboTimer = setTimeout(() => {
            this.gameState.combo = 0;
            document.getElementById('combo').style.display = 'none';
        }, 2000);
    }

    updateTimer() {
        const min = Math.floor(this.gameState.gameTime / 60);
        const sec = this.gameState.gameTime % 60;
        document.getElementById('timer').textContent = `${min}:${sec.toString().padStart(2, '0')}`;
    
        if (this.gameState.gameTime <= 30) {
            document.getElementById('timer').style.color = '#ff0000';
        }
    }
    showNotification(text) {
        const notif = document.getElementById('notification');
        notif.textContent = text;
        notif.style.display = 'block';
        setTimeout(
            () => {
                notif.style.display = 'none';
            }, 
            2000
        );
    }

    updateSizeClass() {
        const sizeCm = this.gameState.ballSize * 100;
        const sizeClass = this.ballSize.find(c => sizeCm >= c.min && sizeCm < c.max);
        if (sizeClass) {  // ★undefinedチェック★
            document.getElementById('sizeClass').textContent = `クラス: ${sizeClass.name}`;
        }
        document.getElementById('size').textContent = Math.floor(sizeCm);
    }

    drawMinimap() {
        if (!this.config["features"]["minimap"]) return;
        const canvas = document.getElementById(this.htmlStructure["minimapID"]);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, 200, 200);
        ctx.fillStyle = 'rgba(0, 50, 0, 0.5)';
        ctx.fillRect(0, 0, 200, 200);
        
        const scale = 200 / 200;
        const centerX = 100;
        const centerY = 100;
        
        this.gameState.objects.forEach(
            obj => {
                if (!obj.collected) {
                    ctx.fillStyle = '#ffff00';
                    ctx.fillRect(centerX + obj.body.position.x * scale - 1, centerY + obj.body.position.z * scale - 1, 2, 2);
                }
            }
        );

        ctx.fillStyle = '#ff69b4';
        ctx.beginPath();
        ctx.arc(centerX + this.ballBody.position.x * scale, centerY + this.ballBody.position.z * scale, 5, 0, Math.PI * 2);
        ctx.fill();
    }

    animate() {
        requestAnimationFrame(() => this.animate());
    
        if (this.isPaused) {
            this.renderer.render(this.scene, this.camera);
            return;
        }

        const force = this.config["control"]["speed"];
        if (this.keys['w'] || this.keys['ArrowUp']) this.ballBody.applyForce(new CANNON.Vec3(0, 0, -force), this.ballBody.position);
        if (this.keys['s'] || this.keys['ArrowDown']) this.ballBody.applyForce(new CANNON.Vec3(0, 0, force), this.ballBody.position);
        if (this.keys['a'] || this.keys['ArrowLeft']) this.ballBody.applyForce(new CANNON.Vec3(-force, 0, 0), this.ballBody.position);
        if (this.keys['d'] || this.keys['ArrowRight']) this.ballBody.applyForce(new CANNON.Vec3(force, 0, 0), this.ballBody.position);
        if (this.keys[' '] && this.ballBody.position.y < this.ballRadius + 0.5) this.ballBody.velocity.y = this.config["control"]["jump"];

        this.world.step(1/60);

        this.ballMesh.position.copy(this.ballBody.position);
        this.ballMesh.quaternion.copy(this.ballBody.quaternion);
        this.attachedGroup.position.copy(this.ballBody.position);
        this.attachedGroup.quaternion.copy(this.ballBody.quaternion);

        this.gameState.objects.forEach(
            obj => {
                if (!obj.collected) {
                    obj.mesh.position.copy(obj.body.position);
                    obj.mesh.quaternion.copy(obj.body.quaternion);
                    
                    const dx = this.ballBody.position.x - obj.body.position.x;
                    const dy = this.ballBody.position.y - obj.body.position.y;
                    const dz = this.ballBody.position.z - obj.body.position.z;
                    const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                    
                    const requiredSize = obj.size * this.currentDifficulty.sizeMultiplier;
                    const canCollect = this.gameState.ballSize >= requiredSize;
                    const collectionRange = (this.ballRadius + obj.size) * this.config["ball"]["grow"]["collectionRange"];  // ★判定を拡大★
                    
                    if (dist < collectionRange && canCollect) {
                        obj.collected = true;
                        this.world.remove(obj.body);
                        this.scene.remove(obj.mesh);

                        const theta = Math.random() * Math.PI * 2;
                        const phi = Math.acos(2 * Math.random() - 1);
                        const r = this.ballRadius * (0.8 + Math.random() * 0.4);

                        const relPos = new THREE.Vector3(
                            r * Math.sin(phi) * Math.cos(theta),
                            r * Math.sin(phi) * Math.sin(theta),
                            r * Math.cos(phi)
                        );

                        obj.mesh.position.copy(relPos);
                        obj.mesh.rotation.set(
                            Math.random() * Math.PI * 2, 
                            Math.random() * Math.PI * 2, 
                            Math.random() * Math.PI * 2
                        );
                        const scale = 0.7 + Math.random() * 0.3;
                        obj.mesh.scale.set(scale, scale, scale);
                        this.attachedGroup.add(obj.mesh);

                        this.gameState.collectedCount++;
                        const comboBonus = this.config["features"]["comboSystem"] && this.gameState.combo > 0 ? this.gameState.combo * 5 : 0;
                        this.gameState.score += obj.points + comboBonus;

                        // ★体積ベースの成長★
                        if (this.config["ball"]["grow"]["enable"]) {
                            const objVolume = obj.size * obj.size * obj.size;
                            const currentVolume = (4/3) * Math.PI * Math.pow(this.ballRadius, 3);
                            const newVolume = currentVolume + (objVolume * this.config["ball"]["grow"]["raito"]);
                            const newRadius = Math.pow((3 * newVolume) / (4 * Math.PI), 1/3);
                            this.gameState.ballSize = newRadius;
                            this.ballRadius = newRadius;
                        }

                        document.getElementById('count').textContent = this.gameState.collectedCount;
                        document.getElementById('score').textContent = this.gameState.score;
                        this.updateSizeClass();

                        const frequency = 
                            this.config["sound"]["baseFreq"] + 
                            (
                                this.config["features"]["comboSystem"] ? 
                                this.gameState.combo * this.config["sound"]["comboFreqBoost"] : 0
                            );

                        if (obj.size > 5) {
                            this.sounds_bigCollect();
                            this.showNotification(`🏠 ${obj.size.toFixed(1)}mを巻き込んだ！`);
                        } 
                        else {
                            this.sounds_collect(frequency);
                        }

                        if (this.config["features"]["comboSystem"]) this.addCombo();

                        const spinBoost = this.config["ball"]["rotation"]["spinBoost"];
                        const randomSpin = new CANNON.Vec3(
                            (Math.random() - 0.5) * spinBoost,
                            (Math.random() - 0.5) * spinBoost,
                            (Math.random() - 0.5) * spinBoost
                        );

                        const prevAngularVelocity = this.ballBody.angularVelocity.vadd(randomSpin);
                        this.world.remove(this.ballBody);
                        this.ballBody = new CANNON.Body(
                            {
                                mass: this.config["ball"]["shape"]["mass"],
                                position: this.ballBody.position,
                                velocity: this.ballBody.velocity,
                                angularVelocity: prevAngularVelocity,
                                linearDamping: 0.3,
                                angularDamping: this.config["ball"]["rotation"]["angularDamping"]
                            }
                        );
                        this.ballBody.addShape(new CANNON.Sphere(this.ballRadius));
                        this.world.add(this.ballBody);

                        this.scene.remove(this.ballMesh);
                        this.ballMesh.geometry.dispose();
                        this.ballMesh.geometry = new THREE.SphereGeometry(this.ballRadius, 32, 32);
                        this.scene.add(this.ballMesh);

                        if (this.gameState.collectedCount >= this.gameState.goalCount) this.endGame(true);
                  }
                }
            }
        );

        // ★カメラ制御を修正★
        if (this.config["features"]["cameraSwitch"]) {
            if (this.cameraMode === 0) {
                const dist = 8 + this.ballRadius * 2;
                const height = 5 + this.ballRadius;
                this.camera.position.x = this.ballBody.position.x + Math.sin(this.controls.rotateY) * dist * Math.cos(this.controls.rotateX);
                this.camera.position.y = this.ballBody.position.y + height + dist * Math.sin(this.controls.rotateX);
                this.camera.position.z = this.ballBody.position.z + Math.cos(this.controls.rotateY) * dist * Math.cos(this.controls.rotateX);
                this.camera.lookAt(this.ballBody.position.x, this.ballBody.position.y + this.ballRadius * 0.5, this.ballBody.position.z);
            
            } 
            else if (this.cameraMode === 1) {
                const dist = 5 + this.ballRadius * 1.5;
                const height = this.ballRadius * 2;
                this.camera.position.x = this.ballBody.position.x + Math.sin(this.controls.rotateY) * dist;
                this.camera.position.y = this.ballBody.position.y + height;
                this.camera.position.z = this.ballBody.position.z + Math.cos(this.controls.rotateY) * dist;
                
                const lookAtDist = 10;
                this.camera.lookAt(
                  this.ballBody.position.x - Math.sin(this.controls.rotateY) * lookAtDist,
                  this.ballBody.position.y,
                  this.ballBody.position.z - Math.cos(this.controls.rotateY) * lookAtDist
                );
            } 
            else if (this.cameraMode === 2) {
                this.camera.position.set(this.ballBody.position.x, this.ballBody.position.y, this.ballBody.position.z);
                
                const lookAtDist = 10;
                this.camera.lookAt(
                    this.ballBody.position.x - Math.sin(this.controls.rotateY) * lookAtDist,
                    this.ballBody.position.y,
                    this.ballBody.position.z - Math.cos(this.controls.rotateY) * lookAtDist
                );

            } 
            else {
                this.camera.position.set(this.ballBody.position.x, this.ballBody.position.y + 50, this.ballBody.position.z);
                this.camera.lookAt(this.ballBody.position.x, this.ballBody.position.y, this.ballBody.position.z);
            }
        }

        if (this.config["features"]["minimap"]) this.drawMinimap();

        this.renderer.render(this.scene, this.camera);
    }

    endGame(win = false) {
        this.gameState.isGameOver = true;
        const title = document.getElementById('resultTitle');
        const text = document.getElementById('resultText');
        
        const isNewRecord = this.save(this.gameState.score);
        
        if (win) {
            title.textContent = '🎉 クリア！';
            title.style.color = '#4CAF50';
            text.innerHTML = `
                ${isNewRecord ? '🎊 新記録！<br>' : ''}
                スコア: ${this.gameState.score.toLocaleString()}点<br>
                巻き込み: ${this.gameState.collectedCount}個<br>
                最終サイズ: ${Math.floor(this.gameState.ballSize * 100)}cm
            `;
        } 
        else {
            title.textContent = '⏰ タイムアップ';
            title.style.color = '#F44336';
            text.innerHTML = `
                ${isNewRecord ? '🎊 新記録！<br>' : ''}
                スコア: ${this.gameState.score.toLocaleString()}点<br>
                巻き込み: ${this.gameState.collectedCount}/${this.gameState.goalCount}個<br>
                最終サイズ: ${Math.floor(this.gameState.ballSize * 100)}cm
            `;
        }

        document.getElementById('gameOver').style.display = 'block';
    }

}