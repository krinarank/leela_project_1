# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class Customer(AbstractUser):
#     username = models.CharField(max_length=50, unique=True)
#     firstname = models.CharField(max_length=50)
#     lastname = models.CharField(max_length=50)
#     gender = models.CharField(max_length=10)
#     email = models.EmailField(unique=True)
#     contactno = models.CharField(max_length=15)
#     address = models.TextField()
#     isadmin = models.BooleanField(default=False)
#     password = models.CharField(max_length=100)

#     creationdate = models.DateTimeField(auto_now_add=True)
#     updationdate = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.username

from django.contrib.auth.models import AbstractUser
from django.db import models

class Customer(AbstractUser):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    contactno = models.CharField(max_length=15)
    address = models.TextField()
    isadmin = models.BooleanField(default=False)

    creationdate = models.DateTimeField(auto_now_add=True)
    updationdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
