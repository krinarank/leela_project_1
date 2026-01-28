from django.db import models
from accounts.models import Customer

class DeliveryPerson(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)

    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    address = models.TextField()

    joining_date = models.DateField(auto_now_add=True)  # ✅ BEST

    def __str__(self):
        return self.fname
