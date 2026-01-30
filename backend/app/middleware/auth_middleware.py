
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from ..core.security import decode_access_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public endpoints that don't need auth
        public_paths = [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/auth/login", 
            "/auth/google",
            "/portfolio", # Auth handled by router via X-User-Email for MVP
            "/" # Root welcome message
        ]
        
        # Check if path is public (startswith to handle subpaths if needed, or exact match)
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
            
        # Check for Authorization header or Cookie
        token = None
        
        # 1. Header: Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
        # 2. Cookie: access_token=<token>
        if not token:
            token = request.cookies.get("access_token")
            
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"}
            )
            
        # Verify Token
        payload = decode_access_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"}
            )
            
        # Attach user info to request state (optional)
        request.state.user_email = payload.get("sub")
        
        response = await call_next(request)
        return response
