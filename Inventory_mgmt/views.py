import django.shortcuts
import requests
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import *
from .functions import *
from Inventory_Managment import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.templatetags.static import static
from django.core.serializers import serialize
import json
from django.db.models import Q
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _


# Create your views here.


def view_item(request, id=None):
    user = request.user
    print_server = PrintServer.objects.all()
    default_print_server = Inventory_Settings.objects.get(id=1).print_server
    try:
        item = Inventory_Item.objects.filter(id=id, user_id=user.id)
    except:
        print('ID' + request.POST['item_id'])
        item = Inventory_Item.objects.filter(id=request.POST['item_id'], user_id=user.id)
    else:
        pass
    if request.method == 'POST':
        if request.POST['form_type'] == 'item_buttons':
            if request.POST['action'] == 'print_lable':
                item = Inventory_Item.objects.get(id=request.POST['item_id'])
                message = print_lable(item, q=request.POST['q'], psid=request.POST['ps'])
                messages.success(request, message)
                return redirect('/view_item/' + request.POST['item_id'])
        if request.POST['form_type'] == 'export':
            if request.POST['export_type'] == 'csv':
                response = export_csv(item)
            if request.POST['export_type'] == 'json':
                response = export_json(item)
            if request.POST['export_type'] == 'yaml':
                response = export_yaml(item)
            return response
    if type(id) == int:
        return render(request, 'view_item.html', {'item': item, 'ps': print_server, 'dps': default_print_server, 'title': _('View Item')})
    else:
        messages.error(request, 'Item not found')
        return render(request, 'view_item.html', {'title': _('View Item')})


def edit_item(request, id=None):
    user = request.user
    if type(id) == int:
        item = Inventory_Item.objects.filter(id=id, user_id=user.id)
        vendors_list = Inventory_Item.objects.values_list(
            'vendor', flat=True).distinct()
        usecases_list = Inventory_Item.objects.values_list(
            'usecase', flat=True).distinct()
        locations_list = Inventory_Item.objects.values_list(
            'location', flat=True).distinct()
        groups_list = Inventory_Item.objects.values_list(
            'group', flat=True).distinct()
        return render(request, 'edit_item.html', {'item': item, 'title': _('Edit Item'), 'vendors_list': vendors_list, 'usecases_list': usecases_list, 'locations_list': locations_list, 'groups_list': groups_list})
    else:
        messages.error(request, 'Item not found')
        return render(request, 'edit_item.html', {'title': _('Edit Item')})


def home(request):
    user = request.user
    all_items = Inventory_Item.objects.filter(user_id=user.id)
    item_count = Inventory_Item.objects.filter(user_id=user.id).count()
    try:
        last_item = all_items.latest('created_at')
    except:
        last_item = None

    if request.method == 'POST':
        if request.POST['form_type'] == 'import-csv':
            filename = request.FILES['import_csv'].name
            if filename.endswith('.csv'):
                print('Import CSV')
                import_csv(request.FILES['import_csv'], user.id)
            if filename.endswith('.json'):
                print('Import JSON')
                import_json(request.FILES['import_csv'], user.id)
            if filename.endswith('.yaml') or filename.endswith('.yml') :
                print('Import YAML')
                import_yaml(request.FILES['import_csv'], user.id)
            
            return redirect('/')
        if request.POST['form_type'] == 'update_numbers':
            print('Update numbers')
            update_number_table()
            messages.success(request, 'Numbers updated')
            return redirect('/')
        if request.POST['form_type'] == 'additem':
            # Check for picture
            print('Recieved Data:', request.POST['form_name'])
            if request.POST['form_vendor'] == "n/a":
                form_vendor = "unknown"
            else:
                form_vendor = request.POST['form_vendor']
            if request.POST['form_picture'] != "":
                new_item = Inventory_Item.objects.create(name=request.POST['form_name'], vendor=form_vendor, usecase=request.POST['form_usecase'], location=request.POST['form_location'],
                                              group=request.POST['form_group'], description=request.POST['form_describtion'], picture=request.FILES['form_picture'], amount=request.POST['form_amount'], user_id=user.id)
                if Inventory_item_LocationID.objects.filter(location_name=request.POST['form_location']).exists():
                    pass
                else:
                    Inventory_item_LocationID.objects.create(
                        location_name=request.POST['form_location'])
                if Inventory_item_UsecaseID.objects.filter(usecase_name=request.POST['form_usecase']).exists():
                    pass
                else:
                    Inventory_item_UsecaseID.objects.create(
                        usecase_name=request.POST['form_usecase'])
                #Item_id = Inventory_Item.objects.get(name=request.POST['form_name'], vendor=request.POST['form_vendor']).id
                Item_id =new_item.id
                Location_id = Inventory_item_LocationID.objects.get(
                    location_name=request.POST['form_location']).id
                Usecase_id = Inventory_item_UsecaseID.objects.get(
                    usecase_name=request.POST['form_usecase']).id
                Full_id = str(Location_id) + "-" + \
                    str(Usecase_id) + "-" + str(Item_id)
                Inventory_Item.objects.filter(
                    id=Item_id).update(full_id=Full_id)

            else:  # no picture
                new_item = Inventory_Item.objects.create(name=request.POST['form_name'], vendor=form_vendor, usecase=request.POST['form_usecase'], location=request.POST[
                                              'form_location'], group=request.POST['form_group'], description=request.POST['form_describtion'], amount=request.POST['form_amount'], user_id=user.id)
                if Inventory_item_LocationID.objects.filter(location_name=request.POST['form_location']).exists():
                    pass
                else:
                    Inventory_item_LocationID.objects.create(
                        location_name=request.POST['form_location'])
                if Inventory_item_UsecaseID.objects.filter(usecase_name=request.POST['form_usecase']).exists():
                    pass
                else:
                    Inventory_item_UsecaseID.objects.create(
                        usecase_name=request.POST['form_usecase'])
                    
                #Item_id = Inventory_Item.objects.get(name=request.POST['form_name'], vendor=request.POST['form_vendor']).id
                Item_id =new_item.id
                Location_id = Inventory_item_LocationID.objects.get(
                    location_name=request.POST['form_location']).id
                Usecase_id = Inventory_item_UsecaseID.objects.get(
                    usecase_name=request.POST['form_usecase']).id
                Full_id = str(Location_id) + "-" + \
                    str(Usecase_id) + "-" + str(Item_id)
                Inventory_Item.objects.filter(
                    id=Item_id).update(full_id=Full_id)

        if request.POST['form_type'] == 'delete_item':
            print('Delete ID:', request.POST['id_to_delete'])
            Inventory_Item.objects.filter(
                id=request.POST['id_to_delete'], user_id=user.id).delete()
        if request.POST['form_type'] == 'view_item':
            id = request.POST['id_to_view']
            print('View ID:', id)
            return view_item(request, id=id)
        if request.POST['form_type'] == 'edit_item':
            print('Edit Entry:', request.POST['id']+'-'+request.POST['form_name'])
            if request.POST['form_vendor'] == "n/a":
                form_vendor = "unknown"
            else:
                form_vendor = request.POST['form_vendor']
            if request.POST['form_picture'] != "":  # Check for Picture
                Inventory_Item.objects.filter(id=request.POST['id'], user_id=user.id).update(name=request.POST['form_name'], vendor=form_vendor, usecase=request.POST['form_usecase'], location=request.POST['form_location'],
                                                                            group=request.POST['form_group'], description=request.POST['form_describtion'], picture=request.FILES['form_picture'], amount=request.POST['form_amount'])
            else:  # no Picture
                Inventory_Item.objects.filter(id=request.POST['id'], user_id=user.id).update(name=request.POST['form_name'], vendor=form_vendor, usecase=request.POST['form_usecase'],
                                                                            location=request.POST['form_location'], group=request.POST['form_group'], description=request.POST['form_describtion'], amount=request.POST['form_amount'])
            return redirect('/view_item/' + request.POST['id'])
        if request.POST['form_type'] == 'export':
            if request.POST['export_type'] == 'csv':
                response = export_csv(all_items)
            if request.POST['export_type'] == 'json':
                response = export_json(all_items)
            if request.POST['export_type'] == 'yaml':
                response = export_yaml(all_items)
            return response
        
    if request.method == 'GET':
        pass
    return render(request, 'home.html', {'title': _('Home'), 'last_item': last_item, 'item_count': item_count})

def all(request):
    user = request.user
    all_items = Inventory_Item.objects.filter(user_id=user.id)
    if request.method == 'POST':
        if request.POST['form_type'] == 'bulkDelete':
            #print(request.POST)
            for entry in request.POST:
                if entry != 'form_type' and entry != 'csrfmiddlewaretoken':
                    print("Delete Item: ", entry)
                    Inventory_Item.objects.filter(id=entry, user_id=user.id).delete()

            return render(request, 'all.html', {'all_items': all_items, 'title': _('All')})
    elif request.method == 'GET':
           
        return render(request, 'all.html', {'all_items': all_items,'url': 'all', 'title': _('All')})

    


def add_item(request):
    vendors_list = Inventory_Item.objects.values_list(
        'vendor', flat=True).distinct()
    usecases_list = Inventory_Item.objects.values_list(
        'usecase', flat=True).distinct()
    locations_list = Inventory_Item.objects.values_list(
        'location', flat=True).distinct()
    groups_list = Inventory_Item.objects.values_list(
        'group', flat=True).distinct()
    
    return render(request, 'add_item.html', {'title': _('Add Item'), 'vendors_list': vendors_list, 'usecases_list': usecases_list, 'locations_list': locations_list, 'groups_list': groups_list})


def vendors(request, vendor=None):
    user = request.user
    type = "Vendor"
    if vendor == None:
        if request.method == 'POST':
            print(request.POST)
            category = request.POST['catName']
            new_Category = request.POST['newName']
            cat_items = Inventory_Item.objects.filter(vendor=category, user_id=user.id)
            for item in cat_items:
                item.vendor = new_Category
                item.save()
            return redirect('/vendors')
        type = "Vendors"
        all_items = Inventory_Item.objects.filter(user_id=user.id)
        ul_vendors = []
        for itm in all_items:
            ul_vendors.append(itm.vendor)
        all_vendors = list(dict.fromkeys(ul_vendors))
        all_vendors.sort()
        all_vendors = list(filter(None, all_vendors))
        return render(request, 'sortedby.html', {'all_detail_items': all_vendors, 'layout': "vendors", 'title': _(type)})
    else:
        type = _("Vendor") + " - " + vendor
        vendor_items = Inventory_Item.objects.filter(vendor=vendor, user_id=user.id)
        if request.method == 'POST':
            if request.POST['form_type'] == 'export':
                print('Export')
                if request.POST['export_type'] == 'csv':
                    response = export_csv(vendor_items)
                if request.POST['export_type'] == 'json':
                    response = export_json(vendor_items)
                if request.POST['export_type'] == 'yaml':
                    response = export_yaml(vendor_items)

                return response
        return render(request, 'items_sorted.html', {'all_items': vendor_items, 'title': type})


def groups(request, group=None):
    user = request.user
    type = "Group"
    if group == None:
        if request.method == 'POST':
            print(request.POST)
            category = request.POST['catName']
            new_Category = request.POST['newName']
            cat_items = Inventory_Item.objects.filter(group=category, user_id=user.id)
            for item in cat_items:
                item.group = new_Category
                item.save()
            return redirect('/groups')
        type = "Groups"
        all_items = Inventory_Item.objects.filter(user_id=user.id)
        ul_groups = []
        for itm in all_items:
            ul_groups.append(itm.group)
        all_groups = list(dict.fromkeys(ul_groups))
        all_groups.sort()
        all_groups = list(filter(None, all_groups))
        return render(request, 'sortedby.html', {'all_detail_items': all_groups, 'layout': "groups", 'title': _(type)})
    else:
        type = _("Group") + " - " + group
        group_items = Inventory_Item.objects.filter(group=group, user_id=user.id)
        if request.method == 'POST':
            if request.POST['form_type'] == 'export_csv':
                response = export_csv(group_items)
                return response
        return render(request, 'items_sorted.html', {'all_items': group_items, 'title': type})


def locations(request, location=None):
    user = request.user
    type = "Location"
    if location == None:
        if request.method == 'POST':
            print(request.POST)
            category = request.POST['catName']
            new_Category = request.POST['newName']
            cat_items = Inventory_Item.objects.filter(location=category, user_id=user.id)
            for item in cat_items:
                item.location = new_Category
                item.save()
            return redirect('/locations')
        type = "Locations"
        all_items = Inventory_Item.objects.filter(user_id=user.id)
        ul_locations = []
        for itm in all_items:
            ul_locations.append(itm.location)
        all_locations = list(dict.fromkeys(ul_locations))
        all_locations.sort()
        all_locations = list(filter(None, all_locations))
        return render(request, 'sortedby.html', {'all_detail_items': all_locations, 'layout': "locations", 'title': _(type)})
    else:
        type = _("Location") + " - " + str(location)
        location_items = Inventory_Item.objects.filter(location=location, user_id=user.id)
        if request.method == 'POST':
            if request.POST['form_type'] == 'export_csv':
                response = export_csv(location_items)
                return response
        return render(request, 'items_sorted.html', {'all_items': location_items, 'title': type})


def usecases(request, usecase=None):
    user = request.user
    type = "Usecase"
    if usecase == None:
        if request.method == 'POST':
            print(request.POST)
            category = request.POST['catName']
            new_Category = request.POST['newName']
            cat_items = Inventory_Item.objects.filter(usecase=category, user_id=user.id)
            for item in cat_items:
                item.usecase = new_Category
                item.save()
            return redirect('/usecases')
        type = "Usecases"
        all_items = Inventory_Item.objects.filter(user_id=user.id)
        ul_usecases = []
        for itm in all_items:
            ul_usecases.append(itm.usecase)
        all_usecases = list(dict.fromkeys(ul_usecases))
        all_usecases.sort()
        all_usecases = list(filter(None, all_usecases))
        return render(request, 'sortedby.html', {'all_detail_items': all_usecases, 'layout': "usecases", 'title': _(type)})
    else:
        type = _("Usecase") + " - " + str(usecase)
        usecase_items = Inventory_Item.objects.filter(usecase=usecase, user_id=user.id)
        if request.method == 'POST':
            if request.POST['form_type'] == 'export_csv':
                response = export_csv(usecase_items)
                return response
        return render(request, 'items_sorted.html', {'all_items': usecase_items, 'title': type})


def search(request, full_id=None):
    user = request.user
    if request.method == 'POST':
        if request.POST['form_type'] == 'search':
            type = "Searchresult: \"%s\"" % request.POST['search']
            print('Search:', request.POST['search'])
            search_items_name = Inventory_Item.objects.filter(
                name__icontains=request.POST['search'], user_id=user.id)
            search_items_vendor = Inventory_Item.objects.filter(
                vendor__icontains=request.POST['search'], user_id=user.id)
            search_items_usecase = Inventory_Item.objects.filter(
                usecase__icontains=request.POST['search'], user_id=user.id)
            search_items_location = Inventory_Item.objects.filter(
                location__icontains=request.POST['search'], user_id=user.id)
            search_items_group = Inventory_Item.objects.filter(
                group__icontains=request.POST['search'], user_id=user.id)
            search_items_full_id = Inventory_Item.objects.filter(
                full_id=request.POST['search'], user_id=user.id)
            search_items = search_items_name | search_items_vendor | search_items_usecase | search_items_location | search_items_group | search_items_full_id
            if search_items.count() == 0:
                messages.error(request, 'No Items found!')
                print('No Items found!')
            if search_items.count() == 1:
                print(search_items[0].id)
                return redirect('view_item', id=search_items[0].id)

            return render(request, 'items_sorted.html', {'all_items': search_items, 'title': _(type)})

    if full_id != None:
        print('Search:', full_id)
        search_items_full_id = Inventory_Item.objects.filter(full_id=full_id, user_id=user.id)
        if search_items_full_id.count() == 0:
            messages.error(request, 'No Items found!')
            print('No Items found!')
        if search_items_full_id.count() == 1:
            print(search_items_full_id[0].id)
            return redirect('view_item', id=search_items_full_id[0].id)
        return render(request, 'items_sorted.html', {'all_items': search_items_full_id, 'title': _(type)})

    else:
        return render(request, 'items_sorted.html')


def login_user(request):
    try:
        autologinkey = request.GET['autologinkey']
    except:
        autologinkey = None
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
                    messages.success(
                        request, 'You have no permission to view this site')
                    return render(request, 'login.html', {'type': 'Login'})
            else:
                messages.success(request, 'Your account has been disabled')
                return render(request, 'login.html', {'type': 'Login'})
        else:
            messages.error(request, 'Invalid login')
            return render(request, 'login.html', {'type': 'Login'})
    elif autologinkey != None:
        try:                
            auto_login_user = UserProfile.objects.get(auto_login_key=autologinkey).user
            login(request, auto_login_user)
            messages.success(request, 'You are loged in with an Autologin Key')
        except:
            messages.success(request, 'This Autologin Key is Invalid')
       


    return render(request, 'login.html', {'type': _('Login')})


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return HttpResponseRedirect('/')


def view_site(user):
    return user.groups.filter(name__in=['Web_User', 'Admin']).exists()

@csrf_exempt
def api(request, api_key=None):
    if api_key != None:
        try:
            api_key_obj = UserProfile.objects.get(api_key=api_key)
        except:
            api_key_obj = None
        if api_key_obj != None:
            api_user_id = api_key_obj.user.id
            return_data = api_query(request, api_user_id)
        else:
            return_data = json.dumps({"error": "Please enter an valid API-Key to use the API"})
    elif 'hwkey' in request.GET:
        hwkey = request.GET['hwkey']
        try:
            hwkey_obj = UserClients.objects.get(hwkey=hwkey)
        except:
            hwkey_obj = None
        if  hwkey_obj != None:
            client_user_id =  hwkey_obj.user.id
            return_data = api_query(request, client_user_id)
            UserClients.objects.filter(pk=hwkey_obj.pk).update(last_login=datetime.now())
        else:
            return_data = json.dumps({'error': 'The given Hardware Key is not registered on this Server'})
    else:
        return_data = json.dumps({'error': 'Please enter an API-Key to use the API'})

    return HttpResponse(return_data, content_type='application/json')

def api_query(request, user_id):
    method = request.method
    if method == 'GET':
        data = request.GET
    elif method == "POST":
        data = request.POST
    else:
        return HttpResponse("Invalid HTTP Method", status=405)
    if request.method == method:
        if request.method == method and 'type' in data:
            if data['type'] == 'get':
                q = Q()
                try:
                    full_id = data['full_id']
                    q |= Q(**{'full_id': full_id})
                except:
                    pass
                try:
                    name = data['name']
                    q |= Q(**{'name': name})
                except:
                    pass
                try:
                    vendor = data['group']
                    q |= Q(**{'group': vendor})
                except:
                    pass
                try:
                    vendor = data['vendor']
                    q |= Q(**{'vendor': vendor})
                except:
                    pass
                try:
                    usecase = data['usecase']
                    q |= Q(**{'usecase': usecase})
                except:
                    pass
                try:
                    location = data['location']
                    q |= Q(**{'location': location})
                except:
                    pass
                try:
                    created_at = data['created_at']
                    q |= Q(**{'created_at': created_at})
                except:
                    pass
                try:
                    item_picture = data['picture']
                    q |= Q(**{'picture': item_picture})
                except:
                    pass
                
                item = Inventory_Item.objects.filter(q, user_id=user_id)
                return_data = serialize('json', item, fields=('full_id', 'name', 'amount', 'vendor', 'group', 'usecase', 'location', 'description', 'created_at', 'picture'))
            
            # API for getting all Items sorted by categories
            
            elif data['type'] == 'getCat':
                if data['cat'] == 'group':
                    all_items = Inventory_Item.objects.filter(user_id=user_id)
                    ul_vendors = []
                    for itm in all_items:
                        ul_vendors.append(itm.group)
                    all_usecases = list(dict.fromkeys(ul_vendors))
                    all_usecases.sort()
                    all_usecases = list(filter(None, all_usecases))
                    sorted_by_vendor = {}
                    for vendor in all_usecases:
                        usecase_items = Inventory_Item.objects.filter(user_id=user_id, group=vendor)
                        usecase_items_new = serialize('json', usecase_items, fields=('full_id', 'name', 'amount', 'vendor', 'group', 'usecase', 'location', 'description', 'created_at', 'picture'))
                        globals()[vendor] = {
                            'name': vendor,
                            'items': json.loads(usecase_items_new)
                        }
                        sorted_by_vendor[vendor] = globals()[vendor]
                    return_data = json.dumps(sorted_by_vendor)
                
                elif data['cat'] == 'vendor':
                    all_items = Inventory_Item.objects.filter(user_id=user_id)
                    ul_vendors = []
                    for itm in all_items:
                        ul_vendors.append(itm.vendor)
                    all_usecases = list(dict.fromkeys(ul_vendors))
                    all_usecases.sort()
                    all_usecases = list(filter(None, all_usecases))
                    sorted_by_vendor = {}
                    for vendor in all_usecases:
                        usecase_items = Inventory_Item.objects.filter(user_id=user_id, vendor=vendor)
                        usecase_items_new = serialize('json', usecase_items, fields=('full_id', 'name', 'amount', 'vendor', 'group', 'usecase', 'location', 'description', 'created_at', 'picture'))
                        globals()[vendor] = {
                            'name': vendor,
                            'items': json.loads(usecase_items_new)
                        }
                        sorted_by_vendor[vendor] = globals()[vendor]
                    return_data = json.dumps(sorted_by_vendor)
                
                elif data['cat'] == 'usecase':
                    all_items = Inventory_Item.objects.filter(user_id=user_id)
                    ul_usecase = []
                    for itm in all_items:
                        ul_usecase.append(itm.usecase)
                    all_usecases = list(dict.fromkeys(ul_usecase))
                    all_usecases.sort()
                    all_usecases = list(filter(None, all_usecases))
                    sorted_by_usecase = {}
                    for usecase in all_usecases:
                        usecase_items = Inventory_Item.objects.filter(user_id=user_id, usecase=usecase)
                        usecase_items_new = serialize('json', usecase_items, fields=('full_id', 'name', 'amount', 'vendor', 'group', 'usecase', 'location', 'description', 'created_at', 'picture'))
                        globals()[usecase] = {
                            'name': usecase,
                            'items': json.loads(usecase_items_new)
                        }
                        sorted_by_usecase[usecase] = globals()[usecase]
                    return_data = json.dumps(sorted_by_usecase)
                    
                elif data['cat'] == 'location':
                    all_items = Inventory_Item.objects.filter(user_id=user_id)
                    ul_locations = []
                    for itm in all_items:
                        ul_locations.append(itm.location)
                    all_locations = list(dict.fromkeys(ul_locations))
                    all_locations.sort()
                    all_locations = list(filter(None, all_locations))
                    sorted_by_location = {}
                    for location in all_locations:
                        location_items = Inventory_Item.objects.filter(user_id=user_id, location=location)
                        location_items_new = serialize('json', location_items, fields=('full_id', 'name', 'amount', 'vendor', 'group', 'usecase', 'location', 'description', 'created_at', 'picture'))
                        globals()[location] = {
                            'name': location,
                            'items': json.loads(location_items_new)
                        }
                        sorted_by_location[location] = globals()[location]
                    return_data = json.dumps(sorted_by_location)
                    
                else:
                    return_data = json.dumps("Please Specify a Category")
            
            
            elif data['type'] == 'edit':
                if request.method == method and 'id' in data:
                    edit_id = data['id']
                    item = Inventory_Item.objects.filter(id=edit_id, user_id=user_id)
                    if 'name' in data:
                        item.update(name=data['name'])
                    if 'amount' in data:
                        item.update(amount=data['amount'])
                    if 'vendor' in data:
                        item.update(vendor=data['vendor'])
                    if 'group' in data:
                        item.update(group=data['group'])
                    if 'usecase' in data:
                        item.update(usecase=data['usecase'])
                    if 'location' in data:
                        item.update(location=data['location'])
                    if 'description' in data:
                        item.update(description=data['description'])
                    confirm_str = json.dumps('Item edited')
                    return_data = confirm_str
                else:
                    return_data = json.dumps({'error': 'Please specify an ID to edit'})
            
            elif data['type'] == 'add':
                if request.method == method and 'name' in data:
                    if data['name'] != '':
                        name = data['name']
                        vendor = data['vendor']
                        vendor = data['group']
                        usecase = data['usecase']
                        location = data['location']
                        description = data['description']
                        amount = data['amount']
                        Inventory_Item.objects.create(name=name, vendor=vendor, group=vendor, usecase=usecase, location=location, description=description, amount=amount, user_id=user_id)
                        if Inventory_item_LocationID.objects.filter(location_name=location).exists():
                            pass
                        else:
                            Inventory_item_LocationID.objects.create(
                                location_name=location)
                        if Inventory_item_UsecaseID.objects.filter(usecase_name=usecase).exists():
                            pass
                        else:
                            Inventory_item_UsecaseID.objects.create(
                                usecase_name=usecase)
                        Item_id = Inventory_Item.objects.get(
                            name=name, vendor=vendor).id
                        Location_id = Inventory_item_LocationID.objects.get(
                            location_name=location).id
                        Usecase_id = Inventory_item_UsecaseID.objects.get(
                            usecase_name=usecase).id
                        Full_id = str(Location_id) + "-" + \
                            str(Usecase_id) + "-" + str(Item_id)
                        Inventory_Item.objects.filter(
                            id=Item_id).update(full_id=Full_id)
                        
                        
                        confirm_str = json.dumps({'success': 'Item added'})
                        return_data = confirm_str
                    else:
                        return_data = json.dumps({'error': 'Please specify a name to add an item'})
                else:
                    return_data = json.dumps({'error': 'Please specify a name to add an item'})
            
            elif data['type'] == 'delete':
                if request.method == method and 'id' in data:
                    delete_id = data['id']
                    Inventory_Item.objects.filter(id=delete_id, user_id=user_id).delete()
                    confirm_str = json.dumps(f'Item {delete_id} deleted')
                    return_data = confirm_str
                else:
                    return_data = json.dumps({'error': 'Please specify an ID to delete'})   
        else:
            return_data = json.dumps({'error': 'Please specify a type to use the API'})

    return return_data


def user_settings(request):
    papers = read_paper_file()
    papers_json = json.dumps(papers)
    user = request.user
    print_config = Inventory_Settings.objects.filter(id=1)
    pserver_def_uuid = Inventory_Settings.objects.get(id=1).print_server
    print_server = PrintServer.objects.all()
    
    try:
        api_key = UserProfile.objects.get(user=request.user).api_key
    except:
        api_key = ''
    try:
        auto_login_key = UserProfile.objects.get(user=request.user).auto_login_key
    except:
        auto_login_key = ''
        
    try:
        clients = UserClients.objects.filter(user=request.user)
    except:
        pass
    
    if request.method == 'POST':
        if request.POST['form_type'] == 'set_pserver':
            print_server = request.POST['pserver']
            print_server = PrintServer.objects.get(uuid=print_server)
            Inventory_Settings.objects.filter(id=1).update(print_server=print_server)
            return HttpResponseRedirect("/settings#5")
        if request.POST["form_type"] == 'delete-pserver':
            if 'server-uuid' in request.POST:
                server_uuid = request.POST['server-uuid']
                PrintServer.objects.get(uuid=server_uuid).delete()
                return HttpResponseRedirect("/settings")
        if request.POST["form_type"] == 'delete-client':
            if 'client-hwkey' in request.POST:
                client_hwkey = request.POST['client-hwkey']
                UserClients.objects.get(hwkey=client_hwkey).delete()
                return HttpResponseRedirect("/settings")
                
        if request.POST['form_type'] == 'gen-api-key':
            api_key = random_string(32)
            try:
                UserProfile.objects.update_or_create(user=request.user, api_key=api_key)
            except:
                UserProfile.objects.filter(user=request.user).update(api_key=api_key)
        if request.POST['form_type'] == 'gen-auto-login-key':
            auto_login_key = random_string(64)
            try:
                UserProfile.objects.update_or_create(user=request.user, auto_login_key=auto_login_key)
            except:
                UserProfile.objects.filter(user=request.user).update(auto_login_key=auto_login_key)

        if request.POST['form_type'] == 'update_user':
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            if request.POST['password']:
                user.set_password(request.POST['password'])
            user.save()
        if request.POST['form_type'] == 'print_settings':
            print_config.update(paper_name=request.POST['paper'], printer_name=request.POST['printer_name'], paper_width=request.POST['paper_width'], paper_height=request.POST['paper_height'], paper_orientation=request.POST['paper_orientation'], print_file_name=request.POST['print_file_name'])

    return render(request, 'settings.html', {'papers_json':papers_json, 'papers': papers, 'title': 'Settings', 'auto_login_key': auto_login_key, 'api_key': api_key, 'user': user, 'print_config_obj': print_config, 'print_server': print_server, 'pserver_def_uuid': pserver_def_uuid, 'debug': settings.DEBUG, 'clients': clients})


def remote_print(request):
    try:
        api_key = request.GET['api_key']
    except:
        api_key = None
        pass
    try:
        print_id = request.GET['print_id'] 
    except:
        print_id = None
        pass
    try:
        hw_key = request.GET['hwkey']
    except:
        hw_key = None
        pass

    if api_key != None:
        user_id = UserProfile.objects.get(api_key=api_key).user.id
        if print_id != None:
            print_item = Inventory_Item.objects.get(user_id=user_id, full_id=print_id)
            message, print_cmd = print_lable(print_item)
            response_string = f'Message: {message}; Output: {print_cmd}'
            response = json.dumps(response_string)
        else:
            response_string = 'No Item ID to Print was given. Abort!'
            response = json.dumps(response_string)
    
    elif hw_key != None:
        user_id = UserClients.objects.get(hwkey=hw_key).user.id
        if print_id != None:
            print_item = Inventory_Item.objects.get(user_id=user_id, full_id=print_id)
            message, print_cmd = print_lable(print_item)
            response_string = f'Message: {message}; Output: {print_cmd}'
            response = json.dumps(response_string)
        else:
            response_string = 'No Item ID to Print was given. Abort!'
            response = json.dumps(response_string)

    else:
        user_id = None
        response_string = 'No API key was specified. Abort!'
        response = json.dumps(response_string)
    with open('remote_print.log', 'w') as log_file:
        date_time = datetime.now().strftime('%D.%M.%Y - %H:%M:%S')
        log_string = f'{date_time} Remote Print requested by UserID: {user_id}  Response: {response_string}'
        log_file.write(log_string)

    return HttpResponse(response, content_type='application/json')

def register_device(request, device_name, os):

    user = request.user
    if user.is_authenticated:
        pass
    else:
        if 'username' in request.GET and 'password' in request.GET:
            username = request.GET['username']
            password = request.GET['password']
        else:
            return JsonResponse({'status':'error', 'error': 'You have to log in. Please specify a username and password'})   

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                permission = view_site(user)
                print(permission)
                if permission:
                    login(request, user)
                    print(f"User {username} logged in")
                else:
                    return JsonResponse({'status':'error', 'error': 'You have no permission to view this site'})
            else:
                return JsonResponse({'status':'error', 'error': 'Your account has been disabled'})
        else:
            return JsonResponse({'status':'error', 'error': 'Invalid login'})

    if 'hwkey' in request.GET:
        hw_key = request.GET['hwkey']
        try:
            if UserClients.objects.get(hwkey=hw_key):
                UserClients.objects.filter(hwkey=hw_key).update(user=user, os=os, name=device_name, last_login=datetime.today())
            else:
                UserClients.objects.create(user=user, os=os, name=device_name, last_login=datetime.now(), hwkey=hw_key)
        except:
            UserClients.objects.create(user=user, os=os, name=device_name, last_login=datetime.now(), hwkey=hw_key) 
        
        display_name_user = f'{user.first_name} {user.last_name}'
    
        return_dict = {
            'User': display_name_user , 'hw_key': hw_key, 'domain': settings.CSRF_TRUSTED_ORIGINS[0],  'status': 'success',
        }

    else:
        return JsonResponse({'status':'error', 'error': 'You have to specify the Hardware Key (hwkey)'})            

        
   
       
    
    
    
    logout(request)
    return JsonResponse(return_dict)

@csrf_exempt
def register_printserver(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        ip = request.POST['ip']
        port = request.POST['port']
        uuid = request.POST['uuid']
        
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                if PrintServer.objects.filter(uuid=uuid).exists():
                    return JsonResponse({'status':'error', 'error': 'This Print Server is already registered.'})
                else:
                    PrintServer.objects.create(name=name, ip=ip, port=port, uuid=uuid)
                    return JsonResponse({'status':'Print Server added successfully.', 'error': ''})
            else:
                return JsonResponse({'status':'error', 'error': 'You have no permission to add a Print Server'})
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    if PrintServer.objects.filter(uuid=uuid).exists():
                        return JsonResponse({'status':'error', 'error': 'This Print Server is already registered.'})
                    else:
                        PrintServer.objects.create(name=name, ip=ip, port=port, uuid=uuid)
                        return JsonResponse({'status':'Print Server added successfully.', 'error': ''})
                else:
                    return JsonResponse({'status':'error', 'error': 'You have no permission to add a Print Server'})
            else:
                return JsonResponse({'status':'error', 'error': 'Username or Password is incorrect'})