"""
Streamlit component for voice input using Web Speech API
"""

import streamlit.components.v1 as components
import json

def voice_input_component(key="voice_input", listening=False):
    """
    Create a voice input component using Web Speech API
    
    Args:
        key: Unique key for the component
        listening: Whether to start listening immediately
    
    Returns:
        The transcribed text or None
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                margin: 0;
            }}
            .voice-container {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #e0e0e0;
            }}
            .status {{
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 5px;
                background: white;
            }}
            .transcript {{
                padding: 15px;
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                min-height: 80px;
                margin-bottom: 15px;
                font-size: 16px;
                line-height: 1.5;
            }}
            .button {{
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                margin: 5px;
            }}
            .btn-primary {{
                background: #4CAF50;
                color: white;
            }}
            .btn-secondary {{
                background: #f44336;
                color: white;
            }}
            .btn-primary:hover {{
                background: #45a049;
            }}
            .btn-secondary:hover {{
                background: #da190b;
            }}
        </style>
    </head>
    <body>
        <div class="voice-container">
            <div id="status" class="status">⏸️ Ready - Click Start to begin listening</div>
            <div id="transcript" class="transcript">Your speech will appear here as you talk...</div>
            <div style="display: flex; gap: 10px;">
                <button id="startBtn" class="button btn-primary" onclick="startListening()">🎙️ Start Listening</button>
                <button id="stopBtn" class="button btn-secondary" onclick="stopListening()" style="display: none;">⏹️ Stop</button>
                <button id="sendBtn" class="button btn-primary" onclick="sendMessage()" style="display: none; flex: 1;">📤 Send Message</button>
            </div>
        </div>
        
        <script>
        let recognition = null;
        let finalTranscript = '';
        let isListening = false;
        
        function initSpeechRecognition() {{
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                document.getElementById('status').textContent = '❌ Speech recognition not supported. Please use Chrome, Edge, or Safari.';
                document.getElementById('status').style.background = '#ffebee';
                document.getElementById('status').style.color = '#c62828';
                return false;
            }}
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {{
                isListening = true;
                document.getElementById('status').textContent = '🎤 Listening... Speak now!';
                document.getElementById('status').style.background = '#e8f5e9';
                document.getElementById('status').style.color = '#2e7d32';
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
                finalTranscript = '';
            }};
            
            recognition.onresult = function(event) {{
                let interimTranscript = '';
                let newFinalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {{
                        newFinalTranscript += transcript + ' ';
                    }} else {{
                        interimTranscript += transcript;
                    }}
                }}
                
                if (newFinalTranscript) {{
                    finalTranscript += newFinalTranscript;
                }}
                
                const displayText = (finalTranscript + interimTranscript).trim();
                const transcriptDiv = document.getElementById('transcript');
                transcriptDiv.textContent = displayText || 'Your speech will appear here as you talk...';
                
                if (displayText && displayText !== 'Your speech will appear here as you talk...') {{
                    document.getElementById('sendBtn').style.display = 'block';
                }}
            }};
            
            recognition.onerror = function(event) {{
                document.getElementById('status').textContent = '❌ Error: ' + event.error;
                document.getElementById('status').style.background = '#ffebee';
                document.getElementById('status').style.color = '#c62828';
                isListening = false;
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
            }};
            
            recognition.onend = function() {{
                isListening = false;
                document.getElementById('status').textContent = '⏸️ Stopped listening';
                document.getElementById('status').style.background = '#f5f5f5';
                document.getElementById('status').style.color = '#666';
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
            }};
            
            return true;
        }}
        
        function startListening() {{
            if (!recognition) {{
                if (!initSpeechRecognition()) {{
                    return;
                }}
            }}
            
            if (!isListening) {{
                try {{
                    recognition.start();
                }} catch(e) {{
                    console.log('Error starting recognition:', e);
                    // Try to reinitialize
                    initSpeechRecognition();
                    recognition.start();
                }}
            }}
        }}
        
        function stopListening() {{
            if (recognition && isListening) {{
                recognition.stop();
            }}
        }}
        
        function sendMessage() {{
            const text = document.getElementById('transcript').textContent.trim();
            if (text && text !== 'Your speech will appear here as you talk...') {{
                // Send to Streamlit parent
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: text
                }}, '*');
                
                // Also store in a way that persists
                window.voiceInputValue = text;
                
                // Stop listening
                if (recognition && isListening) {{
                    recognition.stop();
                }}
                
                // Clear transcript
                document.getElementById('transcript').textContent = 'Your speech will appear here as you talk...';
                document.getElementById('sendBtn').style.display = 'none';
                finalTranscript = '';
            }}
        }}
        
        // Initialize on load
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initSpeechRecognition);
        }} else {{
            initSpeechRecognition();
        }}
        
        // Auto-start if listening flag is set
        if ({str(listening).lower()}) {{
            setTimeout(startListening, 500);
        }}
        </script>
    </body>
    </html>
    """
    
    # Use Streamlit's component system
    result = components.html(html_code, height=300, key=key)
    return result

