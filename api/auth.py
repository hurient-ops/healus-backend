from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid
import jwt
from datetime import datetime, timedelta, timezone

from core.database import get_db
from models import models, schemas

router = APIRouter()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "healus_super_secret_key_for_jwt" # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.UserSignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if PID is already registered to someone else
    if payload.pump_id:
        existing_device = db.query(models.User).filter(models.User.pump_id == payload.pump_id).first()
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pump ID is already registered"
            )

    # Create new user
    new_user = models.User(
        id=str(uuid.uuid4()),
        name=payload.name,
        email=payload.email,
        phone_number=payload.phone_number,
        birth_date=payload.birth_date,
        terms_agreed=payload.terms_agreed,
        pump_id=payload.pump_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "status": "success", 
        "message": "User successfully created",
        "user_id": new_user.id
    }

@router.post("/login")
def login(payload: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
        
    # Generate JWT
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "status": "success",
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "user": {
            "name": user.name,
            "email": user.email,
            "pump_id": user.pump_id
        }
    }