from django.shortcuts import render
from pprint import pprint
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from django.conf import settings

def sendemail(receiver_email, name, otp):
    sender_email = "projectcollege273@gmail.com"  # Your Gmail address
    password = "agpp myat cyhd ovxo"  # Your App password

    # Create MIME message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "OTP Verification"

    # Email body
    html = f"""
    <html>
        <body>
            <p>Dear {name},</p>
            <p>Your Email Verification code is: <strong>{otp}</strong></p>
            <p>Please use this code to complete your email verification.</p>
            <p>Thanks and regards,<br>Blood Bank Team</p>
        </body>
    </html>
    """
    message.attach(MIMEText(html, 'html'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure connection
        server.login(sender_email, password)  # Login
        server.sendmail(sender_email, receiver_email, message.as_string())  # Send email
        server.quit()  # Quit connection
        print("Email sent successfully!")
        return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return False