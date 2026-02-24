from rest_framework import serializers
from .models import DiceMacro


MAX_MACROS_PER_USER = 10  # maximum macros per user

# Dice roll request
class RollRequestSerializer(serializers.Serializer):
    num_dice = serializers.IntegerField(min_value=1, max_value=100)
    sides = serializers.IntegerField(min_value=2, max_value=1000)
    modifier = serializers.IntegerField(required=False, default=0)

class RollResultSerializer(serializers.Serializer):
    rolls = serializers.ListField(child=serializers.IntegerField())
    total = serializers.IntegerField()
    modifier = serializers.IntegerField()
    final = serializers.IntegerField()
    sides = serializers.IntegerField(min_value=2, max_value=100)

# Dice macro serializer
class DiceMacroSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiceMacro
        fields = ["id", "name", "num_dice", "sides", "modifier"]


    def validate(self, attrs):
        request = self.context.get("request")
        user_id = getattr(request.user, "id", None) or request.headers.get("user_id")  # or however you pass JWT id

        # Only check on creation
        if self.instance is None:
            count = DiceMacro.objects.filter(user_id=user_id).count()
            if count >= MAX_MACROS_PER_USER:
                raise serializers.ValidationError(
                    f"You can only save up to {MAX_MACROS_PER_USER} macros."
                )
        # Assign user_id to the macro
        attrs["user_id"] = user_id

        return attrs  # 🔹 MUST return attrs