class Food {
    constructor(x, y, amount) {
        this.x = x;
        this.y = y;
        this.amount = amount;
        this.radius = Math.sqrt(amount) * 0.5;
    }

    render(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(46, 160, 67, 0.6)';
        ctx.fill();
    }
}

export default class FoodSystem {
    constructor(canvas, eventBus) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.eventBus = eventBus;
        this.foodSources = [];
    }

    initialize() {
        this.setupEventListeners();
        this.reset();
    }
    
    setupEventListeners() {
        this.eventBus.on('food:add', (data) => this.addFood(data.x, data.y, data.amount));
        this.eventBus.on('simulation:resetSignal', () => this.reset());
    }

    addFood(x, y, amount) {
        this.foodSources.push(new Food(x, y, amount));
    }

    update(deltaTime) {
        // Food sources can decay over time
        this.foodSources.forEach(food => {
            food.amount -= 0.1 * deltaTime; // Decay rate
            food.radius = Math.sqrt(food.amount) * 0.5;
        });

        // Remove depleted food sources
        this.foodSources = this.foodSources.filter(food => food.amount > 1);
    }
    
    render() {
        this.foodSources.forEach(food => food.render(this.ctx));
    }

    consumeFood(x, y, consumeRadius) {
        let consumedAmount = 0;
        for (const food of this.foodSources) {
            const dist = Math.hypot(x - food.x, y - food.y);
            if (dist < consumeRadius + food.radius) {
                const amountToConsume = Math.min(food.amount, 5); // Consume a fixed amount
                food.amount -= amountToConsume;
                consumedAmount += amountToConsume;
            }
        }
        return consumedAmount;
    }

    reset() {
        this.foodSources = [];
        for (let i = 0; i < 30; i++) {
            this.addFood(
                Math.random() * this.canvas.width,
                Math.random() * this.canvas.height,
                Math.random() * 50 + 20
            );
        }
    }
} 