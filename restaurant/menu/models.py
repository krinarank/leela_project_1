
from django.db import models
from django.conf import settings

class Inquiry(models.Model):
    inquiry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    admin_reply = models.TextField(null=True, blank=True)   # ✅ ADD THIS

    inquiry_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Responded', 'Responded')],
        default='Pending'
    )

    def __str__(self):
        return self.subject
