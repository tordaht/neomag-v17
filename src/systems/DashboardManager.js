// Plotly global olarak yükleniyor
import EventBus from '../core/EventBus.js';

export default class DashboardManager {
    constructor() {
        this.history = {
            generation: [],
            avgEnergy: [],
            alive: [],
        };

        this.charts = {
            population: {
                element: 'population-chart',
                data: [{ x: [], y: [], type: 'scatter', mode: 'lines', name: 'Popülasyon', line: { color: '#3CE7CB', width: 2 } }],
                layout: this.getChartLayout('Zaman', 'Popülasyon')
            },
            fitness: {
                element: 'fitness-chart',
                data: [{ x: [], y: [], type: 'scatter', mode: 'lines', name: 'Ort. Fitness', line: { color: '#FFB86C', width: 2 } }],
                layout: this.getChartLayout('Zaman', 'Fitness')
            },
            diversity: {
                element: 'diversity-chart',
                data: [{ x: [], y: [], type: 'scatter', mode: 'lines', name: 'Çeşitlilik', line: { color: '#F95A77', width: 2 } }],
                layout: this.getChartLayout('Zaman', 'Genetik Çeşitlilik')
            }
        };

        this.initializeCharts();
        this.setupPerformancePanel();
        this.subscribeToEvents();
        
        // Sunucudan performans metriklerini çek
        this.fetchServerMetrics();
        setInterval(() => this.fetchServerMetrics(), 5000); // 5 saniyede bir
    }

    getChartLayout(xTitle, yTitle) {
        return {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { l: 40, r: 20, b: 40, t: 20 },
            xaxis: { 
                title: xTitle,
                color: '#A0A0A0',
                gridcolor: 'rgba(255, 255, 255, 0.1)'
            },
            yaxis: { 
                title: yTitle,
                color: '#A0A0A0',
                gridcolor: 'rgba(255, 255, 255, 0.1)'
            },
            font: {
                family: 'Inter, sans-serif',
                size: 12,
                color: '#E0E0E0'
            },
            showlegend: false
        };
    }

    initializeCharts() {
        for (const chartName in this.charts) {
            const chart = this.charts[chartName];
            const element = document.getElementById(chart.element);
            if (!element) {
                console.error(`Chart container '${chart.element}' not found.`);
                continue;
            }
            Plotly.newPlot(element, chart.data, chart.layout, {responsive: true, displaylogo: false});
        }
    }

    subscribeToEvents() {
        EventBus.on('world_update', (data) => {
            this.update(data);
        });
    }

    update(data) {
        // AppController'dan gelen tam veri paketini işle
        const payload = data.payload;
        if (!payload) return;

        const tick = payload.ticks;

        // Her bir grafik için veriyi güncelle
        Plotly.extendTraces(this.charts.population.element, { x: [[tick]], y: [[payload.population]] }, [0]);
        Plotly.extendTraces(this.charts.fitness.element, { x: [[tick]], y: [[payload.avg_fitness]] }, [0]);
        Plotly.extendTraces(this.charts.diversity.element, { x: [[tick]], y: [[payload.genetic_diversity]] }, [0]);
    }

    reset() {
        this.history = { generation: [], avgEnergy: [], alive: [] };
        // Re-initialize chart to clear it
        this.initializeChart();
    }

    setupPerformancePanel() {
        // Performans panel HTML'ini dinamik olarak ekle
        const performancePanel = document.createElement('div');
        performancePanel.className = 'performance-panel';
        performancePanel.innerHTML = `
            <h3>🚀 Performans Metrikleri</h3>
            <div class="performance-grid">
                <div class="perf-item">
                    <label>FPS (İstemci)</label>
                    <span id="client-fps">--</span>
                </div>
                <div class="perf-item">
                    <label>Render Süresi</label>
                    <span id="render-time">--</span>
                </div>
                <div class="perf-item">
                    <label>CPU (Sunucu)</label>
                    <span id="server-cpu">--</span>
                </div>
                <div class="perf-item">
                    <label>RAM (Sunucu)</label>
                    <span id="server-ram">--</span>
                </div>
                <div class="perf-item">
                    <label>GPU RAM</label>
                    <span id="gpu-ram">--</span>
                </div>
                <div class="perf-item">
                    <label>Bandwidth Tasarrufu</label>
                    <span id="bandwidth-saving">--</span>
                </div>
            </div>
        `;
        
        // Stats container'a ekle
        const statsContainer = document.getElementById('stats-content');
        if (statsContainer) {
            statsContainer.appendChild(performancePanel);
        }
    }

    updatePerformanceMetrics(clientMetrics) {
        // İstemci tarafı metrikleri güncelle
        this.updateElement('client-fps', `${clientMetrics.fps.toFixed(1)} FPS`);
        this.updateElement('render-time', `${clientMetrics.avgRenderTime.toFixed(2)}ms`);
        
        // Performans durumuna göre renk
        const fpsElement = document.getElementById('client-fps');
        if (fpsElement) {
            if (clientMetrics.fps >= 50) {
                fpsElement.style.color = '#3CE7CB'; // Yeşil
            } else if (clientMetrics.fps >= 30) {
                fpsElement.style.color = '#FFB86C'; // Sarı
            } else {
                fpsElement.style.color = '#F95A77'; // Kırmızı
            }
        }
    }

    async fetchServerMetrics() {
        try {
            const response = await fetch('/api/performance');
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    this.updateServerMetrics(data);
                }
            }
        } catch (error) {
            console.warn("Sunucu metriklerine erişilemedi:", error);
        }
    }

    updateServerMetrics(data) {
        const latest = data.latest;
        if (!latest) return;
        
        // CPU ve RAM
        this.updateElement('server-cpu', `${latest.cpu_percent.toFixed(1)}%`);
        this.updateElement('server-ram', `${latest.memory_mb.toFixed(0)}MB`);
        
        // GPU, backend'den bu veri yapısında gelmiyor, şimdilik kaldırıldı.
        // İleride eklenebilir.
        this.updateElement('gpu-ram', 'N/A');
        
        // Bandwidth tasarrufu (server loglarından hesaplanan değer)
        // Bu simulated bir değer, gerçekte server'dan gelmeli
        this.updateElement('bandwidth-saving', '~15%');
    }

    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
} 