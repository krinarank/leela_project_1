from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random


class Customer(AbstractUser):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    contactno = models.CharField(max_length=15)
    address = models.TextField()


    isadmin = models.BooleanField(default=False)
    is_delivery_person = models.BooleanField(default=False)  # ⭐ main role flag


    profile_image = models.ImageField(
        upload_to='customer_profiles/',
        blank=True,
        null=True
    )


    creationdate = models.DateTimeField(auto_now_add=True)
    updationdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)   # ✅ ADD THIS

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)


    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.user.username} - {self.otp}"
