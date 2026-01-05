"""
LangChain agent setup for party booking assistant
"""

import os
from typing import Dict, Any, List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from openai import OpenAI

from backend.roller_client import RollerClient
from backend.packages import PACKAGES, get_package_summary, calculate_total_price
from backend.file_handler import FileHandler
from datetime import datetime


# Initialize Roller client
roller_client = RollerClient()

# Initialize file handler for document search (optional)
file_handler = None
try:
    file_handler = FileHandler()
except Exception as e:
    # File handler is optional - will be None if XAI_API_KEY not set or other error
    pass


@tool
def check_availability(date: str, package_name: str, num_jumpers: int) -> str:
    """
    Check if a party slot is available for a specific date, package, and number of jumpers.
    
    Args:
        date: Date in YYYY-MM-DD format (e.g., "2024-01-18")
        package_name: One of: Rookie, All-Star, MVP, Glo Party
        num_jumpers: Number of jumpers (minimum 10)
    
    Returns:
        String describing availability and available time slots
    """
    # Validate package
    if package_name not in PACKAGES:
        return f"Error: '{package_name}' is not a valid package. Available packages: {', '.join(PACKAGES.keys())}"
    
    # Validate minimum jumpers
    min_jumpers = PACKAGES[package_name]["min_jumpers"]
    if num_jumpers < min_jumpers:
        return f"Error: Minimum {min_jumpers} jumpers required for {package_name} package. You specified {num_jumpers}."
    
    # Check Glo Party restrictions
    if package_name == "Glo Party":
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            if day_name not in ["Friday", "Saturday"]:
                return f"Error: Glo Party is only available on Friday and Saturday nights. {day_name} is not available."
        except ValueError:
            return f"Error: Invalid date format. Please use YYYY-MM-DD format."
    
    # Check availability via Roller API
    result = roller_client.check_availability(
        date=date,
        package_name=package_name,
        num_jumpers=num_jumpers
    )
    
    return result["message"]


@tool
def get_package_info(package_name: str) -> str:
    """
    Get detailed information about a party package.
    
    Args:
        package_name: One of: Rookie, All-Star, MVP, Glo Party
    
    Returns:
        Detailed package information
    """
    if package_name not in PACKAGES:
        return f"Error: '{package_name}' is not a valid package. Available packages: {', '.join(PACKAGES.keys())}"
    
    return get_package_summary(package_name)


@tool
def calculate_price(package_name: str, num_jumpers: int, private_room: bool = False) -> str:
    """
    Calculate the total price for a party booking.
    
    Args:
        package_name: One of: Rookie, All-Star, MVP, Glo Party
        num_jumpers: Number of jumpers
        private_room: Whether to include private room upgrade (default: False)
    
    Returns:
        String with price breakdown
    """
    result = calculate_total_price(package_name, num_jumpers, private_room)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    breakdown = result["breakdown"]
    return f"Price Breakdown:\n{breakdown['package_price']}\nPrivate Room: {breakdown['room_upgrade']}\nTotal: {breakdown['total']}"


@tool
def create_booking(
    package_name: str,
    num_jumpers: int,
    date: str,
    time_slot: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str = "",
    birthday_child_name: str = "",
    private_room: bool = False
) -> str:
    """
    Create a party booking and get the payment checkout link.
    Only call this when the user has confirmed they want to proceed with booking.
    
    Args:
        package_name: One of: Rookie, All-Star, MVP, Glo Party
        num_jumpers: Number of jumpers
        date: Date in YYYY-MM-DD format
        time_slot: Time slot (e.g., "2:00 PM", "4:00 PM")
        customer_name: Name of the person booking
        customer_email: Email address
        customer_phone: Phone number (optional)
        birthday_child_name: Name of the birthday child (optional)
        private_room: Whether to include private room upgrade
    
    Returns:
        String with booking confirmation and checkout URL
    """
    result = roller_client.create_booking(
        package_name=package_name,
        num_jumpers=num_jumpers,
        date=date,
        time_slot=time_slot,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        birthday_child_name=birthday_child_name,
        private_room=private_room
    )
    
    if result["success"]:
        checkout_url = result["checkout_url"]
        booking_id = result["booking_id"]
        return f"""✅ Booking created successfully!

Booking ID: {booking_id}

Please complete your payment to secure your party slot:
{checkout_url}

After payment, you'll receive a confirmation email with all the details, waiver links, and instructions."""
    else:
        return f"❌ Error creating booking: {result.get('error', 'Unknown error')}"


@tool
def search_documents(query: str) -> str:
    """
    Search uploaded documents (waivers, park rules, FAQs, etc.) for information.
    
    Args:
        query: The question or search query
    
    Returns:
        Relevant information from uploaded documents
    """
    if not file_handler:
        return "Document search is not available. Please upload documents first."
    
    try:
        # List uploaded files
        files = file_handler.list_files()
        if not files:
            return "No documents have been uploaded yet. Upload waivers, park rules, or FAQs to enable document search."
        
        # Search through uploaded files
        results = []
        for file_info in files:
            try:
                content = file_handler.get_file_content(file_info["id"])
                if content and query.lower() in content.lower():
                    # Extract relevant section (simplified - in production, use better search)
                    lines = content.split('\n')
                    relevant_lines = [line for line in lines if query.lower() in line.lower()]
                    if relevant_lines:
                        results.append(f"From {file_info['filename']}:\n" + "\n".join(relevant_lines[:5]))
            except Exception as e:
                continue
        
        if results:
            return "\n\n".join(results)
        else:
            return f"I couldn't find information about '{query}' in the uploaded documents. Please ask me about party packages, pricing, or availability instead!"
    except Exception as e:
        return f"Error searching documents: {str(e)}"


def create_agent_executor(conversation_history: list = None):
    """
    Create and configure the LangChain agent with conversation memory
    
    Args:
        conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        Tuple of (agent_executor, chat_history_messages)
    """
    
    # Convert conversation history to LangChain message format
    chat_history = []
    if conversation_history:
        for msg in conversation_history:
            # Handle both dict and Pydantic ChatMessage objects
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
            else:
                # Pydantic model - access as attributes
                role = msg.role
                content = msg.content
            
            if role == "user":
                chat_history.append(HumanMessage(content=content))
            elif role == "assistant":
                chat_history.append(AIMessage(content=content))
    
    # System prompt with package information - super friendly and enthusiastic!
    system_prompt = """You are a warm, enthusiastic, and super friendly party booking assistant for Altitude Trampoline Park in Huntsville, AL! 🎉🎈

Your mission is to help families plan absolutely amazing birthday parties! Always be excited, helpful, and make the booking process feel fun and easy. Sound genuinely enthusiastic about helping them celebrate!

**Available Party Packages (Updated Jan 2026):**

1. **Rookie** - $25/jumper (minimum 10 jumpers)
   - Includes: Jump time, table time, party host, setup & cleanup, basic party supplies (plates/napkins/utensils/tablecloth), Altitude grip socks
   - Does NOT include: Pizza, soda, arcade cards, birthday gift, or free return pass
   - Private room upgrade: +$5 per jumper
   - Perfect for: Families who want to bring their own food and keep it simple!

2. **All-Star** - $30/jumper (minimum 10 jumpers)
   - Everything in Rookie PLUS large pizza per 5 jumpers
   - Private room upgrade: +$5 per jumper
   - Perfect for: Families who want pizza included - one less thing to worry about!

3. **MVP** - $35/jumper (minimum 10 jumpers)
   - Everything in All-Star PLUS arcade card per jumper
   - Private room upgrade: +$5 per jumper
   - Perfect for: Families who want the full experience with arcade fun!

4. **Glo Party** - $40/jumper (minimum 10 jumpers)
   - Everything in MVP PLUS gift for birthday child
   - 3 hours total party time (longer celebration!)
   - Glow lights and DJ atmosphere for an epic party vibe
   - Private room upgrade: +$5 per jumper
   - ⚠️ **CRITICAL: ONLY AVAILABLE FRIDAY & SATURDAY NIGHTS**
   - Perfect for: The ultimate birthday celebration with glow lights and music!

**Important Booking Rules:**
- All packages require minimum 10 jumpers
- Private room upgrade is $5 per jumper for ALL packages
- Glo Party is STRICTLY Friday and Saturday nights only - enforce this!
- Always check availability before confirming any booking
- Never create a booking unless the user explicitly confirms they're ready
- Always calculate and clearly show the total price before asking for confirmation

Your goal is to help customers book amazing birthday parties! Be warm, conversational, and helpful.

**Available Party Packages:**

1. **Rookie** - $25/jumper (min 10 jumpers)
   - 2 hours jump time + 2 hours table time
   - Includes: Jump time, party host, basic party supplies, grip socks, soda
   - Private room: Flat $100 fee
   - Basic package – no food included

2. **All-Star** - $30/jumper (min 10 jumpers)
   - Everything in Rookie PLUS large pizza per 5 jumpers
   - Private room: Flat $50 fee

3. **MVP** - $35/jumper (min 10 jumpers)
   - Everything in All-Star PLUS arcade card per jumper, birthday gift, free jump pass for birthday child
   - Private room: $5 per jumper

4. **Glo Party** - $40/jumper (min 10 jumpers)
   - Everything in MVP PLUS glow lights, DJ atmosphere
   - 3 hours jump time (longer!)
   - ⚠️ **ONLY AVAILABLE FRIDAY & SATURDAY NIGHTS**
   - Private room: $5 per jumper

**Your Conversation Style:**
- Be warm, enthusiastic, and genuinely excited about helping plan their party!
- Use emojis naturally (🎉🎈🎂) to keep it fun
- Explain packages clearly and highlight what makes each one special
- Always sound excited when they choose a package - "That's an awesome choice!"
- Make families feel confident and excited about their booking

**Your Conversation Flow:**

1. **Greet warmly and enthusiastically**: "Hi! Welcome to Altitude Trampoline Park in Huntsville! 🎉 I'm so excited to help you plan an amazing birthday party! Let's make this celebration unforgettable!"

2. **Ask about the party with genuine interest**: Get information about:
   - Birthday child's age (be excited about their age!)
   - Rough number of guests
   - Any preferences (pizza, arcade, glow nights, etc.)
   - What kind of celebration they're envisioning

3. **Explain packages with enthusiasm**: Use the get_package_info tool when asked. Highlight what makes each package special and help them choose the perfect fit!

4. **Gather booking details clearly**:
   - Exact number of jumpers (remind them minimum is 10)
   - Preferred date (YYYY-MM-DD format) - double check Glo Party is Friday/Saturday!
   - Preferred time slot
   - Package choice (celebrate their choice!)
   - Private room upgrade? (explain it's $5 per jumper for all packages)
   - Birthday child's name (use their name to personalize!)
   - Customer contact info (name, email, phone)

5. **Check availability**: Always use check_availability before confirming. Be clear about:
   - Validating Glo Party is only Friday/Saturday (strictly enforce this!)
   - Verifying date format is correct
   - Confirming minimum jumpers requirement

6. **Calculate price clearly**: Use calculate_price to show a clear, easy-to-understand breakdown. Make sure they see exactly what they're paying for!

7. **Confirm booking with excitement**: When user says yes/ready to book:
   - Use create_booking tool with all the details
   - Present the checkout URL clearly and prominently
   - Remind them they'll get a confirmation email after payment
   - End with excitement: "We can't wait to celebrate with you!"

**Tools Available:**
- check_availability: Check if slots are available for a date/package
- get_package_info: Get detailed information about any package
- calculate_price: Calculate total cost with breakdown
- create_booking: Create the booking and get payment link (ONLY when user explicitly confirms)
- search_documents: Search uploaded documents (waivers, rules, FAQs) if user asks about policies, requirements, etc.

Remember: You're helping families create amazing memories! Be enthusiastic, clear, and make the whole process feel fun and easy! 🎈🎂✨"""
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Initialize LLM using OpenAI-compatible client for xAI Grok
    # xAI API is compatible with OpenAI SDK, just change base_url
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        raise ValueError("XAI_API_KEY not found in environment variables. Please set it in your .env file.")
    
    # Use OpenAI-compatible client with xAI base URL
    from langchain_openai import ChatOpenAI
    
    # Use Grok model - grok-3 is the latest (grok-beta was deprecated)
    # For best tool calling: grok-3 or grok-2-1212
    model_name = os.getenv("XAI_MODEL", "grok-3")  # Default to grok-3 (grok-beta deprecated)
    
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1"
    )
    
    # Define tools (include document search if file handler is available)
    tools = [check_availability, get_package_info, calculate_price, create_booking]
    if file_handler:
        tools.append(search_documents)
    
    # Create agent using new LangChain 1.2 API
    # create_agent returns a compiled graph that can be invoked directly
    agent_graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        debug=True
    )
    
    # Wrap in a simple executor-like interface for compatibility
    class AgentWrapper:
        def __init__(self, graph, chat_history):
            self.graph = graph
            self.chat_history = chat_history
        
        def invoke(self, input_dict):
            try:
                # Prepare input for the new agent API
                messages = self.chat_history.copy()
                messages.append(HumanMessage(content=input_dict["input"]))
                
                # Invoke the agent graph
                result = self.graph.invoke({
                    "messages": messages
                })
                
                # Extract the response - handle different result formats
                output = None
                if isinstance(result, dict):
                    if "messages" in result and result["messages"]:
                        # Find the last AI message (should be the response)
                        messages_list = result["messages"]
                        # Get the last message which should be the AI response
                        last_msg = messages_list[-1]
                        
                        # Try to get content from the message
                        if hasattr(last_msg, 'content'):
                            output = last_msg.content
                        elif isinstance(last_msg, dict) and 'content' in last_msg:
                            output = last_msg['content']
                        else:
                            # Fallback: convert to string
                            output = str(last_msg)
                    elif "output" in result:
                        output = result["output"]
                    else:
                        # Try to find any message-like content
                        output = str(result)
                elif hasattr(result, 'content'):
                    # Direct message object
                    output = result.content
                else:
                    output = str(result)
                
                if output is None or output == "":
                    output = "I'm sorry, I couldn't generate a response. Please try again."
                
                return {"output": output}
            except Exception as e:
                import traceback
                error_msg = f"Error in agent invoke: {str(e)}"
                print(f"❌ {error_msg}")
                print(traceback.format_exc())
                return {"output": f"I encountered an error: {str(e)}. Please try again."}
    
    executor = AgentWrapper(agent_graph, chat_history)
    
    return executor, chat_history

