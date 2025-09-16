import time
import random
import logging
import bcrypt
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

otp_router = APIRouter()

# -----------------------------
# In-memory OTP storage
# -----------------------------
otp_storage = {}

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def store_otp(email: str, otp: str) -> None:
    """Store OTP in memory with 5-minute expiry"""
    expiry_time = time.time() + 300  # 300 seconds = 5 minutes
    otp_storage[email] = {"otp": otp, "expiry": expiry_time}
    logger.debug(f"Stored OTP {otp} for {email}")

def verify_otp(email: str, otp: str) -> bool:
    """Verify and consume OTP"""
    if email in otp_storage:
        stored = otp_storage[email]
        if stored["expiry"] >= time.time() and stored["otp"] == otp:
            del otp_storage[email]  # OTP used once
            return True
    return False