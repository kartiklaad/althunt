"""
Voice handler for Grok Voice Agent API (WebSocket-based, OpenAI Realtime compatible)
"""

import os
import json
import asyncio
import websockets
from typing import Optional, Callable
from openai import OpenAI


class VoiceHandler:
    """Handle voice interactions using Grok Voice Agent API"""
    
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found in environment variables")
        
        # Grok Voice uses OpenAI Realtime API compatible endpoint
        self.base_url = "https://api.x.ai/v1"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Voice options
        self.voices = {
            "Ara": "Ara - Friendly, warm female voice",
            "Rex": "Rex - Energetic, enthusiastic male voice"
        }
        self.current_voice = "Ara"  # Default friendly voice
    
    async def create_voice_session(
        self,
        voice: str = "Ara",
        on_audio: Optional[Callable] = None,
        on_text: Optional[Callable] = None
    ):
        """
        Create a WebSocket connection for voice interaction
        
        Args:
            voice: Voice to use ("Ara" or "Rex")
            on_audio: Callback for received audio data
            on_text: Callback for transcribed text
        
        Returns:
            WebSocket connection
        """
        # Grok Voice API WebSocket endpoint (OpenAI Realtime compatible)
        ws_url = f"wss://api.x.ai/v1/realtime?model=grok-2-1212"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key
        }
        
        try:
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                # Send session configuration
                config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": "You are a warm, enthusiastic party booking assistant for Altitude Trampoline Park in Huntsville, AL. Be friendly and helpful!",
                        "voice": voice,
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16"
                    }
                }
                await websocket.send(json.dumps(config))
                
                # Handle messages
                async for message in websocket:
                    data = json.loads(message)
                    
                    if data.get("type") == "response.audio.delta":
                        # Audio data received
                        if on_audio:
                            on_audio(data.get("delta"))
                    
                    elif data.get("type") == "response.text.delta":
                        # Text transcription received
                        if on_text:
                            on_text(data.get("delta"))
                    
                    elif data.get("type") == "response.done":
                        # Response complete
                        break
        
        except Exception as e:
            print(f"Error in voice session: {str(e)}")
            raise
    
    def get_available_voices(self) -> dict:
        """Get available voice options"""
        return self.voices
    
    def set_voice(self, voice: str):
        """Set the voice to use"""
        if voice in self.voices:
            self.current_voice = voice
        else:
            raise ValueError(f"Voice '{voice}' not available. Choose from: {list(self.voices.keys())}")

