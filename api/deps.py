from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from core.database import get_db
from models import models

# Use auto_error=False so it doesn't automatically throw 401 if token is missing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

SECRET_KEY = "healus_super_secret_key_for_jwt"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Extracts the user from the JWT token.
    If no token is provided or the token is invalid, returns the test user
    so that the dashboard can still function in "sample mode".
    """
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email:
                user = db.query(models.User).filter(models.User.email == email).first()
                if user:
                    return user
        except jwt.PyJWTError:
            pass # Invalid token, fallback to test user
            
    # Fallback: return testuser@healus.com for sample viewing
    test_user = db.query(models.User).filter(models.User.email == "testuser@healus.com").first()
    return test_user
