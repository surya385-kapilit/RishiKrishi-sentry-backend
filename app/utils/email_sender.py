# import os
# import requests
# from fastapi import HTTPException

# def send_admin_credentials_email(full_name: str, email: str, password: str, tenant_name: str,role:str):
#     """Send admin credentials email using EmailJS API"""
#     emailjs_user_id = os.getenv("EMAILJS_USER_ID")
#     emailjs_service_id = os.getenv("EMAILJS_SERVICE_ID")
#     emailjs_template_id = os.getenv("EMAILJS_TEMPLATE_ID")

#     print(f"EmailJS User ID: {emailjs_user_id}")
#     print(f"EmailJS Service ID: {emailjs_service_id}")
#     print(f"EmailJS Template ID: {emailjs_template_id}")    

#     if not all([emailjs_user_id, emailjs_service_id, emailjs_template_id]):
#         raise HTTPException(status_code=500, detail="EmailJS configuration missing")

#     url = "https://api.emailjs.com/api/v1.0/email/send"
#     payload = {
#         "user_id": emailjs_user_id,
#         "service_id": emailjs_service_id,
#         "template_id": emailjs_template_id,
#         "template_params": {
#             "to_name": full_name,
#             "to_email": email,
#             "password": password,
#             "role":role,
#             "from_name": tenant_name  
#         }
#     }

#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         return True
#     except requests.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


import os
import httpx
from fastapi import HTTPException

async def send_admin_credentials_email(full_name: str, email: str, password: str, tenant_name: str, role: str):
    emailjs_user_id = os.getenv("EMAILJS_USER_ID")
    emailjs_service_id = os.getenv("EMAILJS_SERVICE_ID")
    emailjs_template_id = os.getenv("EMAILJS_TEMPLATE_ID")
    emailjs_private_key = os.getenv("EMAILJS_PRIVATE_KEY")

    if not all([emailjs_user_id, emailjs_service_id, emailjs_template_id]):
        raise HTTPException(status_code=500, detail="EmailJS configuration missing")

    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "user_id": emailjs_user_id,
        "service_id": emailjs_service_id,
        "template_id": emailjs_template_id,
        "template_params": {
            "to_name": full_name,
            "to_email": email,
            "password": password,
            "role": role,
            "from_name": tenant_name
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {emailjs_private_key}"  # Required for server-side calls
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=20.0)
            response.raise_for_status()
            print("EmailJS Response:", response.status_code, response.text)
            print("Email sent successfully")
            return True
        except httpx.RequestError as e:   
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
