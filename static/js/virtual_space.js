// Three.js 기반 문무대교회 3D 인터랙티브 가상 목양실
let scene, camera, renderer, controls;
let raycaster, mouse;
let interactiveObjects = [];
let audioPlaying = false;
let bgmAudio = null;

document.addEventListener("DOMContentLoaded", () => {
    initThreeSpace();
    initAudio();
});

function initAudio() {
    // 경건하고 잔잔한 로열티 프리 찬양 피아노 음원
    bgmAudio = new Audio("https://cdn.freesound.org/previews/612/612089_11861866-lq.mp3");
    bgmAudio.loop = true;
    bgmAudio.volume = 0.4;
}

function toggleBgm() {
    const btn = document.getElementById("btn-bgm-toggle");
    if (!bgmAudio) return;

    if (audioPlaying) {
        bgmAudio.pause();
        audioPlaying = false;
        if (btn) btn.innerHTML = `<i class="fa-solid fa-volume-xmark mr-1"></i> BGM 켜기`;
        showToast("찬양 배경음악이 일시정지되었습니다.", "info");
    } else {
        bgmAudio.play().then(() => {
            audioPlaying = true;
            if (btn) btn.innerHTML = `<i class="fa-solid fa-volume-high text-gold-400 mr-1 animate-pulse"></i> BGM 끄기`;
            showToast("은혜로운 피아노 찬양이 재생됩니다.", "success");
        }).catch(e => {
            console.log("Audio play blocked:", e);
            showToast("오디오 재생을 위해 화면을 한 번 클릭해 주세요.", "info");
        });
    }
}

function initThreeSpace() {
    const container = document.getElementById("canvas-container");
    if (!container) return;

    // 1. 씬 및 카메라 설정
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1d38);
    scene.fog = new THREE.FogExp2(0x0f1d38, 0.035);

    camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 4.5, 9);

    // 2. 렌더러 설정
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // 3. 궤도 컨트롤러 (마우스 회전/줌)
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 + 0.05; // 바닥 밑으로 못 내려가게
    controls.minDistance = 2;
    controls.maxDistance = 14;
    controls.target.set(0, 2, 0);

    // 4. 조명 시스템 (따뜻하고 은혜로운 빛)
    const ambientLight = new THREE.AmbientLight(0xfff6e5, 0.7);
    scene.add(ambientLight);

    // 십자가 집중 조명
    const crossSpot = new THREE.SpotLight(0xffd700, 2.5);
    crossSpot.position.set(0, 8, 2);
    crossSpot.target.position.set(0, 3.5, -5.8);
    crossSpot.angle = Math.PI / 4;
    crossSpot.penumbra = 0.8;
    crossSpot.castShadow = true;
    scene.add(crossSpot);
    scene.add(crossSpot.target);

    // 방 내부 따뜻한 포인트 라이트
    const roomLight = new THREE.PointLight(0xffecd2, 1.2, 20);
    roomLight.position.set(2, 6, 2);
    scene.add(roomLight);

    // 5. 3D 목양실 룸 구축
    buildRoom();

    // 6. 가구 및 인터랙티브 오브젝트 추가
    buildFurniture();

    // 7. 레이캐스터 (클릭 감지)
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    renderer.domElement.addEventListener("click", onDocumentClick);
    window.addEventListener("resize", onWindowResize);

    // 8. 렌더 루프
    animate();
}

function buildRoom() {
    // 바닥 (고급 원목 마루 텍스처 느낌)
    const floorGeo = new THREE.PlaneGeometry(16, 16);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x4a2e18, roughness: 0.6, metalness: 0.1 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // 중앙 원형 러그
    const rugGeo = new THREE.CircleGeometry(3.8, 32);
    const rugMat = new THREE.MeshStandardMaterial({ color: 0x8b1c1c, roughness: 0.9 });
    const rug = new THREE.Mesh(rugGeo, rugMat);
    rug.rotation.x = -Math.PI / 2;
    rug.position.y = 0.01;
    scene.add(rug);

    // 뒷벽 (십자가 걸린 벽)
    const backWallGeo = new THREE.PlaneGeometry(16, 8);
    const backWallMat = new THREE.MeshStandardMaterial({ color: 0x1b2845, roughness: 0.8 });
    const backWall = new THREE.Mesh(backWallGeo, backWallMat);
    backWall.position.set(0, 4, -6);
    scene.add(backWall);

    // 좌측 벽
    const leftWall = new THREE.Mesh(backWallGeo, backWallMat);
    leftWall.rotation.y = Math.PI / 2;
    leftWall.position.set(-6, 4, 0);
    scene.add(leftWall);

    // 우측 벽 (창문이 있는 벽)
    const rightWall = new THREE.Mesh(backWallGeo, backWallMat);
    rightWall.rotation.y = -Math.PI / 2;
    rightWall.position.set(6, 4, 0);
    scene.add(rightWall);

    // 햇살 창문 표현
    const windowGeo = new THREE.PlaneGeometry(3, 4);
    const windowMat = new THREE.MeshBasicMaterial({ color: 0xebf4fa });
    const windowMesh = new THREE.Mesh(windowGeo, windowMat);
    windowMesh.rotation.y = -Math.PI / 2;
    windowMesh.position.set(5.98, 4.2, 0);
    scene.add(windowMesh);
}

function buildFurniture() {
    // 1. 빛나는 대형 벽걸이 십자가 (핵심 핫스팟)
    const crossGroup = new THREE.Group();
    const crossMat = new THREE.MeshStandardMaterial({ 
        color: 0xffd700, 
        metalness: 0.8, 
        roughness: 0.2, 
        emissive: 0xaa7c11,
        emissiveIntensity: 0.3
    });
    
    // 수직 기둥
    const verticalBar = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2.8, 0.15), crossMat);
    verticalBar.position.y = 1.4;
    crossGroup.add(verticalBar);

    // 수평 기둥
    const horizontalBar = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.3, 0.15), crossMat);
    horizontalBar.position.y = 2.0;
    crossGroup.add(horizontalBar);

    crossGroup.position.set(0, 2.5, -5.85);
    scene.add(crossGroup);

    // 십자가 핫스팟 등록
    registerInteractive(crossGroup, "cross", "십자가 묵상 & 오늘의 축복기도");

    // 2. 목양실 메인 책상
    const deskGroup = new THREE.Group();
    const deskMat = new THREE.MeshStandardMaterial({ color: 0x2b1d0c, roughness: 0.5 });
    
    // 책상 상판
    const deskTop = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.15, 1.6), deskMat);
    deskTop.position.y = 1.4;
    deskTop.castShadow = true;
    deskGroup.add(deskTop);

    // 책상 다리
    const legGeo = new THREE.BoxGeometry(0.12, 1.4, 0.12);
    [ [-1.5, -0.7], [1.5, -0.7], [-1.5, 0.7], [1.5, 0.7] ].forEach(([x, z]) => {
        const leg = new THREE.Mesh(legGeo, deskMat);
        leg.position.set(x, 0.7, z);
        deskGroup.add(leg);
    });

    // 3. 책상 위 성경책 (핫스팟)
    const bibleMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.4 });
    const bible = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.7), bibleMat);
    bible.position.set(-0.8, 1.52, 0.2);
    deskGroup.add(bible);
    registerInteractive(bible, "bible", "청년 장교를 위한 성경 말씀");

    // 성경책 위 금박 십자가
    const bCrossMat = new THREE.MeshBasicMaterial({ color: 0xffd700 });
    const bCross = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.02, 0.3), bCrossMat);
    bCross.position.set(-0.8, 1.57, 0.2);
    deskGroup.add(bCross);

    // 4. 책상 위 노트북 & 램프
    const laptopMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 });
    const laptop = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.04, 0.4), laptopMat);
    laptop.position.set(0.4, 1.5, 0.1);
    deskGroup.add(laptop);

    deskGroup.position.set(0, 0, -2.5);
    scene.add(deskGroup);

    // 5. 상담 가죽 소파 (핫스팟)
    const sofaGroup = new THREE.Group();
    const sofaMat = new THREE.MeshStandardMaterial({ color: 0x5c4033, roughness: 0.7 });
    
    // 소파 바닥
    const sofaBase = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.5, 1.0), sofaMat);
    sofaBase.position.y = 0.4;
    sofaGroup.add(sofaBase);

    // 소파 등받이
    const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.9, 0.3), sofaMat);
    sofaBack.position.set(0, 0.9, -0.4);
    sofaGroup.add(sofaBack);

    sofaGroup.position.set(-3.2, 0, 1.5);
    sofaGroup.rotation.y = Math.PI / 4;
    scene.add(sofaGroup);
    registerInteractive(sofaGroup, "sofa", "1:1 목양상담 예약");

    // 6. 찬양 오디오 / 스피커 (핫스팟)
    const audioMesh = new THREE.Mesh(
        new THREE.BoxGeometry(0.6, 0.9, 0.5),
        new THREE.MeshStandardMaterial({ color: 0x1f2937, metalness: 0.3 })
    );
    audioMesh.position.set(3.8, 0.45, 1.5);
    scene.add(audioMesh);
    registerInteractive(audioMesh, "audio", "은혜로운 찬양 BGM 재생");

    // 7. 반짝이는 펄스 마커(Glow Marker) 추가
    addGlowMarker(0, 4.0, -5.7, "십자가");
    addGlowMarker(-0.8, 1.7, -2.3, "성경");
    addGlowMarker(-3.2, 1.6, 1.5, "상담소파");
    addGlowMarker(3.8, 1.2, 1.5, "찬양기");
}

function addGlowMarker(x, y, z, label) {
    const geo = new THREE.SphereGeometry(0.12, 16, 16);
    const mat = new THREE.MeshBasicMaterial({ color: 0xffd700, wireframe: true });
    const marker = new THREE.Mesh(geo, mat);
    marker.position.set(x, y, z);
    scene.add(marker);

    // 애니메이션을 위해 저장
    interactiveObjects.push({ mesh: marker, type: 'glow', baseY: y });
}

function registerInteractive(obj, type, name) {
    obj.userData = { type, name };
    interactiveObjects.push({ mesh: obj, type });
}

function onDocumentClick(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        let hit = intersects[0].object;
        while (hit && !hit.userData.type && hit.parent) {
            hit = hit.parent;
        }

        if (hit && hit.userData.type) {
            handleInteraction(hit.userData.type);
        }
    }
}

function handleInteraction(type) {
    if (type === "cross") {
        openModal("prayer-modal");
    } else if (type === "bible") {
        openModal("bible-modal");
    } else if (type === "sofa") {
        window.location.href = "/counseling";
    } else if (type === "audio") {
        toggleBgm();
    }
}

function focusCamera(view) {
    if (view === "all") {
        gsapMoveCamera(0, 4.5, 9, 0, 2, 0);
    } else if (view === "cross") {
        gsapMoveCamera(0, 3.8, 2, 0, 3.8, -5.8);
    } else if (view === "desk") {
        gsapMoveCamera(0, 2.8, 0.5, 0, 1.5, -2.5);
    } else if (view === "sofa") {
        gsapMoveCamera(-2.5, 2.5, 4, -3.2, 1.0, 1.5);
    }
}

function gsapMoveCamera(cx, cy, cz, tx, ty, tz) {
    camera.position.set(cx, cy, cz);
    controls.target.set(tx, ty, tz);
    controls.update();
}

function onWindowResize() {
    const container = document.getElementById("canvas-container");
    if (!container) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();

    // 마커 회전
    const time = Date.now() * 0.003;
    interactiveObjects.forEach(item => {
        if (item.type === 'glow') {
            item.mesh.rotation.y += 0.02;
            item.mesh.position.y = item.baseY + Math.sin(time) * 0.05;
        }
    });

    renderer.render(scene, camera);
}
