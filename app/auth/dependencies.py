import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv
import os


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    '''
    Get_current_user autentiserar JWT-token och kontrollerar om det är giltigt.
    '''
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Kunde inte validera dina uppgifter",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return "Success"
    except jwt.PyJWTError:
        raise credentials_exception