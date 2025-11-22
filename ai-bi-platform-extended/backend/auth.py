from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict

SECURITY_SCHEME = HTTPBearer()
SECRET = "dev-secret-change-me"
ALGORITHM = "HS256"
AUDIENCE = "ai-bi-client"

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(SECURITY_SCHEME)) -> Dict:
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM], audience=AUDIENCE)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return payload
