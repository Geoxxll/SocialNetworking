from django.db import models

class Approval(models.Model):
    require_approval = models.BooleanField(default=True, editable = True)

    class Meta:
        verbose_name_plural = "User Approval"
