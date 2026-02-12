from django.contrib.auth.models import AbstractUser
from django.db import models

class Customer(AbstractUser):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    contactno = models.CharField(max_length=15)
    address = models.TextField()
    isadmin = models.BooleanField(default=False)
    # is_delivery_person = models.BooleanField(default=False)  # ⭐ MAIN FLAG

    profile_image = models.ImageField(
        upload_to='customer_profiles/',  # simple folder
        blank=True,
        null=True
    )


    password = models.CharField(max_length=100)
    is_delivery_person = models.BooleanField(default=False)  # ⭐ MAIN FLAG
    
    creationdate = models.DateTimeField(auto_now_add=True)
    updationdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
