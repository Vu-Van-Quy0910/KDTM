// Simple dynamic example: smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute("href")).scrollIntoView({
            behavior: "smooth"
        });
    });
});

// DOM Elements
const chatbotButton = document.getElementById('open-chatbot');
const chatbotWidget = document.getElementById('chatbot-widget');
const closeChatbotButton = document.getElementById('close-chatbot');
const chatbotFooterInput = document.querySelector('.chatbot-footer input');
const chatbotBody = document.querySelector('.chatbot-body');

// Hiển thị chatbot
chatbotButton.addEventListener('click', () => {
    chatbotWidget.classList.remove('d-none');
});

// Ẩn chatbot
closeChatbotButton.addEventListener('click', () => {
    chatbotWidget.classList.add('d-none');
});

// Gửi tin nhắn khi nhấn Enter
chatbotFooterInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const userMessage = chatbotFooterInput.value.trim();
        if (userMessage) {
            appendMessage('user', userMessage);
            chatbotFooterInput.value = '';

            // Giả lập phản hồi từ chatbot
            setTimeout(() => {
                appendMessage('bot', getBotResponse(userMessage));
            }, 1000);
        }
    }
});

// Hàm thêm tin nhắn
function appendMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatbotBody.appendChild(messageDiv);
    chatbotBody.scrollTop = chatbotBody.scrollHeight;
}

// Phản hồi chatbot
function getBotResponse(message) {
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('chào')) {
        return 'Xin chào! Tôi có thể giúp gì cho bạn?';
    }
    return 'Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn.';
}

