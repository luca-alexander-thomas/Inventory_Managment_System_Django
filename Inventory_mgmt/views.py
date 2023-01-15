import django.shortcuts
import requests
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from .models import *
from .functions import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .functions import print_lable, html_to_pdf
from django.views.generic import View
from django.templatetags.static import static




# Create your views here.


def view_item(request, id=None):
    item = Inventory_Item.objects.filter(id=id)
    if request.method == 'POST':
        if request.POST['form_type'] == 'print_lable':
            code = gen_barcode(item[0].full_id)
            context = {'item': item, 'name': 'Name', 'vendor': 'Vendor', 'usecase': 'Usecase', 'location': 'Location',
                       'group': 'Group', 'code': code}
            img = print_lable('lable.html', context)
            messages.success(request, img)
    if type(id) == int:
        return render(request, 'view_item.html', {'item': item, 'title': 'View Item'})
    else:
        messages.error(request, 'Item not found')
        return render(request, 'view_item.html', {'title': 'View Item'})


def edit_item(request, id=None):
    if type(id) == int:
        item = Inventory_Item.objects.filter(id=id)
        return render(request, 'edit_item.html', {'item': item, 'title': 'Edit Item'})
    else:
        messages.error(request, 'Item not found')
        return render(request, 'edit_item.html', {'title': 'Edit Item'})


def home(request):
    all_items = Inventory_Item.objects.all()
    if request.method == 'POST':
        if request.POST['form_type'] == 'update_numbers':
            print('Update numbers')
            update_number_table()
            messages.success(request, 'Numbers updated')
            return redirect('/')
        if request.POST['form_type'] == 'additem':
            print('Recieved Data:', request.POST['form_name']) #Check for picture
            if request.POST['form_picture'] != "":
                Inventory_Item.objects.create(name=request.POST['form_name'], vendor=request.POST['form_vendor'], usecase=request.POST['form_usecase'], location=request.POST['form_location'], group=request.POST['form_group'], description=request.POST['form_describtion'], picture=request.FILES['form_picture'])
                if Inventory_item_LocationID.objects.filter(location_name=request.POST['form_location']).exists():
                    pass
                else:
                    Inventory_item_LocationID.objects.create(location_name=request.POST['form_location'])
                if Inventory_item_UsecaseID.objects.filter(usecase_name=request.POST['form_usecase']).exists():
                    pass
                else:
                    Inventory_item_UsecaseID.objects.create(usecase_name=request.POST['form_usecase'])
                Item_id = Inventory_Item.objects.get(name=request.POST['form_name'], vendor=request.POST['form_vendor']).id
                Location_id = Inventory_item_LocationID.objects.get(location_name=request.POST['form_location']).id
                Usecase_id = Inventory_item_UsecaseID.objects.get(usecase_name=request.POST['form_usecase']).id
                Full_id = str(Location_id) + "-" + str(Usecase_id) + "-" + str(Item_id)
                Inventory_Item.objects.filter(id=Item_id).update(full_id=Full_id)

            else:  # no picture
                Inventory_Item.objects.create(name=request.POST['form_name'], vendor=request.POST['form_vendor'], usecase=request.POST['form_usecase'], location=request.POST['form_location'], group=request.POST['form_group'], description=request.POST['form_describtion'])
                if Inventory_item_LocationID.objects.filter(location_name=request.POST['form_location']).exists():
                    pass
                else:
                    Inventory_item_LocationID.objects.create(location_name=request.POST['form_location'])
                if Inventory_item_UsecaseID.objects.filter(usecase_name=request.POST['form_usecase']).exists():
                    pass
                else:
                    Inventory_item_UsecaseID.objects.create(usecase_name=request.POST['form_usecase'])
                Item_id = Inventory_Item.objects.get(name=request.POST['form_name'],vendor=request.POST['form_vendor']).id
                Location_id = Inventory_item_LocationID.objects.get(location_name=request.POST['form_location']).id
                Usecase_id = Inventory_item_UsecaseID.objects.get(usecase_name=request.POST['form_usecase']).id
                Full_id = str(Location_id) + "-" + str(Usecase_id) + "-" + str(Item_id)
                Inventory_Item.objects.filter(id=Item_id).update(full_id=Full_id)

        if request.POST['form_type'] == 'delete_item':
            print('Delete ID:', request.POST['id_to_delete'])
            Inventory_Item.objects.filter(id=request.POST['id_to_delete']).delete()
        if request.POST['form_type'] == 'view_item':
            id = request.POST['id_to_view']
            print('View ID:', id)
            return view_item(request, id=id)
        if request.POST['form_type'] == 'edit_item':
            print('Edit Entry:', request.POST['id'])
            print('Name:', request.POST['form_name'])
            print('Description:', request.POST['form_describtion'])
            if request.POST['form_picture'] != "": #Check for Picture
                Inventory_Item.objects.filter(id=request.POST['id']).update(name=request.POST['form_name'], vendor=request.POST['form_vendor'], usecase=request.POST['form_usecase'], location=request.POST['form_location'], group=request.POST['form_group'], description=request.POST['form_describtion'], picture=request.FILES['form_picture'])
            else: #no Picture
                Inventory_Item.objects.filter(id=request.POST['id']).update(name=request.POST['form_name'], vendor=request.POST['form_vendor'], usecase=request.POST['form_usecase'], location=request.POST['form_location'], group=request.POST['form_group'], description=request.POST['form_describtion'])
    return render(request, 'home.html', {'all_items': all_items, 'title': 'Home'})
def add_item(request):
    return render(request, 'add_item.html', {'title': 'Add Item'})
def vendors(request, vendor=None):
    type = "Vendor"
    if vendor == None:
        type = "Vendors"
        all_items = Inventory_Item.objects.all()
        ul_vendors = []
        for itm in all_items:
            ul_vendors.append(itm.vendor)
        all_vendors = list(dict.fromkeys(ul_vendors))
        all_vendors.sort()
        all_vendors = list(filter(None, all_vendors))
        return render(request, 'sortedby.html', {'all_detail_items': all_vendors, 'layout': "vendors", 'title': type})
    else:
        vendor_items = Inventory_Item.objects.filter(vendor=vendor)
        return render(request, 'items_sorted.html', {'all_items': vendor_items, 'title': type})
def groups(request, group=None):
    type = "Group"
    if group == None:
        type = "Groups"
        all_items = Inventory_Item.objects.all()
        ul_groups = []
        for itm in all_items:
            ul_groups.append(itm.group)
        all_groups = list(dict.fromkeys(ul_groups))
        all_groups.sort()
        all_groups = list(filter(None, all_groups))
        return render(request, 'sortedby.html', {'all_detail_items': all_groups, 'layout': "groups", 'type': type})
    else:
        group_items = Inventory_Item.objects.filter(group=group)
        return render(request, 'items_sorted.html', {'all_items': group_items, 'type': type})
def locations(request, location=None):
    type = "Location"
    if location == None:
        type = "Locations"
        all_items = Inventory_Item.objects.all()
        ul_locations = []
        for itm in all_items:
            ul_locations.append(itm.location)
        all_locations = list(dict.fromkeys(ul_locations))
        all_locations.sort()
        all_locations = list(filter(None, all_locations))
        return render(request, 'sortedby.html', {'all_detail_items': all_locations, 'layout': "locations", 'type': type})
    else:
        location_items = Inventory_Item.objects.filter(location=location)
        return render(request, 'items_sorted.html', {'all_items': location_items, 'type': type})

def usecases(request, usecase=None):
    type = "Usecase"
    if usecase == None:
        type = "Usecases"
        all_items = Inventory_Item.objects.all()
        ul_usecases = []
        for itm in all_items:
            ul_usecases.append(itm.usecase)
        all_usecases = list(dict.fromkeys(ul_usecases))
        all_usecases.sort()
        all_usecases = list(filter(None, all_usecases))
        return render(request, 'sortedby.html', {'all_detail_items': all_usecases, 'layout': "usecases", 'type': type})
    else:
        usecase_items = Inventory_Item.objects.filter(usecase=usecase)
        return render(request, 'items_sorted.html', {'all_items': usecase_items, 'type': type})

def search(request):
    if request.method == 'POST':
        if request.POST['form_type'] == 'search':
            type = "Searchresult: \"%s\"" % request.POST['search']
            print('Search:', request.POST['search'])
            search_items_name = Inventory_Item.objects.filter(name__icontains=request.POST['search'])
            search_items_vendor = Inventory_Item.objects.filter(vendor__icontains=request.POST['search'])
            search_items_usecase = Inventory_Item.objects.filter(usecase__icontains=request.POST['search'])
            search_items_location = Inventory_Item.objects.filter(location__icontains=request.POST['search'])
            search_items_group = Inventory_Item.objects.filter(group__icontains=request.POST['search'])
            search_items_full_id = Inventory_Item.objects.filter(full_id=request.POST['search'])
            search_items = search_items_name | search_items_vendor | search_items_usecase | search_items_location | search_items_group | search_items_full_id
            if search_items.count() == 0:
                messages.error(request, 'No Items found!')
                print('No Items found!')
            if search_items.count() == 1:
                print(search_items[0].id)
                return redirect('view_item', id=search_items[0].id)

            return render(request, 'items_sorted.html', {'all_items': search_items, 'title': type})
    else:
        return render(request, 'items_sorted.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                permission = view_site(user)
                print(permission)
                if permission:
                    login(request, user)
                    return redirect('/')
                else:
                    messages.success(request, 'You have no permission to view this site')
                    return render(request, 'login.html', {'type': 'Login'})
            else:
                messages.success(request, 'Your account has been disabled')
                return render(request, 'login.html', {'type': 'Login'})
        else:
            messages.error(request, 'Invalid login')
            return render(request, 'login.html', {'type': 'Login'})
    return render(request, 'login.html', {'type': 'Login'})

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return HttpResponseRedirect('/')


def view_site(user):
    return user.groups.filter(name__in=['Web_User', 'Admin']).exists()

def lable(request, id):
    item = Inventory_Item.objects.filter(id=id)
    code = gen_barcode(item[0].full_id)
    context = {'item': item, 'name': 'Name', 'vendor': 'Vendor', 'usecase': 'Usecase', 'location': 'Location', 'group': 'Group', 'code': code}
    img = print_lable('lable.html', context)
    context.update({'pdf': img})
    #return HttpResponse(pdf, content_type='application/pdf')
    return render(request, 'lable.html', context=context)


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        # getting the template
        pdf = html_to_pdf('result.html')

        # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')