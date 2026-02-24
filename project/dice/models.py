"""Models for the dice app."""

from django.db import models


class DiceMacro(models.Model):
    """A saved dice roll configuration owned by a specific user.

    Each macro stores the number of dice, sides per die, and an optional
    modifier. Users can trigger a roll from a macro instead of specifying
    parameters each time.
    """

    user_id = models.CharField(max_length=16)   # 16-char ID from the JWT
    name = models.CharField(max_length=100)
    num_dice = models.IntegerField()
    sides = models.IntegerField()
    modifier = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user_id", "name")   # one macro name per user

    def __str__(self):
        return f"{self.name} ({self.num_dice}d{self.sides}+{self.modifier})"