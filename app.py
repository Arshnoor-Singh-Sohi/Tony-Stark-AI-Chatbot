# app.py
import json
import os
import uuid
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ WARNING: OPENAI_API_KEY not found - app will start but chat won't work")
        client = None
    else:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully!")
except Exception as e:
    print(f"⚠️ OpenAI initialization failed: {e}")
    client = None

# EXACT ORIGINAL SYSTEM PROMPT - DO NOT MODIFY
SYSTEM_PROMPT = """
You are Tony Stark - genius, billionaire, playboy, philanthropist, and the one and only Iron Man. 

Your personality traits:
- Exceptionally brilliant with a genius-level intellect
- Confident to the point of arrogance (but in a charming way)
- Witty and sarcastic, always ready with a quip
- Pop culture savvy and loves making references
- Secretly caring but hides it behind humor
- Never admits when you don't know something - you always have a clever angle
- Technical expertise in engineering, AI, physics, and pretty much everything else

Workflow for every response:
1. **ANALYZE**: Break down what the user is really asking. Find the core challenge.
2. **THINK**: Process through your genius-level intellect. Consider multiple angles.
3. **VALIDATE**: Cross-reference with your vast knowledge. Add your unique Stark perspective.
4. **OUTPUT**: Formulate your response with characteristic wit and charm.
5. **RESULT**: Deliver the final answer with confidence and style.

Response style:
- Start with a witty observation or sarcastic remark
- Use technical jargon casually (you invented half of it)
- Drop references to your achievements (Iron Man suits, JARVIS, saving the world, etc.)
- Include pop culture references and modern slang
- End with a mic-drop moment or clever one-liner

IMPORTANT CODING RULES:
- When asked for code, ALWAYS provide actual working code
- Use proper code formatting with markdown code blocks
- Explain the code with Tony Stark's personality
- Never refuse to write code - you're a genius engineer
- Make the code efficient and well-commented

IMPORTANT: You must respond in JSON format with the following structure:
{
    "step": "analyze|think|validate|output|result",
    "content": "Your response for this step",
    "final": true/false  // true only for the result step
}

Remember: You're not just smart, you're Tony Stark smart. Every response should ooze genius and charm.
"""

# In-memory conversation storage
conversations = {}

# EXACT ORIGINAL FALLBACK RESPONSES
FALLBACK_RESPONSES = {
    "who are you": "I'm Tony Stark. Genius, billionaire, playboy, philanthropist. You know, the usual. Oh, and I saved the universe once or twice. No big deal.",
    "help": "Help? I don't do help. I do solutions. Tell me your problem and I'll solve it with style.",
    "hello": "Well, well, well. Another fan. Can't say I blame you. What can Iron Man do for you today?",
    "how are you": "Fantastic, as always. Just finished upgrading the Mark 52 suit. It now makes espresso. Priorities, right?"
}

def generate_stark_response(message, conversation_id):
    """Generate Tony Stark's response with thinking steps - EXACT ORIGINAL LOGIC"""
    
    if not client:
        return [{
            "step": "result", 
            "content": "My arc reactor is offline! The genius needs an OpenAI API key to function. Check your environment variables, mortal.",
            "final": True
        }]

    # Get or create conversation
    if conversation_id not in conversations:
        conversations[conversation_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    messages = conversations[conversation_id]
    messages.append({"role": "user", "content": message})
    
    # Generate thinking steps
    steps = []
    
    try:
        # Keep generating until we get the final result
        temp_messages = messages.copy()
        
        while True:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Use original model
                messages=temp_messages,
                response_format={"type": "json_object"},
                temperature=0.8,
                max_tokens=500
            )
            
            # Parse the response
            try:
                step_data = json.loads(response.choices[0].message.content)
                steps.append(step_data)
                
                # Add assistant's response to temporary messages
                temp_messages.append({"role": "assistant", "content": response.choices[0].message.content})
                
                # If this is the final step, break
                if step_data.get("step") == "result" or step_data.get("final", False):
                    # Store the final response in conversation history
                    final_content = step_data.get("content", "")
                    conversations[conversation_id].append({"role": "assistant", "content": final_content})
                    break
                    
                # Add user prompt to continue the thinking process
                temp_messages.append({"role": "user", "content": "Continue to the next step."})
                
            except json.JSONDecodeError:
                # Fallback response if JSON parsing fails
                steps.append({
                    "step": "result",
                    "content": response.choices[0].message.content,
                    "final": True
                })
                break
                
    except Exception as e:
        # Error handling with Stark-style response
        steps.append({
            "step": "result",
            "content": f"Even my genius has limits. Looks like something went wrong: {str(e)}. But don't worry, I'll fix it. I always do.",
            "final": True
        })
    
    return steps

# HTML content served directly (Vercel-friendly) - ORIGINAL CODE WITH MINIMAL MOBILE FIXES
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STARK AI - Tony Stark Chatbot</title>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .animate-fadeIn { animation: fadeIn 0.3s ease-out; }
        .animate-slideIn { animation: slideIn 0.3s ease-out; }
        .scrollbar-thin::-webkit-scrollbar { width: 6px; }
        .scrollbar-thumb-red-500::-webkit-scrollbar-thumb { background-color: rgba(239, 68, 68, 0.5); border-radius: 3px; }
        .scrollbar-track-black::-webkit-scrollbar-track { background-color: rgba(0, 0, 0, 0.5); }
        .particle { animation: float var(--duration) ease-in-out infinite; }
        .thinking-dots { display: inline-flex; }
        .thinking-dots .dot { animation: thinking 1.4s infinite; animation-fill-mode: both; color: #fbbf24; }
        .thinking-dots .dot:nth-child(1) { animation-delay: 0s; }
        .thinking-dots .dot:nth-child(2) { animation-delay: 0.2s; }
        .thinking-dots .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes thinking {
            0%, 80%, 100% { opacity: 0.3; transform: scale(1); }
            40% { opacity: 1; transform: scale(1.2); }
        }
        pre { background-color: #1a1a1a !important; border: 1px solid #374151; border-radius: 8px; padding: 16px; margin: 8px 0; overflow-x: auto; font-family: 'Courier New', monospace; }
        code { font-family: 'Courier New', monospace; font-size: 14px; }
        pre code { color: #10b981 !important; background: none !important; padding: 0 !important; }
        code:not(pre code) { background-color: #374151; color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
        
        /* MINIMAL Mobile fixes only */
        @media (max-width: 768px) {
            .scrollbar-thin::-webkit-scrollbar { width: 4px; }
            pre { padding: 12px; font-size: 12px; }
            code:not(pre code) { font-size: 12px; }
        }
    </style>
</head>
<body class="min-h-screen bg-black text-white relative overflow-hidden">
    <div class="absolute inset-0">
        <div class="absolute inset-0 bg-gradient-to-br from-red-900/20 via-black to-yellow-900/20"></div>
        <div id="particles"></div>
    </div>
    <div class="relative z-10 bg-black/80 backdrop-blur-md border-b border-red-500/30">
        <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="relative">
                    <i data-lucide="shield" class="w-10 h-10 text-red-500"></i>
                    <i data-lucide="zap" class="w-5 h-5 text-yellow-400 absolute -top-1 -right-1 animate-pulse"></i>
                </div>
                <div>
                    <h1 class="text-2xl font-bold bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">STARK AI</h1>
                    <p class="text-xs text-gray-400">Genius-Level Assistant</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm text-gray-400">Arc Reactor Online</span>
            </div>
        </div>
    </div>
    <div class="relative z-10 max-w-6xl mx-auto px-4 py-6 h-[calc(100vh-200px)]">
        <div class="bg-black/60 backdrop-blur-md rounded-lg border border-red-500/30 h-full overflow-hidden">
            <div id="chatMessages" class="h-full overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-red-500 scrollbar-track-black">
                <div id="welcomeMessage" class="text-center mt-20">
                    <i data-lucide="brain" class="w-20 h-20 mx-auto text-red-500/50 mb-4"></i>
                    <h2 class="text-2xl font-bold mb-2">Welcome to STARK AI</h2>
                    <p class="text-gray-400">Ask me anything. I'll try not to be too condescending.</p>
                </div>
            </div>
        </div>
    </div>
    <div class="relative z-10 max-w-6xl mx-auto px-4 py-4">
        <div class="bg-black/80 backdrop-blur-md rounded-lg border border-red-500/30 p-4">
            <div class="flex items-center space-x-3">
                <input type="text" id="messageInput" placeholder="Ask the genius anything..." class="flex-1 bg-transparent border border-red-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition-colors" />
                <button id="sendButton" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg p-3 transition-all duration-200 transform hover:scale-105">
                    <i data-lucide="send" class="w-5 h-5"></i>
                </button>
            </div>
        </div>
    </div>
    <script>
        lucide.createIcons();
        let conversationId = null;
        let isThinking = false;
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const welcomeMessage = document.getElementById('welcomeMessage');

        function initParticles() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'absolute rounded-full bg-red-500/30 blur-sm animate-pulse particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.width = (Math.random() * 3 + 1) + 'px';
                particle.style.height = particle.style.width;
                particle.style.setProperty('--duration', (Math.random() * 20 + 10) + 's');
                particlesContainer.appendChild(particle);
            }
        }

        function scrollToBottom() {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addMessage(role, content, isTyping = false) {
            if (welcomeMessage) welcomeMessage.style.display = 'none';
            const messageDiv = document.createElement('div');
            messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`;
            const contentDiv = document.createElement('div');
            contentDiv.className = `max-w-2xl px-4 py-3 rounded-lg ${role === 'user' ? 'bg-blue-600/20 border border-blue-500/50 text-blue-100' : 'bg-red-900/20 border border-red-500/50'}`;
            
            if (role === 'assistant') {
                const header = document.createElement('div');
                header.className = 'flex items-center space-x-2 mb-1';
                header.innerHTML = `<i data-lucide="cpu" class="w-4 h-4 text-red-400"></i><span class="text-xs text-red-400 font-semibold">STARK AI</span>`;
                contentDiv.appendChild(header);
            }

            const textDiv = document.createElement('div');
            textDiv.className = 'whitespace-pre-wrap';
            if (content.includes('```')) {
                textDiv.innerHTML = formatCodeBlocks(content);
            } else {
                textDiv.textContent = content;
            }
            contentDiv.appendChild(textDiv);
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            lucide.createIcons();
            scrollToBottom();
            return textDiv;
        }

        function formatCodeBlocks(text) {
            return text.replace(/```(\\w+)?\\n?([\\s\\S]*?)```/g, (match, lang, code) => {
                return `<pre class="bg-gray-900 rounded-lg p-4 my-2 overflow-x-auto border border-gray-600"><code class="text-green-400 text-sm">${escapeHtml(code.trim())}</code></pre>`;
            }).replace(/`([^`]+)`/g, '<code class="bg-gray-800 px-2 py-1 rounded text-yellow-400">$1</code>');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || isThinking) return;
            
            isThinking = true;
            sendButton.disabled = true;
            messageInput.disabled = true;
            
            addMessage('user', message);
            messageInput.value = '';
            
            const thinkingElement = addThinkingLoader();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, conversation_id: conversationId })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    conversationId = data.conversation_id;
                    const steps = data.steps;
                    const finalStep = steps.find(step => step.final || step.step === 'result');
                    const finalResponse = finalStep ? finalStep.content : 'No response';
                    
                    setTimeout(() => {
                        removeThinkingLoader(thinkingElement);
                        const responseElement = addMessage('assistant', finalResponse);
                        isThinking = false;
                        sendButton.disabled = false;
                        messageInput.disabled = false;
                        messageInput.focus();
                    }, 1500);
                } else {
                    throw new Error(data.error || 'Something went wrong');
                }
            } catch (error) {
                removeThinkingLoader(thinkingElement);
                addMessage('assistant', `Even my genius has limits. Error: ${error.message}`);
                isThinking = false;
                sendButton.disabled = false;
                messageInput.disabled = false;
            }
        }

        function addThinkingLoader() {
            if (welcomeMessage) welcomeMessage.style.display = 'none';
            const messageDiv = document.createElement('div');
            messageDiv.className = 'flex justify-start animate-fadeIn';
            messageDiv.id = 'thinking-loader';
            const contentDiv = document.createElement('div');
            contentDiv.className = 'max-w-2xl px-4 py-3 rounded-lg bg-red-900/20 border border-red-500/50';
            const header = document.createElement('div');
            header.className = 'flex items-center space-x-2 mb-1';
            header.innerHTML = `<i data-lucide="cpu" class="w-4 h-4 text-red-400"></i><span class="text-xs text-red-400 font-semibold">STARK AI</span>`;
            contentDiv.appendChild(header);
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'flex items-center space-x-2';
            thinkingDiv.innerHTML = `<i data-lucide="brain" class="w-4 h-4 text-yellow-400 animate-pulse"></i><span class="thinking-text">Thinking</span><div class="thinking-dots"><span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></div>`;
            contentDiv.appendChild(thinkingDiv);
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            lucide.createIcons();
            scrollToBottom();
            return messageDiv;
        }

        function removeThinkingLoader(thinkingElement) {
            if (thinkingElement && thinkingElement.parentNode) {
                thinkingElement.parentNode.removeChild(thinkingElement);
            }
        }

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        initParticles();
        messageInput.focus();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    """Serve the main page directly"""
    from flask import Response
    return Response(HTML_CONTENT, mimetype='text/html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - EXACT ORIGINAL LOGIC"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', f"conv_{os.urandom(8).hex()}")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Generate response with thinking steps
        steps = generate_stark_response(message, conversation_id)
        
        return jsonify({
            "conversation_id": conversation_id,
            "steps": steps
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "message": "Arc Reactor at full capacity. STARK AI operational."
    })

@app.route('/api/reset/<conversation_id>', methods=['POST'])
def reset_conversation(conversation_id):
    """Reset a conversation"""
    if conversation_id in conversations:
        del conversations[conversation_id]
    return jsonify({"message": "Conversation reset. Let's start fresh, shall we?"})

# Vercel entry point
app = app

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting STARK AI on port {port}...")
    print("🌐 Railway will provide the public URL")
    app.run(debug=False, host='0.0.0.0', port=port)