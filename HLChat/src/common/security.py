from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException

securityHTTPBearer = HTTPBearer(auto_error=False)

def get_access_token(
    auth_header: HTTPAuthorizationCredentials | None = Depends(securityHTTPBearer),
) -> str:
    print(f" Auth Header: {auth_header}")
    if auth_header is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return auth_header.credentials