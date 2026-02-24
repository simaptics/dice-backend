"""
Custom JWT authentication that reads an access_token cookie.

The JWT is signed by an external auth service using a shared secret
(the SECRET_KEY env var). This module decodes the token and returns a
lightweight SimpleUser — Django's built-in User model is not used.
"""

import os
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Shared secret between this service and the auth service that issues tokens.
JWT_SECRET = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"


class SimpleUser:
    """Minimal user object built from JWT claims (no database backing)."""

    def __init__(self, user_id, permissions=None):
        self.id = user_id
        self.permissions = permissions or []
        self.is_authenticated = True


class DiceJWTAuthentication(BaseAuthentication):
    """DRF authentication backend that extracts identity from a JWT cookie.

    Returns (SimpleUser, None) on success, None when no cookie is present
    (allowing unauthenticated endpoints), or raises AuthenticationFailed.
    """

    def authenticate(self, request):
        token = request.COOKIES.get("access_token")
        if not token:
            # Returning None (instead of raising) lets views with AllowAny
            # permission work without a token.
            return None

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")

        # The auth service always issues a 16-character userId.
        user_id = data.get("userId")
        if not user_id or len(user_id) != 16:
            raise AuthenticationFailed("Invalid token payload")

        permissions = data.get("permissions", [])
        user = SimpleUser(user_id, permissions)
        return (user, None)

