/**
 * EcoSoil AI — Main Application
 * Handles form submission, API calls, results rendering, particle effects, and UI logic.
 */

(function () {
    'use strict';

    // ─── DOM References ─────────────────────────────────────
    const soilForm = document.getElementById('soilForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const randomBtn = document.getElementById('randomBtn');
    const resetBtn = document.getElementById('resetBtn');
    const startBtn = document.getElementById('startAnalysisBtn');

    // Section elements
    const sections = {
        analysis: document.getElementById('analysis'),
        dashboard: document.getElementById('dashboard'),
        sustainability: document.getElementById('sustainability'),
        trends: document.getElementById('trends'),
    };

    // Nav links
    const navLinks = document.querySelectorAll('.nav-link');

    // Store latest result
    let latestResult = null;
    let trendData = null;

    // ─── Initialization ─────────────────────────────────────
    function init() {
        setupNavigation();
        setupForm();
        setupInputBars();
        setupParticles();
        setupScrollEffects();
        loadTrendData();
    }

    // ─── Navigation ─────────────────────────────────────────
    function setupNavigation() {
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const sectionId = link.dataset.section;
                showSection(sectionId);
                setActiveNav(link);
            });
        });

        if (startBtn) {
            startBtn.addEventListener('click', (e) => {
                e.preventDefault();
                showSection('analysis');
                setActiveNav(document.querySelector('[data-section="analysis"]'));
                document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
            });
        }
    }

    function showSection(id) {
        Object.entries(sections).forEach(([key, el]) => {
            if (el) {
                if (key === id) {
                    el.classList.remove('hidden');
                    el.querySelectorAll('.glass-card, .crop-card, .rec-card').forEach(
                        (card, i) => {
                            card.style.animation = 'none';
                            card.offsetHeight; // reflow
                            card.style.animation = `slideIn 0.5s cubic-bezier(0.4,0,0.2,1) ${i * 0.06}s both`;
                        }
                    );
                } else {
                    el.classList.add('hidden');
                }
            }
        });
        // Always show analysis
        if (id !== 'analysis') {
            sections.analysis?.classList.add('hidden');
        }
    }

    function setActiveNav(activeLink) {
        navLinks.forEach(l => l.classList.remove('active'));
        activeLink?.classList.add('active');
    }

    // ─── Form ───────────────────────────────────────────────
    function setupForm() {
        soilForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runAnalysis();
        });

        randomBtn.addEventListener('click', fillRandomSample);
    }

    async function runAnalysis() {
        const formData = new FormData(soilForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = isNaN(parseFloat(value)) ? value : parseFloat(value);
        });

        // Show loading
        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (!response.ok) throw new Error('Analysis failed');

            latestResult = await response.json();
            renderResults(latestResult);

            // Switch to dashboard
            showSection('dashboard');
            setActiveNav(document.querySelector('[data-section="dashboard"]'));
            window.scrollTo({ top: sections.dashboard.offsetTop - 80, behavior: 'smooth' });

        } catch (error) {
            console.error('Analysis error:', error);
            alert('Analysis failed. Please check the server is running.');
        } finally {
            analyzeBtn.classList.remove('loading');
            analyzeBtn.disabled = false;
        }
    }

    function fillRandomSample() {
        const soilTypes = ['Alluvial', 'Black Cotton', 'Red', 'Laterite', 'Desert',
            'Mountain', 'Peaty', 'Saline', 'Loamy', 'Clay', 'Sandy', 'Silt', 'Chalky', 'Podzol'];

        const rand = (min, max) => (Math.random() * (max - min) + min).toFixed(1);

        document.getElementById('nitrogen').value = rand(10, 180);
        document.getElementById('phosphorus').value = rand(5, 130);
        document.getElementById('potassium').value = rand(5, 180);
        document.getElementById('ph').value = rand(3.5, 9.5);
        document.getElementById('temperature').value = rand(8, 42);
        document.getElementById('humidity').value = rand(15, 95);
        document.getElementById('rainfall').value = Math.round(Math.random() * 350 + 15);
        document.getElementById('organic_carbon').value = rand(0.1, 4.5);
        document.getElementById('moisture').value = rand(5, 75);
        document.getElementById('ec').value = rand(0.1, 3.5);
        document.getElementById('soil_type').value = soilTypes[Math.floor(Math.random() * soilTypes.length)];

        updateAllInputBars();
    }

    // ─── Input Bars ─────────────────────────────────────────
    function setupInputBars() {
        document.querySelectorAll('.input-wrapper input[type="number"]').forEach(input => {
            input.addEventListener('input', () => updateInputBar(input));
            updateInputBar(input);
        });
    }

    function updateInputBar(input) {
        const bar = input.parentElement.querySelector('.input-bar');
        if (!bar) return;
        const max = parseFloat(bar.dataset.max) || 100;
        const val = parseFloat(input.value) || 0;
        const pct = Math.min((val / max) * 100, 100);
        bar.style.width = pct + '%';
    }

    function updateAllInputBars() {
        document.querySelectorAll('.input-wrapper input[type="number"]').forEach(updateInputBar);
    }

    // ─── Render Results ─────────────────────────────────────
    function renderResults(result) {
        renderHealthGauge(result.health);
        renderNutrients(result.nutrients);
        renderCropCards(result.crop_recommendations);
        renderSustainability(result.sustainability);
        SoilCharts.renderNutrientRadar('nutrientRadar', result.nutrients);
    }

    // Health Gauge (canvas arc)
    function renderHealthGauge(health) {
        const canvas = document.getElementById('healthGauge');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('gaugeScore');
        const gradeEl = document.getElementById('gaugeGrade');
        const descEl = document.getElementById('healthDesc');

        const size = 240;
        const dpr = window.devicePixelRatio || 1;
        canvas.width = size * dpr;
        canvas.height = size * dpr;
        ctx.scale(dpr, dpr);

        const cx = size / 2;
        const cy = size / 2;
        const radius = 95;
        const lineWidth = 12;
        const startAngle = 0.75 * Math.PI;
        const endAngle = 2.25 * Math.PI;
        const totalArc = endAngle - startAngle;

        // Animate
        let currentScore = 0;
        const targetScore = health.score;
        const duration = 1500;
        const startTime = performance.now();

        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            currentScore = eased * targetScore;

            ctx.clearRect(0, 0, size, size);

            // Background arc
            ctx.beginPath();
            ctx.arc(cx, cy, radius, startAngle, endAngle);
            ctx.strokeStyle = 'rgba(255,255,255,0.06)';
            ctx.lineWidth = lineWidth;
            ctx.lineCap = 'round';
            ctx.stroke();

            // Value arc
            const valueAngle = startAngle + (currentScore / 100) * totalArc;
            const gradient = ctx.createLinearGradient(0, 0, size, size);
            gradient.addColorStop(0, '#00e676');
            gradient.addColorStop(0.5, '#00bfa5');
            gradient.addColorStop(1, '#1de9b6');

            ctx.beginPath();
            ctx.arc(cx, cy, radius, startAngle, valueAngle);
            ctx.strokeStyle = gradient;
            ctx.lineWidth = lineWidth;
            ctx.lineCap = 'round';
            ctx.stroke();

            // Glow effect
            ctx.beginPath();
            ctx.arc(cx, cy, radius, startAngle, valueAngle);
            ctx.strokeStyle = 'rgba(0, 230, 118, 0.15)';
            ctx.lineWidth = lineWidth + 8;
            ctx.lineCap = 'round';
            ctx.stroke();

            // Tick marks
            for (let i = 0; i <= 10; i++) {
                const angle = startAngle + (i / 10) * totalArc;
                const innerR = radius - lineWidth / 2 - 6;
                const outerR = radius - lineWidth / 2 - (i % 5 === 0 ? 14 : 10);
                ctx.beginPath();
                ctx.moveTo(cx + innerR * Math.cos(angle), cy + innerR * Math.sin(angle));
                ctx.lineTo(cx + outerR * Math.cos(angle), cy + outerR * Math.sin(angle));
                ctx.strokeStyle = 'rgba(255,255,255,0.15)';
                ctx.lineWidth = i % 5 === 0 ? 1.5 : 0.8;
                ctx.stroke();
            }

            scoreEl.textContent = Math.round(currentScore);
            scoreEl.style.color = health.color;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }

        requestAnimationFrame(animate);
        gradeEl.textContent = health.grade;
        descEl.textContent = health.description;
    }

    // Nutrient Status List
    function renderNutrients(nutrients) {
        const container = document.getElementById('nutrientList');
        container.innerHTML = nutrients.map(n => {
            const severityClass = n.deficient
                ? (n.severity === 'critical' ? 'deficient' : n.severity === 'high' ? 'deficient' : 'moderate')
                : 'adequate';
            return `
                <div class="nutrient-item animate-in">
                    <div class="nutrient-info">
                        <span class="nutrient-name">${n.nutrient}</span>
                        <span class="nutrient-value">${n.value} ${n.key === 'pH' ? '' : n.key === 'OC' ? '%' : 'kg/ha'}</span>
                    </div>
                    <span class="nutrient-badge ${severityClass}">
                        ${n.status} (${n.confidence}%)
                    </span>
                </div>
            `;
        }).join('');
    }

    // Crop Recommendation Cards
    function renderCropCards(crops) {
        const grid = document.getElementById('cropGrid');
        grid.innerHTML = crops.map((crop, i) => `
            <div class="crop-card animate-in">
                <span class="crop-rank">#${i + 1}</span>
                <div class="crop-name">${crop.crop}</div>
                <div class="crop-confidence">Confidence: ${crop.confidence}%</div>
                <div class="crop-details">
                    <div class="crop-detail">
                        <span class="crop-detail-label">Season</span>
                        <span class="crop-detail-value">${crop.season}</span>
                    </div>
                    <div class="crop-detail">
                        <span class="crop-detail-label">Water Req.</span>
                        <span class="crop-detail-value">${crop.water_requirement}</span>
                    </div>
                    <div class="crop-detail">
                        <span class="crop-detail-label">Growth Period</span>
                        <span class="crop-detail-value">${crop.growth_period}</span>
                    </div>
                </div>
                <div class="suitability-bar-container">
                    <div class="suitability-label">Suitability: ${crop.suitability}%</div>
                    <div class="suitability-bar">
                        <div class="suitability-fill" style="width: ${crop.suitability}%"></div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Sustainability
    function renderSustainability(sustainability) {
        // Score ring animation
        const circle = document.getElementById('scoreCircle');
        const scoreEl = document.getElementById('sustainScore');
        const gradeEl = document.getElementById('sustainGrade');

        const circumference = 2 * Math.PI * 85;
        const percent = sustainability.composite_score / 100;
        const offset = circumference * (1 - percent);

        scoreEl.textContent = sustainability.composite_score;
        gradeEl.textContent = sustainability.grade;

        // Animate stroke
        circle.style.transition = 'none';
        circle.style.strokeDashoffset = circumference;
        requestAnimationFrame(() => {
            circle.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
            circle.style.strokeDashoffset = offset;
        });

        // Breakdown chart
        SoilCharts.renderSustainabilityChart('sustainChart', sustainability.breakdown);

        // Impact metrics
        const impact = sustainability.environmental_impact;
        const impactEl = document.getElementById('impactMetrics');
        impactEl.innerHTML = `
            <div class="impact-item">
                <div class="impact-value" style="color: #00e676">${impact.carbon_footprint_reduction}%</div>
                <div class="impact-label">Carbon Reduction</div>
            </div>
            <div class="impact-item">
                <div class="impact-value" style="color: #40c4ff">${impact.water_conservation}%</div>
                <div class="impact-label">Water Conservation</div>
            </div>
            <div class="impact-item">
                <div class="impact-value" style="color: #b388ff">${impact.biodiversity_index}</div>
                <div class="impact-label">Biodiversity Index</div>
            </div>
            <div class="impact-item">
                <div class="impact-value" style="color: ${impact.erosion_risk === 'Low' ? '#00e676' : impact.erosion_risk === 'Medium' ? '#ffd600' : '#ff1744'}">${impact.erosion_risk}</div>
                <div class="impact-label">Erosion Risk</div>
            </div>
        `;

        // Recommendations
        const recsEl = document.getElementById('recsList');
        recsEl.innerHTML = sustainability.recommendations.map(rec => `
            <div class="rec-card priority-${rec.priority.toLowerCase()} animate-in">
                <div class="rec-priority">${rec.priority} Priority</div>
                <div class="rec-action">${rec.action}</div>
                <div class="rec-impact">💡 ${rec.impact}</div>
            </div>
        `).join('');
    }

    // ─── Trend Data ─────────────────────────────────────────
    async function loadTrendData() {
        try {
            const res = await fetch('/api/sustainability-trends');
            const json = await res.json();
            trendData = json.trends;
        } catch (e) {
            console.warn('Could not load trend data:', e);
        }
    }

    // When trends section is shown, render charts
    const origShowSection = showSection;
    showSection = function (id) {
        origShowSection(id);
        if (id === 'trends' && trendData) {
            SoilCharts.renderTrendChart('trendChart', trendData);
            SoilCharts.renderQualityChart('qualityChart', trendData);
            SoilCharts.renderEnvChart('envChart', trendData);
        }
        if (id === 'sustainability' && latestResult) {
            setTimeout(() => {
                renderSustainability(latestResult.sustainability);
            }, 100);
        }
    };

    // ─── Particle Background ────────────────────────────────
    function setupParticles() {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let particles = [];
        let w, h;

        function resize() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }

        function createParticles() {
            particles = [];
            const count = Math.floor((w * h) / 18000);
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    r: Math.random() * 1.5 + 0.5,
                    vx: (Math.random() - 0.5) * 0.3,
                    vy: (Math.random() - 0.5) * 0.3,
                    alpha: Math.random() * 0.4 + 0.1,
                });
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, w, h);
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0) p.x = w;
                if (p.x > w) p.x = 0;
                if (p.y < 0) p.y = h;
                if (p.y > h) p.y = 0;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(0, 230, 118, ${p.alpha})`;
                ctx.fill();
            });

            // Draw connections
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(0, 230, 118, ${0.06 * (1 - dist / 120)})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }

            requestAnimationFrame(drawParticles);
        }

        window.addEventListener('resize', () => { resize(); createParticles(); });
        resize();
        createParticles();
        drawParticles();
    }

    // ─── Scroll Effects ─────────────────────────────────────
    function setupScrollEffects() {
        const navbar = document.getElementById('navbar');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ─── Start ──────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', init);
})();
