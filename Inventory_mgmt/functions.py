from .models import *

def update_number_table():
    all_items = Inventory_Item.objects.all()
    for item in all_items:
        if Inventory_item_LocationID.objects.filter(location_name=item.location).exists():
            pass
        else:
            Inventory_item_LocationID.objects.create(location_name=item.location)
        if Inventory_item_UsecaseID.objects.filter(usecase_name=item.usecase).exists():
            pass
        else:
            Inventory_item_UsecaseID.objects.create(usecase_name=item.usecase)
        Item_id = Inventory_Item.objects.get(name=item.name, vendor=item.vendor).id
        Location_id = Inventory_item_LocationID.objects.get(location_name=item.location).id
        Usecase_id = Inventory_item_UsecaseID.objects.get(usecase_name=item.usecase).id
        Full_id = str(Location_id) + "-" + str(Usecase_id) + "-" + str(Item_id)
        Inventory_Item.objects.filter(id=Item_id).update(full_id=Full_id)