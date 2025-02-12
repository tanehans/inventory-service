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
    """
    Hämtar den aktuella användaren baserat på den angivna JWT-token.
    
    Argument:
        token (str): JWT-token som tillhandahålls av användaren.
    
    Returnerar:
        dict: En ordbok som innehåller användar-ID, e-post och roller.
    
    Undantag:
        HTTPException: Om token är ogiltig, utgången eller om användar-ID inte hittas i token-payload.
    """
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Kunde inte validera dina uppgifter",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
        
        return {"user_id": user_id, "email": email, "roles": payload.get("roles", [])}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token har gått ut")
    except jwt.InvalidTokenError:
        raise credentials_exception


def get_current_admin_user(user: dict = Depends(get_current_user)):
    """
    Hämtar den nuvarande användaren och kontrollerar om användaren har admin-behörighet.

    Args:
        user (dict): Användarens information som hämtas från Depends(get_current_user).

    Raises:
        HTTPException: Om användaren inte har admin-behörighet, kastas ett undantag med statuskoden 401 och meddelandet "Åtkomst nekad".

    Returns:
        dict: Användarens information om användaren har admin-behörighet.
    """
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Åtkomst nekad")
    return user
