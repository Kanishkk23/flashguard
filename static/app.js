let map;
let zoneMarkers = [];
let currentRegion = "Kullu & Manali Valley (HP)";

// =========================================================
// SIREN & MOBILE NOTIFICATION ENGINE
// =========================================================
let customAudio = null;
let audioCtx = null;
let osc1 = null;
let osc2 = null;
let oscSub = null;
let masterGain = null;
let sirenInterval = null;
let isSirenPlaying = false;
let notificationPermissionAsked = false;

document.addEventListener("DOMContentLoaded", async () => {
    initializeMap();
    await loadRegionDropdown();
    await loadRegion(currentRegion);
    requestMobileNotificationPermission();
});

// Request permission for lock-screen mobile alerts
function requestMobileNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default" && !notificationPermissionAsked) {
        notificationPermissionAsked = true;
        Notification.requestPermission().then(perm => {
            console.log("Mobile Notification Permission:", perm);
        });
    }
}

function initializeMap() {
    map = L.map("map", { zoomControl: false }).setView([32.239, 77.188], 11);
    
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
        maxZoom: 19
    }).addTo(map);
    
    L.control.zoom({ position: "bottomright" }).addTo(map);
}

async function loadRegionDropdown() {
    try {
        const res = await fetch("/api/regions");
        const json = await res.json();
        if (json.success) {
            const select = document.getElementById("stateSelect");
            select.innerHTML = "";
            json.regions.forEach(region => {
                const opt = document.createElement("option");
                opt.value = region;
                opt.innerText = region;
                if (region === currentRegion) opt.selected = true;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

async function onStateChange(region) {
    currentRegion = region;
    await syncLiveAPI();
}

async function syncLiveAPI() {
    await loadRegion(currentRegion, null);
}

async function loadRegion(regionName, customParams = null) {
    try {
        let url = `/api/region/${encodeURIComponent(regionName)}`;
        if (customParams) {
            const params = new URLSearchParams(customParams).toString();
            url += `?${params}`;
        }

        const res = await fetch(url);
        const result = await res.json();
        if (!result.success) return;

        // Sync Sliders with live data
        document.getElementById("sliderRain").value = result.data.rain_1h;
        document.getElementById("valRain").innerText = result.data.rain_1h + " mm";

        document.getElementById("sliderSoil").value = result.data.soil_moisture;
        document.getElementById("valSoil").innerText = result.data.soil_moisture + " %";

        document.getElementById("sliderSlope").value = result.data.slope;
        document.getElementById("valSlope").innerText = result.data.slope + " °";

        document.getElementById("sliderRiver").value = result.data.river_level;
        document.getElementById("valRiver").innerText = result.data.river_level + " %";

        map.flyTo([result.lat, result.lng], result.zoom, { duration: 1.2 });
        renderMapMarkers(result);
        updateDashboard(result);

        document.getElementById("lastUpdated").innerText =
            `Live • ${new Date(result.timestamp).toLocaleTimeString()}`;

    } catch (e) {
        console.error(e);
    }
}

// =========================================================
// RENDER DANGER ZONES (🔴) & SAFE HAVENS (🟢) ON MAP
// =========================================================
function renderMapMarkers(result) {
    zoneMarkers.forEach(m => map.removeLayer(m));
    zoneMarkers = [];

    const riskColor = result.prediction.color;
    const score = result.prediction.risk_score;

    // 1. Regional Catchment Perimeter
    const circle = L.circle([result.lat, result.lng], {
        radius: 4500 + score * 40,
        color: riskColor,
        fillColor: riskColor,
        fillOpacity: 0.14,
        weight: 2.5
    }).addTo(map);
    zoneMarkers.push(circle);

    // 2. High Alert Danger Zones (🔴)
    if (result.danger_zones && result.danger_zones.length > 0) {
        result.danger_zones.forEach(zone => {
            const dangerMarker = L.circleMarker([zone.lat, zone.lng], {
                radius: 12,
                color: "#ffffff",
                weight: 2.5,
                fillColor: "#e11d48",
                fillOpacity: 0.95
            }).addTo(map);

            dangerMarker.bindPopup(`
                <div class="popup-title" style="color:#e11d48">🔴 HIGH ALERT DANGER: ${zone.name}</div>
                <div style="font-size:11px; margin-top:4px; color:#a69e92;"><b>Hazard:</b> ${zone.desc}</div>
                <div style="font-size:10px; margin-top:6px; color:#f87171; font-weight:700;">⚠️ AVOID LOW-LYING GORGE</div>
            `);
            zoneMarkers.push(dangerMarker);
        });
    }

    // 3. Safety Zones / Evacuation Centers (🟢)
    const safetyList = result.safety_zones || result.safe_havens || [];
    if (safetyList.length > 0) {
        safetyList.forEach(haven => {
            const safeMarker = L.circleMarker([haven.lat, haven.lng], {
                radius: 12,
                color: "#ffffff",
                weight: 2.5,
                fillColor: "#10b981",
                fillOpacity: 0.95
            }).addTo(map);

            safeMarker.bindPopup(`
                <div class="popup-title" style="color:#10b981">🟢 SAFETY ZONE: ${haven.name}</div>
                <div style="font-size:11px; margin-top:4px; color:#a69e92;"><b>Safety Details:</b> ${haven.desc}</div>
                <div style="font-size:10px; margin-top:6px; color:#34d399; font-weight:700;">🛡️ DESIGNATED HIGH-GROUND SAFETY ZONE</div>
            `);
            zoneMarkers.push(safeMarker);
        });
    }
}

function updateDashboard(result) {
    const data = result.data;
    const prediction = result.prediction;
    const regionName = result.region;

    setText("predictionStateTitle", `${regionName} • Threat Level`);
    setText("mapStateTitle", `${regionName} • Watershed & Safety Map`);
    setText("stateHistory", result.history);

    // Top 4 Metrics
    setText("rain1h", data.rain_1h.toFixed(1));
    setText("soil", data.soil_moisture.toFixed(0));
    setText("slope", data.slope.toFixed(1));
    setText("river", data.river_level.toFixed(0));

    setWidth("soilBar", data.soil_moisture);
    setWidth("riverBar", data.river_level);

    // Telemetry Cards
    setText("sourceRain", data.rain_1h.toFixed(1) + " mm");
    setText("sourceElevation", data.elevation.toFixed(0) + " m");
    setText("sourceSoil", data.soil_moisture.toFixed(0) + " %");
    setText("sourceSatellite", data.satellite_anomaly.toFixed(0) + " %");
    setText("sourceRiver", data.river_level.toFixed(0) + " %");
    setText("sourceTemp", data.temperature.toFixed(1) + " °C");

    // Gauge & Score
    const score = prediction.risk_score;
    setText("riskScore", score);
    setText("riskText", prediction.risk + " THREAT");
    updateRiskBadge(prediction.risk);
    updateGauge(score, prediction.color);

    let desc = "";
    if (prediction.risk === "LOW") {
        desc = `Normal atmospheric baseline in ${regionName}. Mountain catchments show normal absorption capacity.`;
    } else if (prediction.risk === "MODERATE") {
        desc = `Elevated soil saturation detected in ${regionName}. Low-lying riverbeds require active monitoring.`;
    } else if (prediction.risk === "HIGH") {
        desc = `High storm intensity on steep slopes in ${regionName}! Evacuate low gorges to designated Safety Zones.`;
    } else {
        desc = `🚨 CRITICAL CLOUDBURST SURGE ALARM in ${regionName}! Evacuate immediately to designated Safety Zones!`;
    }
    setText("riskDescription", desc);

    // Factor bars
    const rainFactor = Math.min(100, (data.rain_1h / 100) * 100);
    setText("rainFactor", Math.round(rainFactor) + "%");
    setWidth("rainFactorBar", rainFactor);

    setText("soilFactor", Math.round(data.soil_moisture) + "%");
    setWidth("soilFactorBar", data.soil_moisture);

    setText("riverFactor", Math.round(data.river_level) + "%");
    setWidth("riverFactorBar", data.river_level);

    // Probabilities
    const probs = prediction.class_probabilities;
    updateDistribution("lowProbability", "lowBar", probs.LOW);
    updateDistribution("moderateProbability", "moderateBar", probs.MODERATE);
    updateDistribution("highProbability", "highBar", probs.HIGH);
    updateDistribution("extremeProbability", "extremeBar", probs.EXTREME);

    // Auto Siren & Mobile Lockscreen Alert on EXTREME
    if (prediction.risk === "EXTREME") {
        showAlert(prediction.risk, score, regionName);
        startSirenSound();
        triggerMobileLockscreenAlert(regionName, score);
    } else if (prediction.risk === "HIGH") {
        showAlert(prediction.risk, score, regionName);
        stopSirenSound();
    } else {
        dismissAlert();
        stopSirenSound();
    }
}

// =========================================================
// MOBILE LOCKSCREEN ALERT & HARDWARE VIBRATION
// =========================================================
function triggerMobileLockscreenAlert(regionName, score) {
    // 1. Mobile Hardware Haptic Vibration
    if ("vibrate" in navigator) {
        navigator.vibrate([500, 200, 500, 200, 500]);
    }

    // 2. Lockscreen Push Notification
    if ("Notification" in window && Notification.permission === "granted") {
        try {
            new Notification("🚨 FLASH FLOOD EMERGENCY: " + regionName.toUpperCase(), {
                body: `Threat Score: ${score}/100. Critical mountain surge detected! Evacuate low riverbeds and proceed to Safety Zones immediately!`,
                icon: "/static/theme_previews/theme_monsoon_dusk_1787751265804.jpg",
                vibrate: [500, 200, 500],
                requireInteraction: true
            });
        } catch (e) {
            console.warn("Mobile notification dispatch:", e);
        }
    }
}

function updateGauge(score, color) {
    const gauge = document.querySelector(".gauge-ring");
    const angle = score * 3.6;
    gauge.style.background = `
        radial-gradient(circle, #221f1b 58%, transparent 59%),
        conic-gradient(${color} ${angle}deg, rgba(212, 185, 150, 0.12) ${angle}deg)
    `;
}

function updateRiskBadge(risk) {
    const badge = document.getElementById("riskBadge");
    badge.innerText = risk;
    const colors = { LOW: "#7ea193", MODERATE: "#e59840", HIGH: "#c25e40", EXTREME: "#e06846" };
    badge.style.color = colors[risk] || "#d4b996";
    badge.style.background = (colors[risk] || "#d4b996") + "22";
    badge.style.border = `1px solid ${colors[risk]}40`;
}

// =========================================================
// START / STOP SIREN
// =========================================================
function startSirenSound() {
    if (isSirenPlaying) return;

    if (!customAudio) {
        customAudio = new Audio("/static/siren.mp3");
        customAudio.loop = true;
    }

    customAudio.play().then(() => {
        isSirenPlaying = true;
        updateSirenBtn(true);
    }).catch(() => {
        playSynthesizedWarSiren();
    });
}

function playSynthesizedWarSiren() {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
        if (audioCtx.state === 'suspended') audioCtx.resume();

        osc1 = audioCtx.createOscillator();
        osc2 = audioCtx.createOscillator();
        oscSub = audioCtx.createOscillator();

        osc1.type = "sawtooth";
        osc2.type = "triangle";
        oscSub.type = "sine";

        const filter = audioCtx.createBiquadFilter();
        filter.type = "lowpass";
        filter.frequency.setValueAtTime(1200, audioCtx.currentTime);

        masterGain = audioCtx.createGain();
        masterGain.gain.setValueAtTime(0.28, audioCtx.currentTime);

        osc1.connect(filter);
        osc2.connect(filter);
        oscSub.connect(filter);
        filter.connect(masterGain);
        masterGain.connect(audioCtx.destination);

        osc1.frequency.setValueAtTime(320, audioCtx.currentTime);
        osc2.frequency.setValueAtTime(640, audioCtx.currentTime);
        oscSub.frequency.setValueAtTime(90, audioCtx.currentTime);

        osc1.start();
        osc2.start();
        oscSub.start();

        let rising = true;
        sirenInterval = setInterval(() => {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const duration = 1.4;

            if (rising) {
                osc1.frequency.exponentialRampToValueAtTime(820, now + duration);
                osc2.frequency.exponentialRampToValueAtTime(1640, now + duration);
                oscSub.frequency.exponentialRampToValueAtTime(140, now + duration);
            } else {
                osc1.frequency.exponentialRampToValueAtTime(320, now + duration);
                osc2.frequency.exponentialRampToValueAtTime(640, now + duration);
                oscSub.frequency.exponentialRampToValueAtTime(90, now + duration);
            }
            rising = !rising;
        }, 1450);

        isSirenPlaying = true;
        updateSirenBtn(true);
    } catch (e) {
        console.warn(e);
    }
}

function stopSirenSound() {
    if (!isSirenPlaying) return;

    if (customAudio) {
        customAudio.pause();
        customAudio.currentTime = 0;
    }

    if (sirenInterval) clearInterval(sirenInterval);
    if (masterGain && audioCtx) {
        masterGain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
    }

    setTimeout(() => {
        if (osc1) { try { osc1.stop(); osc1.disconnect(); } catch (e) {} }
        if (osc2) { try { osc2.stop(); osc2.disconnect(); } catch (e) {} }
        if (oscSub) { try { oscSub.stop(); oscSub.disconnect(); } catch (e) {} }
        if (audioCtx) { try { audioCtx.close(); } catch (e) {} }
        isSirenPlaying = false;
        audioCtx = null;
        osc1 = null;
        osc2 = null;
        oscSub = null;
        updateSirenBtn(false);
    }, 200);
}

function toggleSiren() {
    if (isSirenPlaying) stopSirenSound();
    else startSirenSound();
}

function updateSirenBtn(playing) {
    const btn = document.getElementById("sirenBtn");
    if (btn) {
        if (playing) {
            btn.innerHTML = "🚨 Silence Siren";
            btn.classList.add("siren-active");
        } else {
            btn.innerHTML = "🔊 Test Siren";
            btn.classList.remove("siren-active");
        }
    }
}

// 4 Slider Controls
function onSliderChange(field, val, unit) {
    document.getElementById(`val${field}`).innerText = val + unit;
}

async function triggerManualPrediction() {
    const params = {
        rain_1h: document.getElementById("sliderRain").value,
        soil_moisture: document.getElementById("sliderSoil").value,
        slope: document.getElementById("sliderSlope").value,
        river_level: document.getElementById("sliderRiver").value
    };
    await loadRegion(currentRegion, params);
}

async function simulateExtremeCloudburst() {
    const extremeParams = {
        rain_1h: 125,
        soil_moisture: 95,
        slope: 44,
        river_level: 94
    };
    await loadRegion(currentRegion, extremeParams);
}

function showAlert(risk, score, regionName) {
    const banner = document.getElementById("alertBanner");
    banner.classList.remove("hidden");
    setText("alertTitle", risk === "EXTREME"
        ? `🚨 SURGICAL FLASH FLOOD ALARM • ${regionName.toUpperCase()}`
        : `⚠ HIGH THREAT WARNING • ${regionName.toUpperCase()}`
    );
    setText("alertMessage", `ML Threat Score: ${score}/100. Critical runoff calculated. Evacuate to Safety Zones immediately!`);
}

function dismissAlert() {
    document.getElementById("alertBanner").classList.add("hidden");
    stopSirenSound();
}

function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.innerText = val;
}

function setWidth(id, val) {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.max(0, Math.min(100, val)) + "%";
}

function updateDistribution(textId, barId, val) {
    setText(textId, val.toFixed(1) + "%");
    setWidth(barId, val);
}

document.addEventListener("click", () => {
    requestMobileNotificationPermission();
}, { once: true });