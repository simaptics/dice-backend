"""Serializers for dice roll requests and macro CRUD."""

from rest_framework import serializers
from .models import DiceMacro

MAX_MACROS_PER_USER = 10


class RollRequestSerializer(serializers.Serializer):
    """Validates incoming dice roll parameters (public endpoint)."""

    num_dice = serializers.IntegerField(min_value=1, max_value=100)
    sides = serializers.IntegerField(min_value=2, max_value=1000)
    modifier = serializers.IntegerField(required=False, default=0)


class RollResultSerializer(serializers.Serializer):
    """Schema for the dice roll response payload."""

    rolls = serializers.ListField(child=serializers.IntegerField())
    total = serializers.IntegerField()
    modifier = serializers.IntegerField()
    final = serializers.IntegerField()
    sides = serializers.IntegerField(min_value=2, max_value=100)


class DiceMacroSerializer(serializers.ModelSerializer):
    """Handles macro creation/updates and enforces the per-user macro limit."""

    class Meta:
        model = DiceMacro
        fields = ["id", "name", "num_dice", "sides", "modifier"]

    def validate(self, attrs):
        request = self.context.get("request")
        # user_id comes from the JWT-backed SimpleUser set by authentication
        user_id = getattr(request.user, "id", None)

        # Only enforce the macro cap on creation, not updates
        if self.instance is None:
            count = DiceMacro.objects.filter(user_id=user_id).count()
            if count >= MAX_MACROS_PER_USER:
                raise serializers.ValidationError(
                    f"You can only save up to {MAX_MACROS_PER_USER} macros."
                )

        # Stamp the owning user so it's saved with the macro
        attrs["user_id"] = user_id

        return attrs