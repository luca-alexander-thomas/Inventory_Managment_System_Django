from django.db import models
from datetime import date
from django.contrib.auth.models import User

# Create your models here.

class Inventory_Item(models.Model):
    full_id = models.CharField(default=None, max_length=50, null=True, blank=True)
    user_id = models.CharField(max_length=50,null=True, blank=True)
    name = models.CharField(max_length=200)
    amount = models.IntegerField(default=1)
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

class PrintServer(models.Model):
    
    name = models.CharField(max_length=255, null=True, blank=True)
    ip = models.CharField(max_length=255, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    uuid = models.CharField(null=True, blank=True, max_length=255)
    def __str__(self):
        return self.name    

class Inventory_Settings(models.Model):
    printer_name = models.CharField(max_length=200)
    paper_width = models.FloatField(default=1)
    paper_height = models.FloatField(default=1)
    paper_orientation = models.CharField(max_length=200, default='landscape')
    paper_name = models.CharField(max_length=200, null=True)
    print_file_name = models.CharField(max_length=200, default='label.pdf')
    print_server = models.ForeignKey(PrintServer, related_name='default_server', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.id) + ' ' + self.printer_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=32, null=True, blank=True)
    auto_login_key = models.CharField(max_length=64, null=True, blank=True)
    def __str__(self):
        return self.user.username
    
class UserClients(models.Model):
    user = models.ForeignKey(User,related_name='clients', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    os = models.CharField(max_length=255, null=True, blank=True)
    hwkey = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(default=None)
    def __str__(self):
        return self.name

