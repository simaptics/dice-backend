import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import os
JWT_SECRET = os.getenv("SECRET_KEY")

JWT_ALGORITHM = "HS256"

class SimpleUser:
    def __init__(self, user_id, permissions=None):
        self.id = user_id
        self.permissions = permissions or []
        self.is_authenticated = True

class DiceJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("access_token")
        if not token:
            return None  # <- important! allow unauthenticated users

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")

        user_id = data.get("userId")
        if not user_id or len(user_id) != 16:
            raise AuthenticationFailed("Invalid token payload")

        permissions = data.get("permissions", [])
        user = SimpleUser(user_id, permissions)
        return (user, None)

