import { THEME } from '../theme.js';

export default class UIManager {
    constructor() {
        this.app = null;
    }

    initialize() {
        // Login formu ile ilgili kodlar kaldırıldı,
        // ana UI doğrudan AppController tarafından yönetilecek.
        // Gerekirse, AppController'dan çağrılacak metodlar buraya eklenebilir.
    }

    loadMainUI() {
        this.setupMainLayout();
        this.canvas = document.getElementById('simulation-container-3d');
        this.initializeControls();
        this.setupEventListeners();
        this.updateTheme();
        this.createConnectionMessageElement();
    }

    getCanvas() {
        if (!this.canvas) {
            throw new Error("Canvas not initialized. Ensure initialize() is called and an element with id 'simulation-container-3d' exists.");
        }
        return this.canvas;
    }
    
    // Bu metod tüm body'yi sildiği için kaldırıldı.
    // setupMainLayout() { ... }

    initializeControls() {
        // ...
    }

    setupEventListeners() {
        // EventBus abonelikleri ve AppController'a devredilen buton eventleri kaldırıldı.
        this.getCanvas().addEventListener('click', (e) => {
            // Bu event'i AppController'a iletmek için EventBus kullanılmamalı.
            // Şimdilik yoruma alınıyor, AppController'dan direkt dinlenebilir.
            /*
            const rect = this.getCanvas().getBoundingClientRect();
            this.eventBus.emit('canvas:click', {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top,
                button: e.button
            });
            */
        });
    }
    
    createConnectionMessageElement() {
        this.connectionMessageElement = document.getElementById('connection-status-overlay');
    }

    showConnectionMessage(message) {
        if (this.connectionMessageElement) {
            this.connectionMessageElement.textContent = message;
            this.connectionMessageElement.style.display = 'flex';
        }
    }

    hideConnectionMessage() {
        if (this.connectionMessageElement) {
            this.connectionMessageElement.style.display = 'none';
        }
    }
    
    // ... (Diğer metodlar: addChart, updateAllMetrics, updateTheme)
    addChart(panelId, config) {
        const panel = document.getElementById(panelId);
        const grid = panel.querySelector('.dashboard-grid');
        if (!grid) {
            console.error(`Dashboard grid in #${panelId} not found.`);
            return null;
        }
        const chartContainer = document.createElement('div');
        chartContainer.id = config.id;
        chartContainer.className = 'chart-container';
        grid.appendChild(chartContainer);
        return chartContainer;
    }
    
    updateAllMetrics(metrics) {
        if (!metrics) return;
        const metricsBar = document.getElementById('metrics-bar');
        
        let content = '';
        for (const [key, value] of Object.entries(metrics)) {
            let formattedValue = typeof value === 'number' ? value.toFixed(2) : value;
            content += `<div class="metric"><strong>${key}:</strong> ${formattedValue}</div>`;
        }
        metricsBar.innerHTML = content;
    }

    updateTheme() {
        const root = document.documentElement;
        for (const [key, value] of Object.entries(this.theme)) {
            root.style.setProperty(`--${key}`, value);
        }
    }
} 