from django.db import models
from datetime import date

# Create your models here.

class Inventory_Item(models.Model):
    full_id = models.CharField(default=None, max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200)
    group = models.CharField(max_length=200)
    vendor = models.CharField(max_length=200)
    usecase = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    created_at = models.DateField(default=date.today)
    picture = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return str(self.id) + ' ' + self.name

class Inventory_item_LocationID(models.Model):
    location_name = models.CharField(max_length=200)
    def __str__(self):
        return str(self.id) + ' ' + self.location_name

class Inventory_item_UsecaseID(models.Model):
    usecase_name = models.CharField(max_length=200)
    def __str__(self):
        return str(self.id) + ' ' + self.usecase_name







