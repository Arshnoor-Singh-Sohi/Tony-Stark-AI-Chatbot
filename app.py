# app.py
import json
import os
import uuid
import time
from flask import Flask, request, jsonify, render_template, Response
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
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
