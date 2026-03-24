/**
 * EcoSoil AI — Charts Module
 * Chart.js configuration and rendering for soil analysis visualizations.
 */

const ChartColors = {
    green: { bg: 'rgba(0, 230, 118, 0.15)', border: '#00e676' },
    teal: { bg: 'rgba(0, 191, 165, 0.15)', border: '#00bfa5' },
    cyan: { bg: 'rgba(29, 233, 182, 0.15)', border: '#1de9b6' },
    blue: { bg: 'rgba(64, 196, 255, 0.15)', border: '#40c4ff' },
    purple: { bg: 'rgba(179, 136, 255, 0.15)', border: '#b388ff' },
    orange: { bg: 'rgba(255, 145, 0, 0.15)', border: '#ff9100' },
    red: { bg: 'rgba(255, 23, 68, 0.15)', border: '#ff1744' },
    yellow: { bg: 'rgba(255, 214, 0, 0.15)', border: '#ffd600' },
};

const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#8892a4',
                font: { family: "'Inter', sans-serif", size: 11, weight: 500 },
                padding: 16,
                usePointStyle: true,
                pointStyleWidth: 8,
            },
        },
        tooltip: {
            backgroundColor: 'rgba(15, 21, 35, 0.95)',
            titleColor: '#e8ecf4',
            bodyColor: '#8892a4',
            borderColor: 'rgba(255,255,255,0.08)',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12,
            titleFont: { family: "'Inter', sans-serif", weight: 600 },
            bodyFont: { family: "'JetBrains Mono', monospace", size: 12 },
            displayColors: true,
            boxPadding: 4,
        },
    },
    scales: {},
};

// Shared scale styles for axis charts
const axisScaleStyle = {
    grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
    ticks: { color: '#5a6478', font: { family: "'Inter', sans-serif", size: 11 } },
};

window.SoilCharts = {
    charts: {},

    /**
     * Nutrient Radar Chart
     */
    renderNutrientRadar(canvasId, nutrients) {
        this._destroy(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = nutrients.map(n => n.nutrient);
        const values = nutrients.map(n => n.value);
        const maxValues = [200, 150, 200, 10, 5];
        const normalized = values.map((v, i) => (v / maxValues[i]) * 100);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels,
                datasets: [{
                    label: 'Current Levels',
                    data: normalized,
                    backgroundColor: ChartColors.green.bg,
                    borderColor: ChartColors.green.border,
                    borderWidth: 2,
                    pointBackgroundColor: ChartColors.green.border,
                    pointBorderColor: '#0a0e17',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                }, {
                    label: 'Optimal Range',
                    data: [60, 53, 52, 65, 35],
                    backgroundColor: ChartColors.teal.bg,
                    borderColor: ChartColors.teal.border,
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    pointRadius: 0,
                }],
            },
            options: {
                ...chartDefaults,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            display: false,
                        },
                        grid: { color: 'rgba(255,255,255,0.06)' },
                        angleLines: { color: 'rgba(255,255,255,0.06)' },
                        pointLabels: {
                            color: '#8892a4',
                            font: { family: "'Inter', sans-serif", size: 11, weight: 500 },
                        },
                    },
                },
                plugins: {
                    ...chartDefaults.plugins,
                    datalabels: { display: false },
                },
            },
        });
    },

    /**
     * Sustainability Breakdown Doughnut
     */
    renderSustainabilityChart(canvasId, breakdown) {
        this._destroy(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = [
            'Soil Quality', 'Biodiversity', 'Water Retention',
            'Carbon Seq.', 'Nutrient Eff.',
        ];
        const data = [
            breakdown.soil_quality,
            breakdown.biodiversity_potential,
            breakdown.water_retention,
            breakdown.carbon_sequestration,
            breakdown.nutrient_efficiency,
        ];
        const colors = [
            ChartColors.green.border, ChartColors.teal.border,
            ChartColors.blue.border, ChartColors.purple.border,
            ChartColors.cyan.border,
        ];
        const bgColors = [
            ChartColors.green.bg, ChartColors.teal.bg,
            ChartColors.blue.bg, ChartColors.purple.bg,
            ChartColors.cyan.bg,
        ];

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: bgColors,
                    borderColor: colors,
                    borderWidth: 2,
                    hoverBorderWidth: 3,
                    hoverOffset: 8,
                }],
            },
            options: {
                ...chartDefaults,
                cutout: '60%',
                plugins: {
                    ...chartDefaults.plugins,
                    legend: {
                        ...chartDefaults.plugins.legend,
                        position: 'bottom',
                    },
                    datalabels: { display: false },
                },
            },
        });
    },

    /**
     * Sustainability Trend Line Chart
     */
    renderTrendChart(canvasId, trends) {
        this._destroy(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = trends.map(t => t.month);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Sustainability',
                        data: trends.map(t => t.sustainability_score),
                        borderColor: ChartColors.green.border,
                        backgroundColor: ChartColors.green.bg,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: ChartColors.green.border,
                        pointBorderColor: '#0a0e17',
                        pointBorderWidth: 2,
                    },
                    {
                        label: 'Soil Health',
                        data: trends.map(t => t.soil_health),
                        borderColor: ChartColors.teal.border,
                        backgroundColor: 'transparent',
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: ChartColors.teal.border,
                        borderDash: [5, 3],
                    },
                    {
                        label: 'Biodiversity',
                        data: trends.map(t => t.biodiversity),
                        borderColor: ChartColors.purple.border,
                        backgroundColor: 'transparent',
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: ChartColors.purple.border,
                        borderDash: [3, 3],
                    },
                ],
            },
            options: {
                ...chartDefaults,
                scales: {
                    x: { ...axisScaleStyle },
                    y: {
                        ...axisScaleStyle,
                        beginAtZero: true,
                        max: 100,
                        ticks: { ...axisScaleStyle.ticks, callback: v => v + '%' },
                    },
                },
                plugins: {
                    ...chartDefaults.plugins,
                    datalabels: { display: false },
                },
                interaction: { mode: 'index', intersect: false },
            },
        });
    },

    /**
     * Soil Quality Distribution Bar Chart
     */
    renderQualityChart(canvasId, trends) {
        this._destroy(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = trends.map(t => t.month);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Water Retention',
                    data: trends.map(t => t.water_retention),
                    backgroundColor: ChartColors.blue.border + '30',
                    borderColor: ChartColors.blue.border,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                }, {
                    label: 'Carbon Seq.',
                    data: trends.map(t => t.carbon_seq),
                    backgroundColor: ChartColors.purple.border + '30',
                    borderColor: ChartColors.purple.border,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                }],
            },
            options: {
                ...chartDefaults,
                scales: {
                    x: { ...axisScaleStyle },
                    y: {
                        ...axisScaleStyle,
                        beginAtZero: true,
                        max: 100,
                    },
                },
                plugins: {
                    ...chartDefaults.plugins,
                    datalabels: { display: false },
                },
            },
        });
    },

    /**
     * Environmental Metrics Polar Area Chart
     */
    renderEnvChart(canvasId, trends) {
        this._destroy(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Aggregate latest values
        const latest = trends[trends.length - 1] || {};

        this.charts[canvasId] = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: ['Sustainability', 'Soil Health', 'Biodiversity', 'Water Retention', 'Carbon Seq.'],
                datasets: [{
                    data: [
                        latest.sustainability_score || 0,
                        latest.soil_health || 0,
                        latest.biodiversity || 0,
                        latest.water_retention || 0,
                        latest.carbon_seq || 0,
                    ],
                    backgroundColor: [
                        ChartColors.green.border + '40',
                        ChartColors.teal.border + '40',
                        ChartColors.purple.border + '40',
                        ChartColors.blue.border + '40',
                        ChartColors.cyan.border + '40',
                    ],
                    borderColor: [
                        ChartColors.green.border,
                        ChartColors.teal.border,
                        ChartColors.purple.border,
                        ChartColors.blue.border,
                        ChartColors.cyan.border,
                    ],
                    borderWidth: 2,
                }],
            },
            options: {
                ...chartDefaults,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { display: false },
                        grid: { color: 'rgba(255,255,255,0.06)' },
                    },
                },
                plugins: {
                    ...chartDefaults.plugins,
                    legend: {
                        ...chartDefaults.plugins.legend,
                        position: 'bottom',
                    },
                    datalabels: { display: false },
                },
            },
        });
    },

    _destroy(id) {
        if (this.charts[id]) {
            this.charts[id].destroy();
            delete this.charts[id];
        }
    },
};
