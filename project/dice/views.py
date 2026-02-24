"""Views for public dice rolling and authenticated macro CRUD + roll."""

import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .serializers import RollRequestSerializer, RollResultSerializer, DiceMacroSerializer
from .models import DiceMacro


# ----------------------
# Public dice roll endpoint — POST /api/roll/
# ----------------------
@method_decorator(csrf_exempt, name="dispatch")
class RollDiceView(APIView):
    """Roll dice without authentication.

    Accepts num_dice, sides, and an optional modifier. Returns the
    individual rolls, their sum, and the modifier-adjusted final total.
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # skip JWT check entirely

    def post(self, request):
        serializer = RollRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        num_dice = serializer.validated_data["num_dice"]
        sides = serializer.validated_data["sides"]
        modifier = serializer.validated_data.get("modifier", 0)

        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls)
        final = total + modifier

        return Response({
            "rolls": rolls,
            "total": total,
            "modifier": modifier,
            "final": final,
            "sides": sides,
        })


# ----------------------
# Dice macros (JWT protected) — /api/macros/
# ----------------------
class DiceMacroViewSet(viewsets.ModelViewSet):
    """CRUD for saved dice macros, scoped to the authenticated user.

    Also exposes a custom `roll` action at POST /api/macros/{id}/roll/
    that executes the saved macro and returns the result.
    """

    serializer_class = DiceMacroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return macros belonging to the current user."""
        return DiceMacro.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        """Stamp the new macro with the authenticated user's ID."""
        serializer.save(user_id=self.request.user.id)

    @action(detail=True, methods=["post"], url_path="roll")
    def roll_macro(self, request, pk=None):
        """Roll dice using the parameters saved in a macro."""
        macro = self.get_object()  # also enforces ownership via get_queryset
        rolls = [random.randint(1, macro.sides) for _ in range(macro.num_dice)]
        total = sum(rolls)
        final = total + macro.modifier

        return Response({
            "macro_id": macro.id,
            "name": macro.name,
            "rolls": rolls,
            "total": total,
            "modifier": macro.modifier,
            "final": final,
        }, status=status.HTTP_200_OK)
