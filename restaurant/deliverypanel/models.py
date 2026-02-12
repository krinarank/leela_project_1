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
    is_active = models.BooleanField(default=True)
    profile_image = models.ImageField(
        upload_to='delivery/profile_pics/',
        null=True,
        blank=True,
        default=None
    )


    def __str__(self):
        return self.fname

class DeliveryVehicle(models.Model):
    delivery_person = models.OneToOneField(
        DeliveryPerson,
        on_delete=models.CASCADE,
        related_name='vehicle'
    )

    VEHICLE_CHOICES = [
        ('Bike', 'Bike'),
        ('Scooter', 'Scooter'),
       
    ]

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    vehicle_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle_type} - {self.vehicle_number}"
    
    