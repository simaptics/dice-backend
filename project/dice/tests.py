"""
Tests for the dice app.

Covers the DiceMacro model, JWT cookie authentication, the public roll
endpoint, authenticated macro CRUD, and the macro roll action.

Run with:
    python manage.py test dice --settings=dice_backend.test_settings
"""

import jwt
import datetime
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed

from dice.models import DiceMacro
from dice.authentication import DiceJWTAuthentication, JWT_ALGORITHM, JWT_SECRET


# ---------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------

def make_token(user_id="abc123def456ghij", permissions=None, expired=False):
    """Generate a signed JWT token for testing.

    Args:
        user_id: 16-char user identifier embedded in the token payload.
        permissions: Optional list of permission strings.
        expired: If True the token's exp claim is set in the past so
                 the authentication layer will reject it.
    """
    payload = {
        "userId": user_id,
        "permissions": permissions or [],
        "iat": datetime.datetime.now(datetime.timezone.utc),
        # Negative timedelta produces an already-expired token
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=-1 if expired else 1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def auth_client(user_id="abc123def456ghij"):
    """Return an APIClient whose requests carry a valid JWT cookie.

    The cookie name (access_token) matches what DiceJWTAuthentication
    reads from incoming requests.
    """
    client = APIClient()
    token = make_token(user_id=user_id)
    client.cookies["access_token"] = token
    return client


# ---------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------
class DiceMacroModelTest(TestCase):
    """Verify DiceMacro field storage, string output, and constraints."""

    def test_create_macro(self):
        macro = DiceMacro.objects.create(
            user_id="abc123def456ghij", name="Fireball", num_dice=8, sides=6, modifier=5
        )
        self.assertEqual(macro.name, "Fireball")
        self.assertEqual(macro.num_dice, 8)
        self.assertEqual(macro.sides, 6)
        self.assertEqual(macro.modifier, 5)

    def test_str_representation(self):
        """__str__ should render in standard dice notation: name (NdS+M)."""
        macro = DiceMacro(name="Attack", num_dice=1, sides=20, modifier=3)
        self.assertEqual(str(macro), "Attack (1d20+3)")

    def test_unique_constraint(self):
        """The same user cannot have two macros with the same name."""
        DiceMacro.objects.create(
            user_id="abc123def456ghij", name="Fireball", num_dice=8, sides=6
        )
        with self.assertRaises(Exception):
            DiceMacro.objects.create(
                user_id="abc123def456ghij", name="Fireball", num_dice=2, sides=10
            )

    def test_same_name_different_user(self):
        """Different users may each have a macro with the same name."""
        DiceMacro.objects.create(
            user_id="abc123def456ghij", name="Fireball", num_dice=8, sides=6
        )
        macro2 = DiceMacro.objects.create(
            user_id="xyz789xyz789xyz7", name="Fireball", num_dice=4, sides=8
        )
        self.assertEqual(macro2.name, "Fireball")


# ---------------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------------
class DiceJWTAuthenticationTest(TestCase):
    """Test the custom JWT-from-cookie authentication backend."""

    def setUp(self):
        self.auth = DiceJWTAuthentication()

    def _make_request(self, token=None):
        """Build a minimal fake request with an optional access_token cookie."""
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.get("/")
        if token:
            request.COOKIES = {"access_token": token}
        else:
            request.COOKIES = {}
        return request

    def test_valid_token(self):
        """A correctly signed, non-expired token should return a SimpleUser."""
        token = make_token()
        request = self._make_request(token)
        user, _ = self.auth.authenticate(request)
        self.assertEqual(user.id, "abc123def456ghij")
        self.assertTrue(user.is_authenticated)

    def test_missing_token_returns_none(self):
        """No cookie means unauthenticated — return None (don't raise)."""
        request = self._make_request()
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_expired_token(self):
        token = make_token(expired=True)
        request = self._make_request(token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_invalid_token(self):
        """Garbage strings should be rejected as invalid tokens."""
        request = self._make_request("not-a-real-token")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_invalid_payload_bad_user_id(self):
        """A valid JWT whose userId is not exactly 16 chars should fail."""
        token = make_token(user_id="short")
        request = self._make_request(token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_permissions_in_token(self):
        """Permissions from the JWT payload should be available on the user."""
        token = make_token(permissions=["admin", "roll"])
        request = self._make_request(token)
        user, _ = self.auth.authenticate(request)
        self.assertEqual(user.permissions, ["admin", "roll"])


# ---------------------------------------------------------------
# Public roll endpoint tests — POST /api/roll/
# ---------------------------------------------------------------
class RollDiceViewTest(TestCase):
    """Test the public (no auth) dice roll endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_successful_roll(self):
        resp = self.client.post("/api/roll/", {"num_dice": 2, "sides": 6, "modifier": 3})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["rolls"]), 2)
        self.assertEqual(data["modifier"], 3)
        self.assertEqual(data["sides"], 6)
        # final = sum of individual rolls + modifier
        self.assertEqual(data["final"], sum(data["rolls"]) + 3)

    def test_roll_without_modifier(self):
        """Omitting modifier should default to 0."""
        resp = self.client.post("/api/roll/", {"num_dice": 1, "sides": 20})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["modifier"], 0)
        self.assertEqual(data["final"], data["total"])

    def test_response_keys(self):
        """Response must include exactly these keys."""
        resp = self.client.post("/api/roll/", {"num_dice": 1, "sides": 6})
        data = resp.json()
        self.assertEqual(set(data.keys()), {"rolls", "total", "modifier", "final", "sides"})

    def test_roll_values_in_range(self):
        """Each die result should be between 1 and the number of sides."""
        resp = self.client.post("/api/roll/", {"num_dice": 10, "sides": 6})
        data = resp.json()
        for roll in data["rolls"]:
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)

    # --- Validation: num_dice must be 1–100, sides must be 2–1000 ---

    def test_num_dice_too_low(self):
        resp = self.client.post("/api/roll/", {"num_dice": 0, "sides": 6})
        self.assertEqual(resp.status_code, 400)

    def test_num_dice_too_high(self):
        resp = self.client.post("/api/roll/", {"num_dice": 101, "sides": 6})
        self.assertEqual(resp.status_code, 400)

    def test_sides_too_low(self):
        resp = self.client.post("/api/roll/", {"num_dice": 1, "sides": 1})
        self.assertEqual(resp.status_code, 400)

    def test_sides_too_high(self):
        resp = self.client.post("/api/roll/", {"num_dice": 1, "sides": 1001})
        self.assertEqual(resp.status_code, 400)

    def test_missing_required_fields(self):
        resp = self.client.post("/api/roll/", {})
        self.assertEqual(resp.status_code, 400)


# ---------------------------------------------------------------
# Macro CRUD tests — /api/macros/
# ---------------------------------------------------------------
class DiceMacroViewSetTest(TestCase):
    """Test authenticated CRUD operations on dice macros."""

    def setUp(self):
        self.user_id = "abc123def456ghij"
        self.client = auth_client(self.user_id)

    def test_create_macro(self):
        resp = self.client.post(
            "/api/macros/", {"name": "Fireball", "num_dice": 8, "sides": 6, "modifier": 5}
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["name"], "Fireball")

    def test_list_macros(self):
        DiceMacro.objects.create(
            user_id=self.user_id, name="A", num_dice=1, sides=6
        )
        DiceMacro.objects.create(
            user_id=self.user_id, name="B", num_dice=2, sides=8
        )
        resp = self.client.get("/api/macros/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_retrieve_macro(self):
        macro = DiceMacro.objects.create(
            user_id=self.user_id, name="Hit", num_dice=1, sides=20, modifier=5
        )
        resp = self.client.get(f"/api/macros/{macro.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["name"], "Hit")

    def test_update_macro(self):
        macro = DiceMacro.objects.create(
            user_id=self.user_id, name="Hit", num_dice=1, sides=20
        )
        resp = self.client.patch(
            f"/api/macros/{macro.id}/", {"modifier": 7}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        macro.refresh_from_db()
        self.assertEqual(macro.modifier, 7)

    def test_delete_macro(self):
        macro = DiceMacro.objects.create(
            user_id=self.user_id, name="Hit", num_dice=1, sides=20
        )
        resp = self.client.delete(f"/api/macros/{macro.id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(DiceMacro.objects.count(), 0)

    # --- Access control ---

    def test_unauthenticated_access(self):
        """Requests without a JWT cookie should be rejected."""
        client = APIClient()
        resp = client.get("/api/macros/")
        self.assertIn(resp.status_code, [401, 403])

    def test_cannot_access_other_users_macro(self):
        """Querying another user's macro by ID should 404 (filtered out)."""
        macro = DiceMacro.objects.create(
            user_id="other_user_id_1234", name="Secret", num_dice=1, sides=20
        )
        resp = self.client.get(f"/api/macros/{macro.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_list_only_own_macros(self):
        """Listing macros should never include another user's data."""
        DiceMacro.objects.create(
            user_id=self.user_id, name="Mine", num_dice=1, sides=6
        )
        DiceMacro.objects.create(
            user_id="other_user_id_1234", name="Theirs", num_dice=2, sides=8
        )
        resp = self.client.get("/api/macros/")
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["name"], "Mine")

    def test_max_macros_limit(self):
        """Users are capped at 10 macros; the 11th should be rejected."""
        for i in range(10):
            DiceMacro.objects.create(
                user_id=self.user_id, name=f"Macro{i}", num_dice=1, sides=6
            )
        resp = self.client.post(
            "/api/macros/", {"name": "OneMore", "num_dice": 1, "sides": 6}
        )
        self.assertEqual(resp.status_code, 400)


# ---------------------------------------------------------------
# Macro roll action tests — POST /api/macros/{id}/roll/
# ---------------------------------------------------------------
class MacroRollTest(TestCase):
    """Test rolling dice through a saved macro."""

    def setUp(self):
        self.user_id = "abc123def456ghij"
        self.client = auth_client(self.user_id)
        self.macro = DiceMacro.objects.create(
            user_id=self.user_id, name="Fireball", num_dice=8, sides=6, modifier=5
        )

    def test_roll_macro(self):
        """Rolling a macro should return the correct structure and math."""
        resp = self.client.post(f"/api/macros/{self.macro.id}/roll/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["name"], "Fireball")
        self.assertEqual(data["macro_id"], self.macro.id)
        self.assertEqual(len(data["rolls"]), 8)
        self.assertEqual(data["modifier"], 5)
        self.assertEqual(data["final"], sum(data["rolls"]) + 5)

    def test_roll_values_in_range(self):
        resp = self.client.post(f"/api/macros/{self.macro.id}/roll/")
        for roll in resp.json()["rolls"]:
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)

    def test_cannot_roll_other_users_macro(self):
        """Rolling another user's macro should 404 (queryset is filtered)."""
        other_macro = DiceMacro.objects.create(
            user_id="other_user_id_1234", name="Secret", num_dice=1, sides=20
        )
        resp = self.client.post(f"/api/macros/{other_macro.id}/roll/")
        self.assertEqual(resp.status_code, 404)
