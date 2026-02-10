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
# Public dice roll endpoint
# ----------------------
@method_decorator(csrf_exempt, name="dispatch")
class RollDiceView(APIView):
    # No authentication needed
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RollRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        num_dice = serializer.validated_data["num_dice"]
        sides = serializer.validated_data["sides"]
        modifier = serializer.validated_data.get("modifier", 0)

        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls)
        final = total + modifier

        result = {
            "rolls": rolls,
            "total": total,
            "modifier": modifier,
            "final": final,
        }

        return Response(result)


# ----------------------
# Dice macros (JWT protected)
# ----------------------
class DiceMacroViewSet(viewsets.ModelViewSet):
    serializer_class = DiceMacroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DiceMacro.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)
        
    @action(detail=True, methods=["post"], url_path="roll")
    def roll_macro(self, request, pk=None):
        macro = self.get_object()  # ensures macro belongs to user
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
