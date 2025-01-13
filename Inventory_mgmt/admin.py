from django.contrib import admin
from .models import *
import requests

def own_items(modeladmin, requests, queryset):
    UserID = requests.user.id
    queryset.update(user_id=UserID)

own_items.short_description = "Overtake the Ownership of all selected items"

class Inventory_ItemA(admin.ModelAdmin):
    list_display = ('name', 'full_id', 'user_id', 'created_at')
    list_filter = ('created_at', 'user_id')
    actions = [own_items]


admin.site.site_header = "Inventory Managment Administration"



# Register your models here.
admin.site.register(Inventory_Item, Inventory_ItemA)
admin.site.register(Inventory_item_LocationID)
admin.site.register(Inventory_item_UsecaseID)
admin.site.register(Inventory_Settings)
admin.site.register(UserProfile)
admin.site.register(UserClients)
admin.site.register(PrintServer)
