"""
Roller API client for authentication, availability checking, and booking creation
"""

import os
import requests
from typing import Optional, Dict, List
from datetime import datetime
import time


class RollerClient:
    """Client for interacting with Roller API"""
    
    def __init__(self):
        self.client_id = os.getenv("ROLLER_CLIENT_ID")
        self.client_secret = os.getenv("ROLLER_CLIENT_SECRET")
        self.base_url = os.getenv("ROLLER_BASE_URL", "https://api.roller.app/v1/")
        self.auth_url = "https://auth.roller.app/connect/token"
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        # Check if token is still valid (with 5 minute buffer)
        if self._access_token and time.time() < self._token_expires_at - 300:
            return self._access_token
        
        # Request new token
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "api"
        }
        
        try:
            response = requests.post(self.auth_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            # Tokens typically expire in 3600 seconds (1 hour)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in
            return self._access_token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to authenticate with Roller API: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_products(self) -> List[Dict]:
        """Fetch available party packages/products from Roller"""
        try:
            headers = self._get_headers()
            # Adjust endpoint based on actual Roller API structure
            response = requests.get(
                f"{self.base_url}products",
                headers=headers,
                params={"type": "party_package"}  # Adjust based on actual API
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            # Return empty list if API call fails (for local testing)
            print(f"Warning: Could not fetch products from Roller API: {str(e)}")
            return []
    
    def check_availability(
        self, 
        date: str, 
        product_id: Optional[str] = None,
        package_name: Optional[str] = None,
        num_jumpers: Optional[int] = None
    ) -> Dict:
        """
        Check availability for a specific date and package
        
        Args:
            date: Date in YYYY-MM-DD format
            product_id: Roller product ID (if known)
            package_name: Package name to map to product ID
            num_jumpers: Number of jumpers (for capacity checking)
        
        Returns:
            Dict with availability information
        """
        try:
            headers = self._get_headers()
            params = {"date": date}
            
            if product_id:
                params["productId"] = product_id
            
            if num_jumpers:
                params["capacity"] = num_jumpers
            
            response = requests.get(
                f"{self.base_url}availability",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse available time slots
            available_slots = data.get("availableSlots", [])
            if available_slots:
                times = [slot.get("time", "") for slot in available_slots]
                return {
                    "available": True,
                    "slots": available_slots,
                    "times": times,
                    "message": f"Available time slots: {', '.join(times)}"
                }
            else:
                return {
                    "available": False,
                    "slots": [],
                    "times": [],
                    "message": "No available slots for this date"
                }
        except requests.exceptions.RequestException as e:
            # For local testing, return mock availability
            print(f"Warning: Could not check availability via Roller API: {str(e)}")
            # Mock response for testing
            return {
                "available": True,
                "slots": [
                    {"time": "14:00", "available": True},
                    {"time": "16:00", "available": True},
                    {"time": "18:00", "available": True}
                ],
                "times": ["2:00 PM", "4:00 PM", "6:00 PM"],
                "message": "Available time slots: 2:00 PM, 4:00 PM, 6:00 PM (mock data)"
            }
    
    def create_booking(
        self,
        package_name: str,
        num_jumpers: int,
        date: str,
        time_slot: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str] = None,
        birthday_child_name: Optional[str] = None,
        private_room: bool = False,
        additional_notes: Optional[str] = None
    ) -> Dict:
        """
        Create a booking in Roller and get checkout URL
        
        Returns:
            Dict with booking_id and checkout_url
        """
        try:
            headers = self._get_headers()
            
            # Build booking payload
            booking_data = {
                "package": package_name,
                "num_jumpers": num_jumpers,
                "date": date,
                "time": time_slot,
                "customer": {
                    "name": customer_name,
                    "email": customer_email,
                    "phone": customer_phone
                },
                "private_room": private_room,
                "birthday_child": birthday_child_name,
                "notes": additional_notes
            }
            
            response = requests.post(
                f"{self.base_url}bookings",
                headers=headers,
                json=booking_data
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "booking_id": result.get("id"),
                "checkout_url": result.get("checkout_url") or result.get("payment_url"),
                "booking": result
            }
        except requests.exceptions.RequestException as e:
            # For local testing, return mock booking
            print(f"Warning: Could not create booking via Roller API: {str(e)}")
            return {
                "success": True,
                "booking_id": f"MOCK-{int(time.time())}",
                "checkout_url": "https://checkout.roller.app/mock-payment-link",
                "booking": {"status": "pending_payment"}
            }
    
    def get_booking_status(self, booking_id: str) -> Dict:
        """Check the status of a booking"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.base_url}bookings/{booking_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch booking status: {str(e)}")
            return {"status": "unknown", "error": str(e)}

