import EventBus from './EventBus.js';
import { Renderer2D } from '../systems/Renderer2D.js';
// DashboardManager'ı buradan kaldırıyoruz, dinamik olarak yüklenecek.
import FPSMonitor from '../utils/FPSMonitor.js';

export default class AppController {
    constructor() {
        this.socket = null;
        this.renderer = null;
        this.dashboard = null;
        this.fpsMonitor = new FPSMonitor({ updateInterval: 1000 });
        this.worldDimensionsSet = false;
        this.heartbeatInterval = null;
        this.reconnectTimeout = null;
        this.reconnectDelay = 5000;
        this.isRunning = false;

        this.pendingAcks = new Map();
        this.msgIdCounter = 0;

        this.pendingParams = {};
        this.appliedParams = {};

        // --- YENİ EKLENENLER: Gelen Veri Kuyruğu ve İşleme ---
        this.agentDataQueue = [];
        this.lastUpdateTime = 0;
        this.UPDATE_THROTTLE_MS = 16; // ~60 FPS için yeterli bir gecikme
        this.AGENT_PROCESS_LIMIT = 500; // Her karede işlenecek maksimum ajan sayısı
        // --- BİTİŞ ---

        this.paramDefinitions = [
            { id: 'speed', label: 'Ajan Hızı', min: 10, max: 200, step: 1, value: 50 },
            { id: 'aggression', label: 'Saldırganlık', min: 0, max: 1, step: 0.05, value: 0.2 },
            { id: 'energy_decay', label: 'Enerji Tüketimi', min: 0.01, max: 0.5, step: 0.01, value: 0.1 }
        ];
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp());
        } else {
            this.initializeApp();
        }
    }

    async initializeApp() { // Fonksiyonu async yapıyoruz
        console.log("AppController v17.2 başlatılıyor...");
        
        // 1. ÖNCELİK: Render motorunu hemen başlat ve ilk kareyi göster
        const canvas = document.getElementById('simulation-canvas');
        if (canvas) {
            this.renderer = new Renderer2D(canvas);
            this.animate(); // Render döngüsünü hemen başlat ki kullanıcı boş ekran görmesin
        } else {
            console.error("2D canvas 'simulation-canvas' bulunamadı.");
            return;
        }

        // 2. ÖNCELİK: Arka planda WebSocket bağlantısını kur
        this.connectWebSocket();

        this.setupEventListeners();
        this.createParameterControls();
        
        this.fpsMonitor.start();
        this.fpsMonitor.addCallback((metrics) => {
            if (this.dashboard) {
                this.dashboard.updatePerformanceMetrics(metrics);
            }
        });

        console.log("Kritik sistemler başlatıldı. Ağır bileşenler arka planda yükleniyor...");

        // 3. ÖNCELİK (KRİTİK DEĞİL): Dashboard'u ve ağır bağımlılığını tembel yükle
        try {
            const { default: DashboardManager } = await import('../systems/DashboardManager.js');
            this.dashboard = new DashboardManager();
            console.log("Dashboard ve Plotly başarıyla yüklendi.");
        } catch (error) {
            console.error("DashboardManager yüklenirken hata oluştu:", error);
        }
    }

    animate() {
        // Döngüyü sürekli hale getir
        requestAnimationFrame(this.animate.bind(this));
        
        // FPS'i her zaman güncelle
        this.fpsMonitor.update();

        // Gelen veriyi işle ve render et
        const agentsToRender = this.processAgentQueue();

        // Her zaman render yap
        if (this.renderer) {
            this.renderer.render(agentsToRender);
        }
    }

    processAgentQueue() {
        const now = performance.now();
        if (now - this.lastUpdateTime < this.UPDATE_THROTTLE_MS && this.agentDataQueue.length > 0) {
            // Return last known agents if throttled
            return this.lastProcessedAgents;
        }

        if (this.agentDataQueue.length === 0) {
            return this.lastProcessedAgents || [];
        }

        // Kuyruktaki tüm veriyi birleştirerek tek bir state oluştur
        const combinedPayload = {
            agents: [],
            dead_agent_ids: [] // Bu bilgi şu an renderda kullanılmıyor ama ileride lazım olabilir
        };
        
        let lastWorldDimensions = null;

        this.agentDataQueue.forEach(data => {
            if(data.payload.agents) {
                // Gelen son ajan listesini bir öncekilerin üzerine yazıyoruz.
                // Bu, her zaman en güncel durumu garantiler.
                combinedPayload.agents = data.payload.agents;
            }
            if(data.payload.world_dimensions) {
                lastWorldDimensions = data.payload.world_dimensions;
            }
        });

        // Kuyruğu temizle
        this.agentDataQueue = [];
        
        // Dünya boyutunu güncelle, eğer değiştiyse
        if (lastWorldDimensions && !this.worldDimensionsSet) {
             this.renderer.updateWorldSize(lastWorldDimensions);
             this.worldDimensionsSet = true; // Sadece bir kere ayarla
        }

        this.lastUpdateTime = now;
        this.lastProcessedAgents = combinedPayload.agents; // Son işlenen ajanları sakla

        // Dashboard için olay yayınla (bu kısım render'ı etkilemiyor)
        EventBus.emit('world_update', { payload: { ...combinedPayload, world_dimensions: lastWorldDimensions } });

        return combinedPayload.agents;
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

        this.socket.onopen = () => {
            console.log("🚀 WebSocket bağlantısı kuruldu.");
            this.startHeartbeat();
            if (this.reconnectTimeout) {
                clearTimeout(this.reconnectTimeout);
                this.reconnectTimeout = null;
            }
            const connStatus = document.getElementById('connection-status');
            if(connStatus) connStatus.style.display = 'none';
        };

        this.socket.onclose = () => {
            console.log("💨 WebSocket bağlantısı kapandı. Yeniden bağlanma denenecek...");
            this.stopHeartbeat();
            const connStatus = document.getElementById('connection-status');
            if(connStatus) {
                connStatus.textContent = 'Bağlantı koptu. Yeniden bağlanılıyor...';
                connStatus.style.display = 'block';
            }
            this.reconnectTimeout = setTimeout(() => this.connectWebSocket(), this.reconnectDelay);
        };

        this.socket.onerror = (error) => {
            console.error(" WebSocket Hatası:", error);
            this.socket.close();
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'ack') {
                    this.handleAck(data.payload.msgId);
                    return;
                }
                
                if (data.type === 'pong') {
                    return; 
                }

                if (data.type === 'world_update' && data.payload) {
                    // Veriyi doğrudan işlemek yerine kuyruğa ekle
                    this.agentDataQueue.push(data);
                } else {
                    // Diğer olaylar burada işlenebilir
                }
            } catch (e) {
                console.error("Gelen WebSocket mesajı işlenemedi:", e);
            }
        };
    }

    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatInterval = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                // Ping mesajları için ACK takibi yapmıyoruz
                this.socket.send(JSON.stringify({ type: 'ping' }));
            }
        }, 10000);
    }

    stopHeartbeat() {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
    }

    setupEventListeners() {
        document.getElementById('run-btn')?.addEventListener('click', () => this.runSimulation());
        document.getElementById('stop-btn')?.addEventListener('click', () => this.pauseSimulation());
        document.getElementById('reset-btn')?.addEventListener('click', () => this.resetSimulation());
        
        document.getElementById('param-apply-btn')?.addEventListener('click', () => this.applyParams());
        document.getElementById('param-revert-btn')?.addEventListener('click', () => this.revertParams());
    }

    sendMessage(type, payload = {}) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;

        const msgId = ++this.msgIdCounter;
        const message = { type, payload, msgId };
        
        this.socket.send(JSON.stringify(message));

        const timeoutId = setTimeout(() => this.retryMessage(msgId), 3000);
        this.pendingAcks.set(msgId, { message, timeoutId, retries: 0 });
    }

    handleAck(msgId) {
        const pending = this.pendingAcks.get(msgId);
        if (pending) {
            clearTimeout(pending.timeoutId);
            this.pendingAcks.delete(msgId);
        }
    }

    retryMessage(msgId) {
        const pending = this.pendingAcks.get(msgId);
        if (!pending) return;

        if (pending.retries < 3) {
            pending.retries++;
            console.warn(`Mesaj #${msgId} için ACK gelmedi. Yeniden deneniyor (${pending.retries}/3)...`);
            this.socket.send(JSON.stringify(pending.message));
            pending.timeoutId = setTimeout(() => this.retryMessage(msgId), 3000);
        } else {
            console.error(`❌ Mesaj #${msgId} gönderilemedi! Sunucu yanıt vermiyor.`);
            const connStatus = document.getElementById('connection-status');
            if(connStatus) {
                connStatus.textContent = 'Sunucuyla iletişimde sorun var. Lütfen sayfayı yenileyin.';
                connStatus.style.display = 'block';
            }
            this.pendingAcks.delete(msgId);
        }
    }

    runSimulation() {
        this.sendMessage("set_pause", { paused: false });
        this.isRunning = true;
        this.animate(); // Döngüyü başlat/devam ettir
        document.getElementById('run-btn')?.classList.add('active');
        document.getElementById('stop-btn')?.classList.remove('active');
    }

    pauseSimulation() {
        this.sendMessage("set_pause", { paused: true });
        this.isRunning = false;
        document.getElementById('run-btn')?.classList.remove('active');
        document.getElementById('stop-btn')?.classList.add('active');
    }

    resetSimulation() {
        this.sendMessage("reset", {});
        this.isRunning = false;
        document.getElementById('run-btn')?.classList.remove('active');
        document.getElementById('stop-btn')?.classList.remove('active');
    }

    createParameterControls() {
        const container = document.getElementById('parameters-content');
        if (!container) return;
        container.innerHTML = '';
        
        this.paramDefinitions.forEach(param => {
            this.appliedParams[param.id] = param.value;
        });

        this.paramDefinitions.forEach(param => {
            const wrapper = document.createElement('div');
            wrapper.className = 'param-control';
            
            const label = document.createElement('label');
            label.setAttribute('for', param.id);
            const valueLabel = document.createElement('span');
            valueLabel.textContent = `${param.label}: ${parseFloat(param.value).toFixed(2)}`;

            const slider = document.createElement('input');
            slider.type = 'range';
            slider.id = param.id;
            slider.min = param.min;
            slider.max = param.max;
            slider.step = param.step;
            slider.value = param.value;

            slider.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                valueLabel.textContent = `${param.label}: ${value.toFixed(2)}`;
                this.pendingParams[param.id] = value;
                this.showParamControls();
            });
            
            label.appendChild(valueLabel);
            wrapper.appendChild(label);
            wrapper.appendChild(slider);
            container.appendChild(wrapper);
        });
    }
    
    showParamControls() {
        document.getElementById('param-controls-footer').style.display = 'flex';
    }

    hideParamControls() {
        document.getElementById('param-controls-footer').style.display = 'none';
    }

    applyParams() {
        if (Object.keys(this.pendingParams).length > 0) {
            this.sendMessage('batch_param_change', this.pendingParams);
            
            Object.assign(this.appliedParams, this.pendingParams);
            this.pendingParams = {};
            this.hideParamControls();
        }
    }

    revertParams() {
        this.paramDefinitions.forEach(param => {
            const slider = document.getElementById(param.id);
            if (slider) {
                slider.value = this.appliedParams[param.id];
                const label = slider.previousSibling.firstChild;
                if(label) {
                     label.textContent = `${param.label}: ${parseFloat(this.appliedParams[param.id]).toFixed(2)}`;
                }
            }
        });
        this.pendingParams = {};
        this.hideParamControls();
    }
}
