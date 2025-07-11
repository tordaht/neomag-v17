class Renderer2D {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        this.worldSize = { width: 1000, height: 1000 }; // Default, will be updated
        this.camera = {
            x: 0,
            y: 0,
            zoom: 1.0
        };
    }

    updateWorldSize(size) {
        this.worldSize = size;
        this.resize();
    }

    resize() {
        this.width = this.canvas.clientWidth;
        this.height = this.canvas.clientHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;

        // Adjust zoom to fit the world into the canvas
        const zoomX = this.width / this.worldSize.width;
        const zoomY = this.height / this.worldSize.height;
        this.camera.zoom = Math.min(zoomX, zoomY) * 0.9; // 90% of the screen

        // Center the view
        this.camera.x = this.worldSize.width / 2;
        this.camera.y = this.worldSize.height / 2;
    }

    worldToScreen(x, y) {
        const screenX = (x - this.camera.x) * this.camera.zoom + this.width / 2;
        const screenY = (y - this.camera.y) * this.camera.zoom + this.height / 2;
        return { x: screenX, y: screenY };
    }
    
    getColorForAgent(agent) {
        const geneValue = agent.genetic_code[0]; // Example: color based on the first gene
        const r = Math.floor((geneValue % 256));
        const g = Math.floor(((geneValue * 17) % 256));
        const b = Math.floor(((geneValue * 31) % 256));
        return `rgb(${r},${g},${b})`;
    }


    render(agents) {
        if (!this.ctx) return;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Background
        this.ctx.fillStyle = '#111';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw agents
        if (!agents || agents.length === 0) {
            return;
        }

        const agentRadius = 2 * this.camera.zoom;

        agents.forEach(agent => {
            const screenPos = this.worldToScreen(agent.position.x, agent.position.y);
            this.ctx.beginPath();
            this.ctx.arc(screenPos.x, screenPos.y, agentRadius, 0, 2 * Math.PI, false);
            this.ctx.fillStyle = this.getColorForAgent(agent);
            this.ctx.fill();
        });
    }

    dispose() {
        this.ctx = null;
        this.canvas = null;
    }
}

export { Renderer2D }; 