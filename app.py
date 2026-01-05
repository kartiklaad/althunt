"""
Streamlit frontend for Altitude Huntsville Party Booking Assistant
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from dotenv import load_dotenv
from typing import List, Dict
import base64
import json

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Altitude Huntsville Party Booking",
    page_icon="🎉",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []

if "booking_created" not in st.session_state:
    st.session_state.booking_created = False

if "checkout_url" not in st.session_state:
    st.session_state.checkout_url = None

if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

if "is_listening" not in st.session_state:
    st.session_state.is_listening = False


def upload_file_to_backend(file) -> bool:
    """Upload file to backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{BACKEND_URL}/upload-file",
            files=files,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            st.session_state.uploaded_files.append({
                "filename": file.name,
                "file_id": data.get("file_id")
            })
            return True
        return False
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return False


def send_message(message: str) -> str:
    """Send message to backend API and get response"""
    try:
        print(f"\n📤 DEBUG - send_message() called with: '{message}'")
        print(f"📤 DEBUG - Message length: {len(message)}")
        
        # Prepare conversation history
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ]
        print(f"📤 DEBUG - Conversation history length: {len(history)}")
        print(f"📤 DEBUG - Backend URL: {BACKEND_URL}/chat")
        
        print(f"📡 DEBUG - Sending POST request to backend...")
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "conversation_history": history
            },
            timeout=60  # Increased timeout for Grok API calls
        )
        
        print(f"📡 DEBUG - Response status code: {response.status_code}")
        print(f"📡 DEBUG - Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        print(f"📡 DEBUG - Parsing JSON response...")
        data = response.json()
        print(f"📡 DEBUG - Response data keys: {list(data.keys())}")
        print(f"📡 DEBUG - Response text (first 200 chars): {data.get('response', '')[:200]}")
        
        # Check if booking was created
        if data.get("booking_created"):
            st.session_state.booking_created = True
            if data.get("checkout_url"):
                st.session_state.checkout_url = data.get("checkout_url")
        
        response_text = data.get("response", "I'm sorry, I couldn't process that request.")
        print(f"✅ DEBUG - Returning response text (length: {len(response_text)}): {response_text[:100]}...")
        return response_text
    except requests.exceptions.Timeout as e:
        error_msg = f"❌ Request timed out. The backend may be slow or unresponsive. Error: {str(e)}"
        print(f"❌ DEBUG - Timeout error: {error_msg}")
        return error_msg
    except requests.exceptions.ConnectionError as e:
        error_msg = f"❌ Cannot connect to backend at {BACKEND_URL}. Is the backend running? Error: {str(e)}"
        print(f"❌ DEBUG - Connection error: {error_msg}")
        return error_msg
    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ HTTP error from backend: {response.status_code} - {response.text[:200]}"
        print(f"❌ DEBUG - HTTP error: {error_msg}")
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error connecting to the booking system. Please make sure the backend is running. Error: {str(e)}"
        print(f"❌ DEBUG - Request exception: {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        print(f"❌ DEBUG - Unexpected error: {error_msg}")
        import traceback
        print(f"❌ DEBUG - Traceback:\n{traceback.format_exc()}")
        return error_msg


# Main UI
st.title("🎉 Altitude Huntsville Party Booking Assistant")
st.markdown("**Your friendly AI assistant for planning amazing birthday parties!**")

# Sidebar with package info and controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Voice mode toggle
    voice_mode = st.toggle("🎤 Voice Mode", value=st.session_state.voice_mode)
    st.session_state.voice_mode = voice_mode
    
    if voice_mode:
        st.info("🎤 Voice mode enabled! Use the voice controls below to speak with the AI.")
        st.markdown("---")
    
    # File upload section
    st.header("📄 Upload Documents")
    st.markdown("Upload waivers, park rules, or FAQs for the AI to reference")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'doc', 'docx', 'md'],
        help="Upload documents that the AI can search through"
    )
    
    if uploaded_file is not None:
        if st.button("Upload File"):
            with st.spinner("Uploading..."):
                if upload_file_to_backend(uploaded_file):
                    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                    st.rerun()
    
    # Show uploaded files
    if st.session_state.uploaded_files:
        st.markdown("**Uploaded Files:**")
        for file_info in st.session_state.uploaded_files:
            st.write(f"📄 {file_info['filename']}")
    
    st.markdown("---")
    st.header("📦 Party Packages")
    
    packages = {
        "Rookie": "$25/jumper",
        "All-Star": "$30/jumper",
        "MVP": "$35/jumper",
        "Glo Party": "$40/jumper"
    }
    
    for pkg, price in packages.items():
        with st.expander(f"{pkg} - {price}"):
            if pkg == "Rookie":
                st.write("Basic package with jump time, party host, and supplies")
            elif pkg == "All-Star":
                st.write("Everything in Rookie + pizza")
            elif pkg == "MVP":
                st.write("Everything in All-Star + arcade cards, gift, free pass")
            elif pkg == "Glo Party":
                st.write("Everything in MVP + glow lights, DJ. **Friday & Saturday only!**")
    
    st.markdown("---")
    st.markdown("**💡 Tip:** Ask me about packages, availability, or pricing!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show checkout URL if it's in the message
        if message["role"] == "assistant" and "checkout" in message["content"].lower():
            if st.session_state.checkout_url:
                st.markdown(f"[🔗 Complete Payment Here]({st.session_state.checkout_url})")

# Checkout URL banner (if booking created)
if st.session_state.booking_created and st.session_state.checkout_url:
    st.success(f"🎉 Booking created! [Click here to complete payment]({st.session_state.checkout_url})")

# Voice mode UI - Full voice-to-voice using Web Speech API
if st.session_state.voice_mode:
    st.markdown("### 🎤 Voice-to-Voice Mode")
    st.info("💡 **Click 'Start Listening', speak your message, then click 'Send'. The AI will respond and speak automatically!**")
    
    # Debug info
    with st.expander("🔍 Debug Info"):
        st.write(f"Voice mode active: {st.session_state.voice_mode}")
        st.write(f"Last voice input: {st.session_state.get('last_voice_input', 'None')}")
        st.write(f"Voice input in session: {st.session_state.get('voice_input', 'None')}")
        st.write(f"voice_input_to_send: {st.session_state.get('voice_input_to_send', 'None')}")
        st.write(f"voice_transcript: {st.session_state.get('voice_transcript', 'None')}")
        st.write(f"Total messages: {len(st.session_state.messages)}")
        
        # Show recent messages
        if st.session_state.messages:
            st.write("**Recent Messages:**")
            for i, msg in enumerate(st.session_state.messages[-5:]):  # Last 5 messages
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                st.write(f"{role_emoji} {msg['role']}: {msg['content'][:100]}...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Backend Connection"):
                try:
                    print(f"\n🧪 DEBUG - Testing backend connection...")
                    test_response = send_message("What are the party packages?")
                    st.success(f"✅ Backend working! Response: {test_response[:100]}...")
                    print(f"✅ DEBUG - Test successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Backend error: {str(e)}")
                    print(f"❌ DEBUG - Test failed: {str(e)}")
        
        with col2:
            if st.button("Clear Voice State"):
                st.session_state.last_voice_input = ""
                st.session_state.voice_input = ""
                st.session_state.voice_input_to_send = ""
                st.session_state.voice_transcript = ""
                st.success("✅ Voice state cleared!")
                st.rerun()
        
        # Show query params
        if st.query_params:
            st.write("**Current URL Query Params:**")
            st.json(dict(st.query_params))
    
    # Use Streamlit buttons instead of HTML buttons for better reliability
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_clicked = st.button("🎙️ Start Listening", key="voice_start_btn", use_container_width=True, type="primary")
        if start_clicked:
            st.session_state.is_listening = True
            st.rerun()
    
    with col2:
        stop_clicked = st.button("⏹️ Stop Listening", key="voice_stop_btn", use_container_width=True, disabled=not st.session_state.is_listening)
        if stop_clicked:
            st.session_state.is_listening = False
            st.rerun()
    
    # Check for transcript from URL (when Send button redirects with transcript)
    send_transcript_from_url = st.query_params.get("send_transcript", "")
    if send_transcript_from_url:
        print(f"✅ DEBUG - Received transcript from Send button URL: '{send_transcript_from_url}'")
        # Store it immediately in session state
        st.session_state.voice_transcript = send_transcript_from_url
        st.session_state.voice_input = send_transcript_from_url
        st.session_state.voice_input_to_send = send_transcript_from_url
        # Clear URL param
        st.query_params.clear()
    
    # Also check for voice_transcript from URL (when voice recognition updates via URL)
    voice_transcript_from_url = st.query_params.get("voice_transcript", "")
    if voice_transcript_from_url and voice_transcript_from_url != "Your speech will appear here as you talk...":
        print(f"🔄 DEBUG - Received transcript from voice recognition URL: '{voice_transcript_from_url}'")
        st.session_state.voice_transcript = voice_transcript_from_url
        # Clear the sync param but keep transcript
        if "_sync" in st.query_params:
            st.query_params.pop("_sync")
        if "_restore" in st.query_params:
            st.query_params.pop("_restore")
    
    # Voice transcript display - use session state to prevent reset
    current_transcript = st.session_state.get("voice_transcript", "Your speech will appear here as you talk...")
    
    with col3:
        # Always enable the button - we'll check for transcript when clicked
        send_clicked = st.button("📤 Send & Get Voice Response", key="voice_send_btn", use_container_width=True, disabled=False)
        
        # JavaScript to read transcript directly from textarea and send via URL
        if send_clicked:
            read_and_send_js = """
            <script>
            console.log('📤 DEBUG - Send button clicked, reading transcript...');
            
            // Try multiple sources in priority order:
            // 1. sessionStorage (most reliable - updated by voice recognition)
            // 2. textarea DOM element
            // 3. Any other stored value
            
            let transcript = '';
            
            // First, try sessionStorage (this is updated by the voice recognition component)
            const storedTranscript = sessionStorage.getItem('streamlit_voice_transcript');
            if (storedTranscript && storedTranscript.trim() && storedTranscript !== 'Your speech will appear here as you talk...') {
                transcript = storedTranscript.trim();
                console.log('✅ DEBUG - Found transcript in sessionStorage:', transcript);
            } else {
                // Fallback: try to read from textarea
                const textarea = window.parent.document.querySelector('textarea[aria-label*="Voice Transcript"]');
                if (textarea) {
                    const textareaValue = textarea.value.trim();
                    if (textareaValue && textareaValue !== 'Your speech will appear here as you talk...') {
                        transcript = textareaValue;
                        console.log('✅ DEBUG - Found transcript in textarea:', transcript);
                        // Also store it in sessionStorage for next time
                        sessionStorage.setItem('streamlit_voice_transcript', transcript);
                    } else {
                        console.warn('⚠️ DEBUG - Textarea value is empty or placeholder:', textareaValue);
                    }
                } else {
                    console.warn('⚠️ DEBUG - Textarea not found in DOM');
                }
            }
            
            // Check if we have a valid transcript
            if (transcript && transcript.length > 0) {
                console.log('✅ DEBUG - Valid transcript found:', transcript);
                console.log('✅ DEBUG - Transcript length:', transcript.length);
                
                // IMPORTANT: Redirect the PARENT window (Streamlit), not the iframe
                // Get the parent window's URL, not the iframe's URL
                try {
                    const parentUrl = window.parent.location.href.split('?')[0].split('#')[0];
                    const newUrl = parentUrl + '?send_transcript=' + encodeURIComponent(transcript) + '&_send=' + Date.now();
                    console.log('🔄 DEBUG - Redirecting PARENT window with transcript:', newUrl);
                    window.parent.location.href = newUrl;
                } catch(e) {
                    console.error('❌ DEBUG - Error redirecting parent:', e);
                    // Fallback: try using postMessage
                    console.log('🔄 DEBUG - Trying postMessage fallback...');
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: transcript
                    }, '*');
                }
            } else {
                console.error('❌ DEBUG - No valid transcript found!');
                console.error('❌ DEBUG - sessionStorage value:', sessionStorage.getItem('streamlit_voice_transcript'));
                console.error('❌ DEBUG - Textarea element:', window.parent.document.querySelector('textarea[aria-label*="Voice Transcript"]'));
                alert('No speech detected in transcript box.\\n\\nPlease:\\n1. Click "Start Listening"\\n2. Speak clearly\\n3. Wait for your words to appear in the transcript box\\n4. Then click Send again\\n\\nIf you see your text but still get this error, check the browser console (F12) for details.');
            }
            </script>
            """
            components.html(read_and_send_js, height=0)
            
            # The transcript will be processed on the next rerun via URL parameter
            # (handled at the top of the voice mode section)
    
    # Voice status display
    status_color = "#4CAF50" if st.session_state.is_listening else "#666"
    status_text = "🎤 Listening... Speak now!" if st.session_state.is_listening else "⏸️ Ready - Click Start to begin"
    st.markdown(f"""
    <div style="padding: 15px; background: rgba(76, 175, 80, 0.1); border-radius: 8px; margin: 10px 0; text-align: center;">
        <strong style="color: {status_color}; font-size: 18px;">{status_text}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice transcript display (using current_transcript defined above)
    # IMPORTANT: This uses session state, so it won't reset on rerun
    st.text_area(
        "🎙️ Voice Transcript",
        value=current_transcript,
        key="voice_transcript_display",
        height=120,
        disabled=True,
        label_visibility="visible"
    )
    
    # Self-contained voice component with JavaScript for speech recognition
    voice_component_html = f"""
    <div id="voice-recognition-container">
    <script>
    (function() {{
        let recognition = null;
        let finalTranscript = '';
        let isListening = {str(st.session_state.is_listening).lower()};
        
        function initSpeechRecognition() {{
            console.log('🔧 DEBUG - Initializing speech recognition...');
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                console.error('❌ DEBUG - Speech recognition not supported');
                return false;
            }}
            console.log('✅ DEBUG - Speech recognition API available');
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {{
                isListening = true;
                finalTranscript = '';
                console.log('🎤 DEBUG - Voice recognition started');
                console.log('🎤 DEBUG - isListening set to:', isListening);
                // Update Streamlit via postMessage
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: 'listening_started'
                }}, '*');
            }};
            
            recognition.onresult = function(event) {{
                let interimTranscript = '';
                let newFinal = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {{
                        newFinal += transcript + ' ';
                    }} else {{
                        interimTranscript += transcript;
                    }}
                }}
                
                if (newFinal) {{
                    finalTranscript += newFinal;
                }}
                
                const displayText = (finalTranscript + interimTranscript).trim();
                console.log('Voice recognition result:', displayText);
                
                // Store in sessionStorage and update Streamlit immediately
                if (displayText) {{
                    sessionStorage.setItem('streamlit_voice_transcript', displayText);
                    console.log('✅ Stored transcript in sessionStorage:', displayText);
                    
                    // Update textarea directly with multiple events
                    const textarea = window.parent.document.querySelector('textarea[aria-label*="Voice Transcript"]');
                    if (textarea) {{
                        textarea.value = displayText;
                        // Trigger multiple events to ensure Streamlit picks it up
                        textarea.dispatchEvent(new Event('input', {{bubbles: true}}));
                        textarea.dispatchEvent(new Event('change', {{bubbles: true}}));
                        textarea.dispatchEvent(new KeyboardEvent('keyup', {{bubbles: true}}));
                        console.log('✅ Updated textarea with:', displayText);
                    }} else {{
                        console.warn('⚠️ Textarea not found!');
                    }}
                    
                    // Update Streamlit via URL (but only if transcript changed significantly)
                    // Don't update on every small change to avoid too many reloads
                    try {{
                        const baseUrl = window.parent.location.href.split('?')[0].split('#')[0];
                        const currentUrl = window.parent.location.href;
                        // Only update URL if transcript is substantial and URL doesn't already have it
                        if (displayText.length > 5 && !currentUrl.includes('voice_transcript=')) {{
                            const timestamp = Date.now();
                            const newUrl = baseUrl + '?voice_transcript=' + encodeURIComponent(displayText) + '&_sync=' + timestamp;
                            console.log('🔄 Updating URL to sync transcript:', newUrl);
                            window.parent.location.href = newUrl;
                        }}
                    }} catch(err) {{
                        console.error('❌ Error updating URL:', err);
                    }}
                }}
            }};
            
            recognition.onerror = function(event) {{
                console.error('❌ DEBUG - Speech recognition error:', event.error);
                console.error('❌ DEBUG - Error details:', event);
                isListening = false;
                
                if (event.error === 'not-allowed') {{
                    console.error('❌ DEBUG - Microphone permission denied');
                    alert('Microphone permission denied. Please allow microphone access and try again.');
                }} else if (event.error === 'no-speech') {{
                    console.log('⚠️ DEBUG - No speech detected (this is normal if you haven\'t spoken yet)');
                }} else {{
                    console.error('❌ DEBUG - Voice recognition error:', event.error);
                }}
            }};
            
            recognition.onend = function() {{
                console.log('🛑 DEBUG - Recognition ended. isListening:', isListening);
                if (isListening) {{
                    // Auto-restart if still listening
                    try {{
                        console.log('🔄 DEBUG - Auto-restarting recognition...');
                        recognition.start();
                    }} catch(e) {{
                        console.error('❌ DEBUG - Auto-restart failed:', e);
                    }}
                }} else {{
                    console.log('✅ DEBUG - Recognition stopped (not listening)');
                }}
            }};
            
            return true;
        }}
        
        // Start recognition if listening state is true
        console.log('🔍 DEBUG - Initial state check. isListening:', isListening);
        if (isListening) {{
            console.log('🚀 DEBUG - Starting recognition (isListening=true)');
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', function() {{
                    console.log('📄 DEBUG - DOM loaded, initializing recognition');
                    if (initSpeechRecognition()) {{
                        console.log('✅ DEBUG - Recognition initialized, starting...');
                        recognition.start();
                    }}
                }});
            }} else {{
                console.log('📄 DEBUG - DOM ready, initializing recognition');
                if (initSpeechRecognition()) {{
                    console.log('✅ DEBUG - Recognition initialized, starting...');
                    recognition.start();
                }}
            }}
        }} else {{
            console.log('⏸️ DEBUG - Not starting recognition (isListening=false)');
        }}
        
        // Listen for Streamlit button clicks via postMessage
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'start_listening') {{
                if (!recognition) {{
                    if (initSpeechRecognition()) {{
                        recognition.start();
                    }}
                }} else if (!isListening) {{
                    recognition.start();
                }}
            }} else if (event.data && event.data.type === 'stop_listening') {{
                isListening = false;
                if (recognition) {{
                    recognition.stop();
                }}
            }}
        }});
    }})();
    </script>
    </div>
    """
    
    # Start/stop voice recognition based on button clicks
    if start_clicked or st.session_state.is_listening:
        # Start voice recognition via JavaScript
        start_js = """
        <script>
        if (window.parent) {
            window.parent.postMessage({type: 'start_listening'}, '*');
        }
        // Also try direct initialization
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                if (transcript) {
                    sessionStorage.setItem('streamlit_voice_transcript', transcript);
                    // Update Streamlit
                    const textarea = window.parent.document.querySelector('textarea[aria-label*="Voice Transcript"]');
                    if (textarea) {
                        textarea.value = transcript;
                        textarea.dispatchEvent(new Event('input', {bubbles: true}));
                    }
                }
            };
            
            recognition.start();
            window.voiceRecognition = recognition;
        }
        </script>
        """
        components.html(start_js, height=0)
    
    if stop_clicked:
        stop_js = """
        <script>
        if (window.voiceRecognition) {
            window.voiceRecognition.stop();
        }
        if (window.parent) {
            window.parent.postMessage({type: 'stop_listening'}, '*');
        }
        </script>
        """
        components.html(stop_js, height=0)
    
    # Sync transcript from sessionStorage to textarea (lightweight, no URL redirects)
    sync_transcript_js = """
    <script>
    let lastSyncedTranscript = '';
    console.log('🔄 DEBUG - Starting transcript sync interval (every 500ms)');
    setInterval(function() {
        const transcript = sessionStorage.getItem('streamlit_voice_transcript');
        if (transcript && transcript !== lastSyncedTranscript && transcript !== 'Your speech will appear here as you talk...') {
            lastSyncedTranscript = transcript;
            console.log('📤 DEBUG - Syncing transcript to textarea:', transcript.substring(0, 50) + '...');
            
            // Update textarea directly (no URL redirects to avoid page reloads)
            const textarea = window.parent.document.querySelector('textarea[aria-label*="Voice Transcript"]');
            if (textarea && textarea.value !== transcript) {
                textarea.value = transcript;
                // Trigger events to update Streamlit
                textarea.dispatchEvent(new Event('input', {bubbles: true}));
                textarea.dispatchEvent(new Event('change', {bubbles: true}));
                console.log('✅ DEBUG - Textarea updated');
            }
        }
    }, 500);
    </script>
    """
    components.html(sync_transcript_js, height=0)
    
    # Update session state with transcript from URL (set by JavaScript)
    transcript_from_url = st.query_params.get("voice_transcript", "")
    if transcript_from_url:
        print(f"📥 DEBUG - Received transcript from URL: '{transcript_from_url}'")
        st.session_state.voice_transcript = transcript_from_url
        st.session_state.voice_input = transcript_from_url
        # Clear sync param but keep transcript
        if "_sync" in st.query_params:
            # Keep voice_transcript but remove _sync
            new_params = {k: v for k, v in st.query_params.items() if k != "_sync"}
            st.query_params.clear()
            for k, v in new_params.items():
                if k == "voice_transcript":
                    st.query_params["voice_transcript"] = v
    
    # Also update from text area if it changed (this is the most reliable)
    if current_transcript and current_transcript != "Your speech will appear here as you talk...":
        if current_transcript != st.session_state.get("voice_transcript", ""):
            print(f"📝 DEBUG - Updating transcript from textarea: '{current_transcript}'")
            st.session_state.voice_input = current_transcript
            st.session_state.voice_transcript = current_transcript
    
    # DEBUG: Show current state in expandable panel
    with st.expander("🔍 Debug Info - Voice Mode State", expanded=False):
        st.write("**Session State:**")
        st.json({
            "voice_transcript": st.session_state.get("voice_transcript", ""),
            "voice_input": st.session_state.get("voice_input", ""),
            "is_listening": st.session_state.get("is_listening", False),
            "voice_mode": st.session_state.get("voice_mode", False),
            "current_transcript": current_transcript,
            "transcript_from_url": transcript_from_url
        })
        st.write("**Query Params:**")
        st.json(dict(st.query_params))
        st.write("**Instructions:**")
        st.write("1. Open browser console (F12) → Console tab")
        st.write("2. Click 'Start Listening' and watch for '🎤 DEBUG' messages")
        st.write("3. Speak clearly and watch for 'Voice recognition result:' messages")
        st.write("4. Check if transcript appears in the textarea above")
        st.write("5. Click Send and check the debug output below")
        st.write("6. Check terminal/backend logs for Python DEBUG messages")
    
    components.html(voice_component_html, height=200)
    
    # Check for voice input from sessionStorage (via JavaScript)
    # We'll use a simple approach: check if there's a voice input waiting
    import json
    voice_input_js = """
    <script>
    const voiceInput = sessionStorage.getItem('streamlit_voice_input');
    if (voiceInput) {
        // Store it in a way Streamlit can access
        document.body.setAttribute('data-voice-input', voiceInput);
    }
    </script>
    """
    components.html(voice_input_js, height=0)
    
    # Check for voice_input_to_send FIRST (set when Send button is clicked with transcript)
    voice_input_to_send = st.session_state.get("voice_input_to_send", "")
    
    # DEBUG: Log the state before processing
    print(f"\n🔍 DEBUG - Voice input processing check:")
    print(f"  - voice_input_to_send: '{voice_input_to_send}'")
    print(f"  - voice_transcript: '{st.session_state.get('voice_transcript', '')}'")
    print(f"  - last_voice_input: '{st.session_state.get('last_voice_input', '')}'")
    print(f"  - voice_mode: {st.session_state.get('voice_mode', False)}")
    
    # Process voice input if provided (priority: voice_input_to_send)
    voice_input_to_process = voice_input_to_send.strip() if voice_input_to_send else ""
    
    # Also check voice_transcript as fallback
    if not voice_input_to_process:
        voice_transcript = st.session_state.get("voice_transcript", "")
        if voice_transcript and voice_transcript != "Your speech will appear here as you talk...":
            voice_input_to_process = voice_transcript.strip()
            print(f"  - Using voice_transcript as fallback: '{voice_input_to_process}'")
    
    if voice_input_to_process and voice_input_to_process != st.session_state.get("last_voice_input", ""):
        # Send the voice input as a message
        user_message = voice_input_to_process.strip()
        print(f"\n📤 DEBUG - Processing voice message to send to backend: '{user_message}'")
        st.session_state.last_voice_input = user_message
        st.session_state.voice_input = ""  # Clear from session state
        st.session_state.voice_text_input = ""  # Clear input field
        st.session_state.voice_input_to_send = ""  # Clear the send flag
        
        # IMPORTANT: Keep voice mode active after sending message
        st.session_state.voice_mode = True
        
        # Add to messages
        st.session_state.messages.append({"role": "user", "content": user_message})
        print(f"✅ DEBUG - Added user message to chat history. Total messages: {len(st.session_state.messages)}")
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    print(f"🤖 DEBUG - About to call send_message() with: '{user_message}'")
                    response = send_message(user_message)
                    print(f"🤖 DEBUG - send_message() returned: '{response[:100] if response else 'None'}...'")
                    
                    if response:
                        print(f"✅ DEBUG - Displaying response in chat")
                        st.markdown(response)
                        
                        # Auto-speak the response
                        tts_script = f"""
                        <script>
                        if ('speechSynthesis' in window) {{
                            window.speechSynthesis.cancel();
                            const utterance = new SpeechSynthesisUtterance({repr(response)});
                            utterance.rate = 1.0;
                            utterance.pitch = 1.0;
                            utterance.volume = 1.0;
                            utterance.lang = 'en-US';
                            setTimeout(() => {{ window.speechSynthesis.speak(utterance); }}, 500);
                        }}
                        </script>
                        """
                        components.html(tts_script, height=0)
                        print(f"✅ DEBUG - TTS script injected")
                    else:
                        error_msg = "No response from AI. Please check backend connection."
                        print(f"❌ DEBUG - {error_msg}")
                        st.error(error_msg)
                        response = "I'm sorry, I couldn't get a response. Please try again."
                except Exception as e:
                    error_msg = f"Error getting response: {str(e)}"
                    print(f"❌ DEBUG - Exception in voice mode response: {error_msg}")
                    import traceback
                    print(f"❌ DEBUG - Traceback:\n{traceback.format_exc()}")
                    st.error(error_msg)
                    response = error_msg
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Reset last_voice_input after processing so next voice input can be processed
        st.session_state.last_voice_input = ""
        st.rerun()
    
    # JavaScript to sync voice input from sessionStorage to URL (backup method)
    sync_js = """
    <script>
    // Check sessionStorage and move to URL if needed
    const voiceInput = sessionStorage.getItem('streamlit_voice_input');
    if (voiceInput && !window.location.href.includes('voice_input=')) {
        const currentUrl = window.location.href;
        const separator = currentUrl.includes('?') ? '&' : '?';
        window.location.href = currentUrl + separator + 'voice_input=' + encodeURIComponent(voiceInput);
        sessionStorage.removeItem('streamlit_voice_input');
    }
    </script>
    """
    components.html(sync_js, height=0)
    
    st.markdown("---")

# Handle voice input first (if in voice mode)
voice_prompt = None
if st.session_state.voice_mode and st.session_state.voice_input:
    voice_prompt = st.session_state.voice_input
    st.session_state.voice_input = ""  # Clear after use
    st.session_state.is_listening = False

# Chat input (text or voice)
if voice_prompt:
    prompt = voice_prompt
elif prompt := st.chat_input("How can I help with your party?"):
    pass  # Use the prompt from chat_input
else:
    prompt = None

if prompt:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = send_message(prompt)
            st.markdown(response)
            
            # If checkout URL is available, display it prominently
            if st.session_state.checkout_url and "checkout" in response.lower():
                st.markdown("---")
                st.markdown(f"### [🔗 Complete Your Payment Here]({st.session_state.checkout_url})")
            
            # Auto-speak response in voice mode
            if st.session_state.voice_mode and response:
                tts_script = f"""
                <script>
                if ('speechSynthesis' in window) {{
                    // Stop any ongoing speech
                    window.speechSynthesis.cancel();
                    
                    const utterance = new SpeechSynthesisUtterance({repr(response)});
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    utterance.lang = 'en-US';
                    
                    // Small delay to ensure smooth playback
                    setTimeout(() => {{
                        window.speechSynthesis.speak(utterance);
                    }}, 500);
                }}
                </script>
                """
                components.html(tts_script, height=0)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "Altitude Trampoline Park Huntsville | Powered by AI 🚀"
    "</div>",
    unsafe_allow_html=True
)

