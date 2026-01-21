from django.contrib.auth.models import User
from django.db import models

class Inquiry(models.Model):
    inquiry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    inquiry_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Responded', 'Responded')],
        default='Pending'
    )

    def __str__(self):
        return self.subject
