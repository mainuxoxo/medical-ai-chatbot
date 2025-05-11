document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');

    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    try {
        // Add user message
        addMessage(message, 'user');
        input.value = '';
        
        // Show loading
        loading.classList.remove('hidden');

        // Real API call
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.answer, 'bot');
        
    } catch (error) {
        showError('Failed to get response. Please try again.');
    } finally {
        loading.classList.add('hidden');
        input.focus();
    }
}

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.setAttribute('role', sender === 'bot' ? 'status' : 'none');
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageDiv.append(contentDiv, timestampDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('visible');
        setTimeout(() => {
            errorMessage.classList.remove('visible');
        }, 5000);
    }

    // Simulated response - replace with actual API call
    async function simulateBotResponse(message) {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve("This is a simulated response. Connect to your AI backend here.");
            }, 1000);
        });
    }
});