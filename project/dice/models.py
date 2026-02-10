from django.db import models

class DiceMacro(models.Model):
    user_id = models.CharField(max_length=16)  # comes from JWT
    name = models.CharField(max_length=100)
    num_dice = models.IntegerField()
    sides = models.IntegerField()
    modifier = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user_id", "name")  # one macro name per user

    def __str__(self):
        return f"{self.name} ({self.num_dice}d{self.sides}+{self.modifier})"