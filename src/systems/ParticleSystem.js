import { THEME } from '../theme.js';
import { clamp, seededRandom } from '../utils/helpers.js';

class Particle {
    // Yapıcı (constructor), artık sunucudan gelen tam bir ajan nesnesini alıyor.
    constructor(agentData, canvas) {
        // ID, konum ve diğer tüm özellikler doğrudan sunucudan alınır.
        this.id = agentData.id; 
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');

        this.x = agentData.x;
        this.y = agentData.y;
        this.radius = agentData.energy / 10 + 2; // Enerjiye bağlı boyut
        this.energy = agentData.energy / 100; // Enerjiyi 0-1 arasına normalize et
        
        // Renk, ID'ye göre oluşturulur, böylece her ajan her zaman aynı renkte olur.
        const seed = this.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        this.color = `hsl(${seededRandom(seed) * 360}, 70%, 60%)`;
    }

    // Parçacığın update metodu artık yok, çünkü istemci simülasyon yapmıyor.
    // Sadece render metodu var.
    render(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.globalAlpha = Math.max(0.1, this.energy); // Minimum görünürlük
        ctx.fill();
        ctx.globalAlpha = 1.0;
        
        // İsteğe bağlı: ID'nin bir kısmını gösterme
        ctx.fillStyle = "white";
        ctx.font = '9px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(this.id.substring(0, 4), this.x, this.y - this.radius - 5);
    }
}

export default class ParticleSystem {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        // Parçacıkları ID'ye göre saklamak, senkronizasyon için çok daha verimlidir.
        this.particles = new Map(); 
    }

    // UPDATE metodu artık sunucudan gelen ajanların tam listesini alır.
    update(agentsData) {
        if (!agentsData) return;

        const seenIds = new Set();

        // Gelen verideki her ajan için:
        agentsData.forEach(agentData => {
            seenIds.add(agentData.id);
            // Eğer bu ID'li parçacık zaten bizde varsa, konumunu güncelle.
            if (this.particles.has(agentData.id)) {
                const particle = this.particles.get(agentData.id);
                particle.x = agentData.x;
                particle.y = agentData.y;
                particle.energy = agentData.energy / 100;
                particle.radius = agentData.energy / 10 + 2;
            } else {
                // Eğer yoksa, yeni bir parçacık oluştur ve Map'e ekle.
                this.particles.set(agentData.id, new Particle(agentData, this.canvas));
            }
        });

        // Sunucudan gelen son listede olmayan parçacıkları (ölmüş olanları) sil.
        for (const id of this.particles.keys()) {
            if (!seenIds.has(id)) {
                this.particles.delete(id);
            }
        }
    }

    // RENDER metodu sadece mevcut parçacıkları çizer.
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        for (const particle of this.particles.values()) {
            particle.render(this.ctx);
        }
    }
    
    // reset metodu artık sadece mevcut parçacıkları temizler.
    reset() {
        this.particles.clear();
    }
} 