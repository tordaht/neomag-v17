import AppController from './core/AppController.js';

document.addEventListener('DOMContentLoaded', () => {
    // AppController artık tüm alt sistemleri (UI, Renderer, vb.) kendi içinde yönetiyor.
    // Bu nedenle sadece AppController'ı başlatmamız yeterli.
    new AppController(); 
}); 