import os
import httpx
from fastapi import HTTPException

async def send_admin_credentials_email(
    full_name: str,
    email: str,
    tenant_name: str,
    role: str,
    password: str = None,
    is_new_user: bool = False,
    is_existing_user: bool = False,
    is_otp: bool = False,
    otp: str = None,
    forgot_password_link: str = None,
):
    emailjs_user_id = os.getenv("EMAILJS_USER_ID")
    emailjs_service_id = os.getenv("EMAILJS_SERVICE_ID")
    emailjs_template_id = os.getenv("EMAILJS_TEMPLATE_ID")

    if not all([emailjs_user_id, emailjs_service_id, emailjs_template_id]):
        raise HTTPException(status_code=500, detail="EmailJS configuration missing")

    # # --- Build dynamic subject + body ---
    # subject = "Notification from Kapil Agro Farms"
    # email_body = ""

    # if is_otp and otp:
    #     subject = "Your OTP Code to Reset Password"
    #     email_body = f"""
    #         <p style="font-size:16px; margin:0 0 15px;">
    #         We received a request to reset your password. Use the OTP below to continue:
    #         </p>
    #         <div style="background:#f9f9f9; padding:15px; border:1px solid #ddd; border-radius:6px; text-align:center; font-size:18px; font-weight:bold; letter-spacing:2px; color:#2c7a7b;">
    #         {otp}
    #         </div>
    #         <p style="font-size:14px; color:#555; margin-top:15px;">
    #         This OTP is valid for <strong>5 minutes</strong>. If you didn’t request this, you can safely ignore this email.
    #         </p>
    #     """

    # elif is_new_user and password:
    #     subject = f"Welcome to {tenant_name} – Your {role} Account Details"
    #     email_body = f"""
    #         <p style="font-size:16px; margin:0 0 15px;">
    #         Your <strong>{role}</strong> account has been successfully created. Below are your login credentials:
    #         </p>
    #         <div style="background:#f9f9f9; padding:15px; border:1px solid #ddd; border-radius:6px; font-size:15px; line-height:1.6;">
    #         <p><strong>Email:</strong> {email}</p>
    #         <p><strong>Password:</strong> {password}</p>
    #         </div>
    #         <p style="margin-top:15px; font-size:15px;">
    #         <a href="#" style="background:#2c7a7b; color:#fff; text-decoration:none; padding:10px 20px; border-radius:5px; display:inline-block; font-weight:bold;">
    #             Log In
    #         </a>
    #         </p>
    #         <p style="font-size:14px; color:#555;">
    #         For security, we recommend changing your password after your first login.
    #         </p>
    #     """

    # elif is_existing_user:
    #     subject = "Account Already Exists – Login Instructions"
    #     email_body = f"""
    #         <p style="font-size:16px; margin:0 0 15px;">
    #         Your account already exists in our system. Please continue using your current password.
    #         </p>
    #         <p style="font-size:14px; color:#555;">
    #         
    #         </p>
    #     """

    # --- Build dynamic subject + body ---
    subject = "Notification from {{from_name}}"
    email_body = ""

    if is_otp and otp:
        subject = "OTP Code for Password Reset"
        email_body = f"""
            <p style="font-size:15px; margin:0 0 10px; color:#333;">
            We've received a request to reset your password. Use the OTP below to proceed:
            </p>
            <div style="background:#f9f9f9; padding:10px 15px; border:1px solid #ddd; border-radius:6px; text-align:center; font-size:16px; font-weight:bold; letter-spacing:2px; color:#2c7a7b; margin:15px auto; display:inline-block;">
            {otp}
            </div>
            <p style="font-size:13px; color:#555; margin-top:10px;">
            This OTP is valid for <strong>5 minutes</strong>. If you didn’t request this, please ignore this email.
            </p>
        """

    elif is_new_user and password:
        subject = f"welcome to {tenant_name} – Your {role} Account Details"
        email_body = f"""
            <p style="font-size:15px; margin:0 0 15px; color:#333;">
            Your <strong>{role}</strong> account has been created successfully. Below are your login details:
            </p>
            <div style="background:#f9f9f9; padding:20px; border:1px solid #ddd; border-radius:8px; font-size:14px; line-height:1.7; color:#333;">
                <p style="margin:0 0 10px;"><strong>Email:</strong> {email}</p>
                <p style="margin:0;"><strong>Password:</strong> {password}</p>
            </div>
            <p style="font-size:13px; color:#555;">
            For security, please change your password after your first login.
            </p>
        """

    elif is_existing_user:
        subject = "Account Already Exists – Login Instructions"
        email_body = f"""
            <p style="font-size:15px; margin:0 0 15px; color:#333;">
            An account with your email already exists in our system. You can continue using your current password.
            </p>
            <p style="font-size:14px; color:#555; margin:15px 0;">
            Forgot your password? Reset it using the link below:
            </p>
            <p style="margin:20px 0; font-size:14px;">
            If you forgot it, you can reset it using the 
             <a href="{forgot_password_link or '#'}" style="color:#2c7a7b; text-decoration:none; font-weight:bold;">
                Forgot Password
             </a> option in the app.        
            </p>
        """




    # Template parameters sent to EmailJS
    template_params = {
        "to_name": full_name,
        "from_name": tenant_name,
        "email_body": email_body,
        "to_email": email,
        "subject": subject,  #  dynamic subject
    }

    payload = {
        "user_id": emailjs_user_id,
        "service_id": emailjs_service_id,
        "template_id": emailjs_template_id,
        "template_params": template_params,
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json=payload,
                headers=headers,
                timeout=20.0,
            )
            print("Payload:", payload)  # Debugging line
            response.raise_for_status()
            print("EmailJS Response:", response.status_code, response.text)
            return True
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
