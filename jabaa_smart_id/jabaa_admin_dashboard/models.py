from django.db import models
from django.utils import timezone
from datetime import date

class Account(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=128, verbose_name="Password")
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.full_name = self.full_name.title()
        super().save(*args, **kwargs)

class Citizen(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    full_name = models.CharField(max_length=255)
    dob = models.DateField()  # Correctly define the dob field
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    card_id = models.CharField(max_length=20, unique=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_age(self):  # Add 'self' parameter
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def __str__(self):
        return self.full_name