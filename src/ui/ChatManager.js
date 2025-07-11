export default class ChatManager {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.messageContainer = null;
    }

    initialize() {
        this.messageContainer = document.querySelector('#chat-panel .chat-messages');
        if (!this.messageContainer) {
            console.error('Chat message container not found!');
            return;
        }
        
        this.eventBus.on('chat:log', (data) => this.addMessage(data.message, data.type));
        
        // Example of logging a system message
        this.addMessage('Chat Manager Initialized.', 'system');
    }

    addMessage(text, type = 'info') {
        if (!this.messageContainer) return;

        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${type}`;
        messageEl.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
        
        this.messageContainer.appendChild(messageEl);
        
        // Auto-scroll to bottom
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }
} 