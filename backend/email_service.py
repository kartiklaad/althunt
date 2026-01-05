"""
Email service for sending booking confirmations
"""

import os
from typing import Dict, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_booking_confirmation(
    customer_email: str,
    customer_name: str,
    booking_details: Dict,
    booking_id: str
) -> bool:
    """
    Send booking confirmation email
    
    Args:
        customer_email: Customer's email address
        customer_name: Customer's name
        booking_details: Dict with booking information
        booking_id: Booking ID from Roller
    
    Returns:
        True if email sent successfully, False otherwise
    """
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@altitudehuntsville.com")
    
    if not sendgrid_api_key:
        print("Warning: SENDGRID_API_KEY not set. Email not sent.")
        print(f"Would send confirmation to {customer_email} for booking {booking_id}")
        return False
    
    # Build email content
    package = booking_details.get("package", "Unknown")
    num_jumpers = booking_details.get("num_jumpers", 0)
    date = booking_details.get("date", "")
    time_slot = booking_details.get("time", "")
    private_room = booking_details.get("private_room", False)
    birthday_child = booking_details.get("birthday_child", "")
    
    subject = f"🎉 Your Altitude Huntsville Party Booking Confirmation - {booking_id}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #4CAF50;">🎉 Party Booking Confirmed!</h1>
            
            <p>Hi {customer_name},</p>
            
            <p>We're so excited to host your party at Altitude Trampoline Park in Huntsville!</p>
            
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h2 style="margin-top: 0;">Booking Details</h2>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Package:</strong> {package}</p>
                <p><strong>Number of Jumpers:</strong> {num_jumpers}</p>
                <p><strong>Date:</strong> {date}</p>
                <p><strong>Time:</strong> {time_slot}</p>
                {f'<p><strong>Birthday Child:</strong> {birthday_child}</p>' if birthday_child else ''}
                {f'<p><strong>Private Room:</strong> Yes</p>' if private_room else ''}
            </div>
            
            <h3>What's Next?</h3>
            <ul>
                <li>Complete your payment using the checkout link provided</li>
                <li>All participants will need to sign waivers (we'll send the link)</li>
                <li>Arrive 15 minutes early on your party date</li>
                <li>Don't forget to bring Altitude grip socks (or purchase at the park)</li>
            </ul>
            
            <h3>Important Reminders</h3>
            <ul>
                <li>Minimum age: Check our website for age requirements</li>
                <li>Waivers: All jumpers must have signed waivers</li>
                <li>Cancellation: Please contact us at least 48 hours in advance for changes</li>
            </ul>
            
            <p>If you have any questions, feel free to reach out to us!</p>
            
            <p>See you soon! 🎈</p>
            
            <p style="margin-top: 30px; font-size: 12px; color: #666;">
                Altitude Trampoline Park Huntsville<br>
                This is an automated confirmation email.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
    Party Booking Confirmed!
    
    Hi {customer_name},
    
    We're excited to host your party at Altitude Trampoline Park in Huntsville!
    
    Booking Details:
    - Booking ID: {booking_id}
    - Package: {package}
    - Number of Jumpers: {num_jumpers}
    - Date: {date}
    - Time: {time_slot}
    {f'- Birthday Child: {birthday_child}' if birthday_child else ''}
    {f'- Private Room: Yes' if private_room else ''}
    
    What's Next?
    - Complete your payment using the checkout link
    - All participants need to sign waivers
    - Arrive 15 minutes early
    
    Questions? Contact us!
    
    Altitude Trampoline Park Huntsville
    """
    
    try:
        message = Mail(
            from_email=from_email,
            to_emails=customer_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_content
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 202]:
            print(f"Confirmation email sent to {customer_email}")
            return True
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_payment_confirmation(
    customer_email: str,
    customer_name: str,
    booking_id: str,
    amount: float
) -> bool:
    """Send payment confirmation email"""
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@altitudehuntsville.com")
    
    if not sendgrid_api_key:
        print("Warning: SENDGRID_API_KEY not set. Email not sent.")
        return False
    
    subject = f"✅ Payment Received - Booking {booking_id}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #4CAF50;">✅ Payment Confirmed!</h1>
            <p>Hi {customer_name},</p>
            <p>We've received your payment of ${amount:.2f} for booking {booking_id}.</p>
            <p>Your party is all set! We'll see you soon! 🎉</p>
        </div>
    </body>
    </html>
    """
    
    try:
        message = Mail(
            from_email=from_email,
            to_emails=customer_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Error sending payment confirmation: {str(e)}")
        return False

