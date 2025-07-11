class ScientificUI {
    constructor(containerElement) {
        if (!containerElement) {
            console.error("ScientificUI için bir konteyner elemanı sağlanmadı!");
            return;
        }
        this.container = containerElement;
        this.isInitialized = false;
        this.lastExportTime = null;
        this.currentStatistics = null;
        this.exportQueue = [];
        this.autoExportInterval = null;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        // Bilimsel kontroller panelini doğrudan sağlanan konteynere oluştur
        this.createScientificPanel(this.container);
        
        // Event listener'ları ekle
        this.setupEventListeners();
        
        // Auto-refresh başlat
        this.startAutoRefresh();
        
        this.isInitialized = true;
        console.log("🔬 Bilimsel UI v13.0 başlatıldı");
    }
    
    createScientificPanel(container) {
        // Mevcut kontrol panelini genişletmek yerine doğrudan konteyneri kullan
        container.innerHTML = ''; // Önce içini temizle
        
        // Bilimsel araçlar bölümü
        const scientificSection = document.createElement('div');
        scientificSection.className = 'scientific-section';
        scientificSection.innerHTML = `
            <div class="section-header">
                <h3>🔬 Bilimsel Analiz Araçları</h3>
                <div class="version-badge">NeoMag v13.0 Scientific</div>
            </div>
            
            <!-- Veri Dışa Aktarma -->
            <div class="tool-group">
                <h4>📊 Veri Dışa Aktarma</h4>
                <div class="export-controls">
                    <select id="export-format" class="scientific-select">
                        <option value="all">Tüm Formatlar</option>
                        <option value="csv">CSV (Analiz için)</option>
                        <option value="excel">Excel (Kapsamlı)</option>
                        <option value="json">JSON (Ham veri)</option>
                        <option value="report">İstatistik Raporu</option>
                    </select>
                    <button id="export-btn" class="scientific-btn primary">
                        📤 Veriyi Dışa Aktar
                    </button>
                    <button id="auto-export-btn" class="scientific-btn secondary">
                        ⚡ Otomatik Dışa Aktarma
                    </button>
                </div>
                <div id="export-status" class="status-indicator"></div>
            </div>
            
            <!-- Anlık İstatistikler -->
            <div class="tool-group">
                <h4>📈 Canlı İstatistikler</h4>
                <div id="live-statistics" class="statistics-grid">
                    <div class="stat-card">
                        <span class="stat-label">Popülasyon Analizi</span>
                        <div id="population-stats" class="stat-values">Yükleniyor...</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Enerji Dinamikleri</span>
                        <div id="energy-stats" class="stat-values">Yükleniyor...</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Genetik Çeşitlilik</span>
                        <div id="genetics-stats" class="stat-values">Yükleniyor...</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Üreme Başarısı</span>
                        <div id="reproduction-stats" class="stat-values">Yükleniyor...</div>
                    </div>
                </div>
                <button id="refresh-stats-btn" class="scientific-btn secondary">
                    🔄 İstatistikleri Güncelle
                </button>
            </div>
            
            <!-- Araştırma Kontrolleri -->
            <div class="tool-group">
                <h4>🧪 Araştırma Kontrolleri</h4>
                <div class="research-controls">
                    <button id="save-snapshot-btn" class="scientific-btn secondary">
                        📸 Snapshot Kaydet
                    </button>
                    <button id="reset-simulation-btn" class="scientific-btn warning">
                        🔄 Simülasyonu Sıfırla
                    </button>
                    <button id="toggle-detailed-logging" class="scientific-btn secondary">
                        📝 Detaylı Kayıt
                    </button>
                </div>
            </div>
            
            <!-- Veri Analiz Görünümü -->
            <div class="tool-group">
                <h4>📊 Veri Görselleştirme</h4>
                <div class="visualization-controls">
                    <select id="chart-type" class="scientific-select">
                        <option value="fitness_vs_generation">Fitness vs. Jenerasyon</option>
                        <option value="population_vs_generation">Popülasyon vs. Jenerasyon</option>
                        <option value="genetic_diversity_vs_generation">Genetik Çeşitlilik vs. Jenerasyon</option>
                        <option value="age_vs_fitness">Yaş vs. Fitness Dağılımı</option>
                        <option value="speed_vs_efficiency">Hız vs. Verimlilik Dağılımı</option>
                    </select>
                    <button id="update-chart-btn" class="scientific-btn primary">
                        📈 Grafiği Güncelle
                    </button>
                </div>
                <div id="scientific-chart-container" style="width:100%; height:250px; margin-top:10px; background: #0f172a; border-radius: 6px;"></div>
            </div>
            
            <!-- Sistem Durumu -->
            <div class="tool-group">
                <h4>⚙️ Sistem Durumu</h4>
                <div id="system-status" class="system-status">
                    <div class="status-row">
                        <span>Simülasyon:</span>
                        <span id="sim-status" class="status-running">Çalışıyor</span>
                    </div>
                    <div class="status-row">
                        <span>Veri Kalitesi:</span>
                        <span id="data-quality" class="status-good">İyi</span>
                    </div>
                    <div class="status-row">
                        <span>Son Dışa Aktarma:</span>
                        <span id="last-export">Henüz yok</span>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(scientificSection);
        
        // CSS stillerini ekle
        this.addScientificStyles();
    }
    
    createBasePanel() {
        const panel = document.createElement('div');
        panel.id = 'control-panel';
        panel.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 350px;
            background: rgba(20, 25, 40, 0.95);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #e2e8f0;
            z-index: 1000;
            max-height: 85vh;
            overflow-y: auto;
            backdrop-filter: blur(10px);
        `;
        document.body.appendChild(panel);
        return panel;
    }
    
    addScientificStyles() {
        if (document.getElementById('scientific-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'scientific-styles';
        style.textContent = `
            .scientific-section {
                margin-top: 20px;
                border-top: 2px solid #3b82f6;
                padding-top: 15px;
            }
            
            .section-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .section-header h3 {
                margin: 0;
                color: #60a5fa;
                font-size: 16px;
            }
            
            .version-badge {
                background: linear-gradient(45deg, #3b82f6, #1d4ed8);
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            }
            
            .tool-group {
                margin-bottom: 20px;
                padding: 15px;
                background: rgba(15, 23, 42, 0.6);
                border-radius: 8px;
                border: 1px solid #1e293b;
            }
            
            .tool-group h4 {
                margin: 0 0 10px 0;
                color: #94a3b8;
                font-size: 14px;
                font-weight: 600;
            }
            
            .scientific-btn {
                background: linear-gradient(45deg, #1e40af, #3730a3);
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                margin: 2px;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            
            .scientific-btn:hover {
                background: linear-gradient(45deg, #2563eb, #4338ca);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            .scientific-btn.secondary {
                background: linear-gradient(45deg, #475569, #64748b);
            }
            
            .scientific-btn.secondary:hover {
                background: linear-gradient(45deg, #64748b, #94a3b8);
            }
            
            .scientific-btn.warning {
                background: linear-gradient(45deg, #dc2626, #991b1b);
            }
            
            .scientific-btn.warning:hover {
                background: linear-gradient(45deg, #ef4444, #dc2626);
            }
            
            .scientific-select {
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                margin: 2px;
                width: 100%;
            }
            
            .export-controls {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .statistics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin: 10px 0;
            }
            
            .stat-card {
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 10px;
                text-align: center;
            }
            
            .stat-label {
                display: block;
                font-size: 11px;
                color: #94a3b8;
                margin-bottom: 5px;
                font-weight: 600;
            }
            
            .stat-values {
                font-size: 11px;
                color: #e2e8f0;
                line-height: 1.4;
            }
            
            .status-indicator {
                margin: 8px 0;
                padding: 6px;
                border-radius: 4px;
                font-size: 11px;
                text-align: center;
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid #334155;
            }
            
            .status-indicator.success {
                background: rgba(16, 185, 129, 0.1);
                color: #10b981;
                border-color: #10b981;
            }
            
            .status-indicator.error {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
                border-color: #ef4444;
            }
            
            .status-indicator.processing {
                background: rgba(245, 158, 11, 0.1);
                color: #f59e0b;
                border-color: #f59e0b;
            }
            
            .research-controls {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            }
            
            .research-controls .scientific-btn {
                flex: 1;
                min-width: 100px;
                justify-content: center;
            }
            
            .visualization-controls {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .system-status {
                font-size: 11px;
            }
            
            .status-row {
                display: flex;
                justify-content: space-between;
                margin: 4px 0;
                padding: 2px 0;
            }
            
            .status-running { color: #10b981; }
            .status-stopped { color: #ef4444; }
            .status-good { color: #10b981; }
            .status-warning { color: #f59e0b; }
            .status-error { color: #ef4444; }
        `;
        
        document.head.appendChild(style);
    }
    
    setupEventListeners() {
        // Veri dışa aktarma
        document.getElementById('export-btn')?.addEventListener('click', () => {
            this.exportData();
        });
        
        // Otomatik dışa aktarma
        document.getElementById('auto-export-btn')?.addEventListener('click', () => {
            this.toggleAutoExport();
        });
        
        // İstatistik güncelleme
        document.getElementById('refresh-stats-btn')?.addEventListener('click', () => {
            this.refreshStatistics();
        });
        
        // Snapshot kaydetme
        document.getElementById('save-snapshot-btn')?.addEventListener('click', () => {
            this.saveSnapshot();
        });
        
        // Grafik güncelleme
        document.getElementById('update-chart-btn')?.addEventListener('click', () => {
            this.updateChart();
        });
    }
    
    async exportData() {
        const formatSelect = document.getElementById('export-format');
        const statusDiv = document.getElementById('export-status');
        const exportBtn = document.getElementById('export-btn');
        
        if (!formatSelect || !statusDiv) return;
        
        const format = formatSelect.value;
        
        try {
            // UI feedback
            statusDiv.className = 'status-indicator processing';
            statusDiv.textContent = 'Veriler dışa aktarılıyor...';
            exportBtn.disabled = true;
            exportBtn.textContent = '⏳ İşleniyor...';
            
            // API çağrısı
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ format_type: format }),
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                statusDiv.className = 'status-indicator success';
                statusDiv.textContent = `✅ ${result.message}`;
                
                // Son dışa aktarma zamanını güncelle
                this.lastExportTime = new Date();
                document.getElementById('last-export').textContent = 
                    this.lastExportTime.toLocaleTimeString('tr-TR');
                
                // Dosya listesini göster
                if (result.files) {
                    const fileList = Object.values(result.files).map(file => 
                        file.split('/').pop()
                    ).join(', ');
                    setTimeout(() => {
                        statusDiv.textContent += ` (${fileList})`;
                    }, 2000);
                }
                
            } else {
                throw new Error(result.message || 'Bilinmeyen hata');
            }
            
        } catch (error) {
            console.error('Export error:', error);
            statusDiv.className = 'status-indicator error';
            statusDiv.textContent = `❌ Hata: ${error.message}`;
        } finally {
            exportBtn.disabled = false;
            exportBtn.textContent = '📤 Veriyi Dışa Aktar';
        }
    }
    
    async refreshStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.updateStatisticsDisplay(result.statistics);
                this.currentStatistics = result.statistics;
            } else {
                console.error('Statistics error:', result.message);
            }
        } catch (error) {
            console.error('Failed to fetch statistics:', error);
        }
    }
    
    updateStatisticsDisplay(stats) {
        // Popülasyon
        const popElement = document.getElementById('population-stats');
        if (popElement && stats.population) {
            popElement.innerHTML = `
                <div>Toplam: ${stats.population.total}</div>
                <div>Hayatta: ${stats.population.alive}</div>
                <div>Ölüm Oranı: ${(stats.population.death_rate * 100).toFixed(1)}%</div>
            `;
        }
        
        // Enerji
        const energyElement = document.getElementById('energy-stats');
        if (energyElement && stats.energy) {
            energyElement.innerHTML = `
                <div>Ort: ${stats.energy.mean.toFixed(1)}</div>
                <div>±${stats.energy.std.toFixed(1)}</div>
                <div>Min-Max: ${stats.energy.min.toFixed(0)}-${stats.energy.max.toFixed(0)}</div>
            `;
        }
        
        // Genetik
        const geneticsElement = document.getElementById('genetics-stats');
        if (geneticsElement && stats.genetics) {
            geneticsElement.innerHTML = `
                <div>Hız: ${stats.genetics.speed_mean.toFixed(2)}</div>
                <div>Verimlilik: ${stats.genetics.efficiency_mean.toFixed(2)}</div>
                <div>Algılama: ${stats.genetics.detection_mean.toFixed(0)}</div>
            `;
        }
        
        // Üreme
        const reproductionElement = document.getElementById('reproduction-stats');
        if (reproductionElement && stats.reproduction) {
            reproductionElement.innerHTML = `
                <div>Toplam Yavru: ${stats.reproduction.total_offspring}</div>
                <div>Ort/Ajan: ${stats.reproduction.avg_offspring_per_agent.toFixed(1)}</div>
                <div>Üreyen: ${stats.reproduction.reproductive_agents}</div>
            `;
        }
    }
    
    async saveSnapshot() {
        const btn = document.getElementById('save-snapshot-btn');
        try {
            btn.disabled = true;
            btn.textContent = '⏳ Kaydediliyor...';
            
            const response = await fetch('/api/save_snapshot', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.status === 'success') {
                btn.textContent = '✅ Kaydedildi';
                setTimeout(() => {
                    btn.textContent = '📸 Snapshot Kaydet';
                }, 2000);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            btn.textContent = '❌ Hata';
            setTimeout(() => {
                btn.textContent = '📸 Snapshot Kaydet';
            }, 2000);
        } finally {
            btn.disabled = false;
        }
    }
    
    toggleAutoExport() {
        const btn = document.getElementById('auto-export-btn');
        
        if (this.autoExportInterval) {
            // Durdur
            clearInterval(this.autoExportInterval);
            this.autoExportInterval = null;
            btn.textContent = '⚡ Otomatik Dışa Aktarma';
            btn.className = 'scientific-btn secondary';
        } else {
            // Başlat (her 5 dakikada bir)
            this.autoExportInterval = setInterval(() => {
                this.exportData();
            }, 5 * 60 * 1000);
            btn.textContent = '⏹️ Otomatik Durdur';
            btn.className = 'scientific-btn warning';
        }
    }
    
    async updateChart() {
        const chartContainer = document.getElementById('scientific-chart-container');
        const chartType = document.getElementById('chart-type').value;
        if (!chartContainer || !chartType) return;

        try {
            // Veri çekme (geçmiş ve anlık durum)
            const metricsRes = await fetch('/api/metrics_history');
            
            if (!metricsRes.ok) {
                throw new Error("Metrik verisi sunucudan alınamadı.");
            }

            const metricsHistory = await metricsRes.json();
            
            // Mevcut istatistikleri kullan, yeniden çekme
            const worldStateData = this.currentStatistics; 
            
            if (!worldStateData || worldStateData.status !== 'success') {
                 throw new Error(worldStateData?.message || 'Geçerli istatistik verisi bulunamadı. Lütfen güncelleyin.');
            }
            
            // world_state yerine doğrudan statistics altındaki ajanları kullan
            const agents = worldStateData?.statistics?.population?.all_agents_for_chart || [];

            // Grafik verisini hazırla
            const { data, layout } = this.prepareChartData(chartType, metricsHistory, agents);

            // Grafiği çiz
            Plotly.newPlot(chartContainer, data, { ...this.getCommonLayout(), ...layout }, {responsive: true, displaylogo: false});

        } catch (error) {
            console.error("Grafik güncelleme hatası:", error);
            chartContainer.innerHTML = `<div class="status-indicator error" style="height:100%; display:flex; align-items:center; justify-content:center;">Grafik yüklenemedi: ${error.message}</div>`;
        }
    }

    getCommonLayout() {
        return {
            paper_bgcolor: 'rgba(15, 23, 42, 0.8)',
            plot_bgcolor: 'rgba(15, 23, 42, 1)',
            margin: { l: 50, r: 30, b: 40, t: 30, pad: 4 },
            legend: { font: { color: '#e2e8f0' } },
            font: {
                family: 'Segoe UI, sans-serif',
                color: '#94a3b8'
            },
            xaxis: { gridcolor: '#1e293b' },
            yaxis: { gridcolor: '#1e293b' }
        };
    }

    prepareChartData(type, history, agents) {
        let data = [];
        let layout = {};

        switch (type) {
            case 'fitness_vs_generation':
                data = [{
                    x: history.map(h => h.generation),
                    y: history.map(h => h.avg_fitness),
                    type: 'scatter', mode: 'lines+markers', name: 'Ort. Fitness',
                    line: { color: '#2563eb' }
                }];
                layout = { title: 'Ortalama Fitness Değişimi', xaxis: {title: 'Jenerasyon'}, yaxis: {title: 'Fitness'} };
                break;
            
            case 'population_vs_generation':
                data = [{
                    x: history.map(h => h.generation),
                    y: history.map(h => h.population_size),
                    type: 'bar', name: 'Popülasyon',
                    marker: { color: '#10b981' }
                }];
                layout = { title: 'Popülasyon Değişimi', xaxis: {title: 'Jenerasyon'}, yaxis: {title: 'Ajan Sayısı'} };
                break;

            case 'genetic_diversity_vs_generation':
                data = [{
                    x: history.map(h => h.generation),
                    y: history.map(h => h.genetic_diversity),
                    type: 'scatter', mode: 'lines', name: 'Genetik Çeşitlilik',
                    line: { color: '#f59e0b' }, fill: 'tozeroy'
                }];
                layout = { title: 'Genetik Çeşitlilik İndeksi', xaxis: {title: 'Jenerasyon'}, yaxis: {title: 'Shannon İndeksi'} };
                break;

            case 'age_vs_fitness':
                data = [{
                    x: agents.map(a => a.age),
                    y: agents.map(a => a.genes.speed * 10 + a.energy), // Örnek fitness
                    mode: 'markers', type: 'scatter',
                    marker: { 
                        size: agents.map(a => a.energy / 10),
                        color: agents.map(a => a.generation),
                        colorscale: 'Viridis',
                        showscale: true
                    }
                }];
                layout = { title: 'Yaş-Fitness Dağılımı', xaxis: {title: 'Yaş (tick)'}, yaxis: {title: 'Hesaplanan Fitness'} };
                break;
            
            case 'speed_vs_efficiency':
                 data = [{
                    x: agents.map(a => a.genes.speed),
                    y: agents.map(a => a.genes.energy_efficiency),
                    mode: 'markers', type: 'scatter',
                    marker: { 
                        size: 8,
                        color: agents.map(a => a.energy),
                        colorscale: 'Plasma',
                        showscale: true,
                        colorbar: { title: 'Enerji' }
                    }
                }];
                layout = { title: 'Hız-Verimlilik Gen Dağılımı', xaxis: {title: 'Gen: Hız'}, yaxis: {title: 'Gen: Enerji Verimliliği'} };
                break;
        }
        return { data, layout };
    }
    
    startAutoRefresh() {
        // Her 10 saniyede bir istatistikleri güncelle
        setInterval(() => {
            this.refreshStatistics();
        }, 10000);
        
        // İlk güncelleme
        setTimeout(() => {
            this.refreshStatistics();
            this.updateChart(); // İstatistikler güncellendikten sonra grafiği de güncelle
        }, 2000);
    }
}

// Modül olarak dışa aktar
export default ScientificUI; 