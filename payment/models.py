from django.db import models
from user.models import User


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.JSONField(default=dict)

    def __str__(self):
        return f"Payment #{self.id} - {self.amount} {self.method} on {self.date}"
