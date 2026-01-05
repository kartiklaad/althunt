"""
FastAPI backend for party booking assistant
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

from backend.agent import create_agent_executor
from backend.roller_client import RollerClient
from backend.packages import PACKAGES
from backend.file_handler import FileHandler
from fastapi import UploadFile, File

# Load environment variables
load_dotenv()

app = FastAPI(title="Altitude Huntsville Party Booking API")

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    booking_created: bool = False
    checkout_url: Optional[str] = None


# Note: We create agent executor per request to maintain conversation state


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Altitude Huntsville Party Booking Assistant",
        "packages": list(PACKAGES.keys())
    }


@app.get("/packages")
async def get_packages():
    """Get all available party packages"""
    return {"packages": PACKAGES}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for conversing with the booking assistant
    """
    try:
        print(f"\n📥 DEBUG - Received chat request")
        print(f"📥 DEBUG - Message: '{request.message}'")
        print(f"📥 DEBUG - Message length: {len(request.message)}")
        print(f"📥 DEBUG - Conversation history length: {len(request.conversation_history or [])}")
        
        # Create agent executor with conversation history for memory
        conversation_history = request.conversation_history or []
        print(f"🔧 DEBUG - Creating agent executor...")
        agent_executor, chat_history = create_agent_executor(conversation_history=conversation_history)
        print(f"✅ DEBUG - Agent executor created. Chat history length: {len(chat_history)}")
        
        # Prepare input - AgentWrapper only needs "input"
        agent_input = {
            "input": request.message
        }
        print(f"🤖 DEBUG - Invoking agent with input: '{request.message[:100]}...'")
        
        # Invoke agent with user message
        result = agent_executor.invoke(agent_input)
        print(f"🤖 DEBUG - Agent returned result type: {type(result)}")
        print(f"🤖 DEBUG - Agent result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        response_text = result.get("output", "I'm sorry, I couldn't process that request.")
        print(f"✅ DEBUG - Extracted response text (length: {len(response_text)}): '{response_text[:200]}...'")
        
        # Check if booking was created (look for checkout URL in response)
        booking_created = "checkout" in response_text.lower() or "booking created" in response_text.lower()
        checkout_url = None
        
        if booking_created:
            # Try to extract checkout URL from response
            import re
            url_match = re.search(r'https?://[^\s]+', response_text)
            if url_match:
                checkout_url = url_match.group(0)
                print(f"✅ DEBUG - Found checkout URL: {checkout_url}")
        
        response_obj = ChatResponse(
            response=response_text,
            booking_created=booking_created,
            checkout_url=checkout_url
        )
        print(f"📤 DEBUG - Returning response (booking_created={booking_created})")
        return response_obj
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Error in chat endpoint: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"Full traceback:\n{error_details}")
        # Log to file for debugging
        with open("/tmp/backend_errors.log", "a") as f:
            f.write(f"\n{error_msg}\n{error_details}\n")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat: {str(e)}"
        )


@app.get("/availability")
async def check_availability(
    date: str,
    package: str,
    jumpers: int
):
    """Direct endpoint to check availability"""
    roller = RollerClient()
    result = roller.check_availability(
        date=date,
        package_name=package,
        num_jumpers=jumpers
    )
    return result


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for document search (waivers, park rules, etc.)
    """
    try:
        file_handler = FileHandler()
        content = await file.read()
        file_id = file_handler.upload_file_content(
            content=content,
            filename=file.filename
        )
        
        if file_id:
            return {
                "success": True,
                "file_id": file_id,
                "filename": file.filename,
                "message": f"File '{file.filename}' uploaded successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/files")
async def list_files():
    """List all uploaded files"""
    try:
        file_handler = FileHandler()
        files = file_handler.list_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@app.post("/webhook/roller")
async def roller_webhook(payload: Dict[str, Any]):
    """
    Webhook endpoint for Roller payment confirmations
    This would be called by Roller when payment is completed
    """
    # Handle webhook from Roller
    event_type = payload.get("event")
    booking_id = payload.get("booking_id")
    
    if event_type == "payment.success":
        # Send confirmation email
        # Update booking status
        return {"status": "processed", "booking_id": booking_id}
    
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000)))

