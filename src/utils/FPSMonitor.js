/**
 * Gelişmiş, arayüzü olmayan performans monitörü.
 * FPS, render süresi gibi metrikleri hesaplar ve callback aracılığıyla raporlar.
 */
export default class FPSMonitor {
    constructor(config = {}) {
        this.updateInterval = config.updateInterval || 1000; // ms
        this.lastUpdateTime = 0;
        this.frames = 0;
        this.fps = 0;

        this.renderTimes = [];
        this.avgRenderTime = 0;
        this.currentRenderStart = 0;

        this.callbacks = [];
        this.isRunning = false;
    }

    start() {
        this.isRunning = true;
        this.lastUpdateTime = performance.now();
        this.frames = 0;
        this.renderTimes = [];
    }

    update() {
        if (!this.isRunning) return;

        this.frames++;
        const now = performance.now();
        const delta = now - this.lastUpdateTime;

        if (delta >= this.updateInterval) {
            this.fps = (this.frames * 1000) / delta;
            this.avgRenderTime = this.renderTimes.length > 0
                ? this.renderTimes.reduce((a, b) => a + b, 0) / this.renderTimes.length
                : 0;

            this.lastUpdateTime = now;
            this.frames = 0;
            this.renderTimes = [];

            this.fireCallbacks();
        }
    }

    startRenderTiming() {
        this.currentRenderStart = performance.now();
    }

    endRenderTiming() {
        if (this.currentRenderStart > 0) {
            const renderTime = performance.now() - this.currentRenderStart;
            this.renderTimes.push(renderTime);
            this.currentRenderStart = 0;
        }
    }
    
    analyzeWebGLState(renderer) {
        // Bu metod, gelecekte WebGL render bilgisini analiz etmek için kullanılabilir.
        // Şimdilik boş bırakılmıştır.
    }

    addCallback(callback) {
        this.callbacks.push(callback);
    }

    fireCallbacks() {
        const metrics = {
            fps: this.fps,
            avgRenderTime: this.avgRenderTime,
        };
        for (const callback of this.callbacks) {
            callback(metrics);
        }
    }
} 