from os.path import join
import os
from Inventory_Managment import settings
from Inventory_Managment import config_file
from .models import *
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import code128
from html2image import Html2Image
import subprocess
from django.core.files.storage import default_storage
import pdfkit
import csv
import io
import subprocess
from datetime import datetime
from .printlable import *
from django.contrib.auth.models import User
import random
import string
import yaml
import json
from django.contrib.sites.models import Site
import requests



def update_number_table():
    all_items = Inventory_Item.objects.all()
    for item in all_items:
        if Inventory_item_LocationID.objects.filter(location_name=item.location).exists():
            pass
        else:
            Inventory_item_LocationID.objects.create(
                location_name=item.location)
        if Inventory_item_UsecaseID.objects.filter(usecase_name=item.usecase).exists():
            pass
        else:
            Inventory_item_UsecaseID.objects.create(usecase_name=item.usecase)
        #Item_id = Inventory_Item.objects.get(name=item.name, vendor=item.vendor).id
        Location_id = Inventory_item_LocationID.objects.get(
            location_name=item.location).id
        Usecase_id = Inventory_item_UsecaseID.objects.get(
            usecase_name=item.usecase).id
        Full_id = str(Location_id) + "-" + str(Usecase_id) + "-" + str(item.id)
        Inventory_Item.objects.filter(id=item.id).update(full_id=Full_id)

def print_lable(item, client="Webclient", q="1", psid=False):
    name = item.name
    id = item.full_id
    location = item.location
    amount = item.amount
    type = "print"
    if psid == False:
        ps = Inventory_Settings.objects.get(id=1).print_server
    else:
        ps = PrintServer.objects.get(id=psid)
    print(ps)
    url = f'http://{ps.ip}:{ps.port}/print'
    data = {'name': name, 'id': id, 'location': location, 'amount': amount, 'type': type, 'client': client, 'q': q}

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises an error for bad status codes
        json_msg = response.json()
        if json_msg['status'] == 'error':
            msg = json_msg['error']
        else:
            msg = json_msg['status']

        return msg
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

    


def print_lable_old(item):
    # text = """Name: {Name}
    # Amount: {Amount}
    # Location: {Location}""".format(Name=item.name, Amount=item.amount, Location=item.location)

    #dir = "/prj/Inventory_Managment_System_Django/"
    dir = ""

    text = f"Name: {item.name}\nAmount: {item.amount}\nLocation: {item.location}\nID: {item.full_id}"

    qr = item.full_id
    gen_print_label(text, qr=qr)
    printer = Inventory_Settings.objects.get(id=1).printer_name
    file_name = Inventory_Settings.objects.get(id=1).print_file_name
    file_name = f"{dir}{file_name}"
    width = Inventory_Settings.objects.get(id=1).paper_width
    height = Inventory_Settings.objects.get(id=1).paper_height
    orientation = Inventory_Settings.objects.get(id=1).paper_orientation
    cmd = f'lpr -P "{printer}" -o {orientation} -o media=Custom.{width}x{height}mm -o fit-to-page {file_name}'
    print_cmd = subprocess.call(cmd, shell=True)
    print(print_cmd)
    os.remove(str(file_name))
    if print_cmd == 0:
        message = 'Lable printed'
    else:
        if print_cmd == 1: 
            message = 'Lable not printed'
        else:
            message = 'Error'
    
    return message, print_cmd


def html_to_pdf(template_src, context_dict={}):

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def gen_barcode(id):
    path = join(settings.MEDIA_ROOT, 'barcodes', str(id) + '.png')
    code = code128.image(id).save(path)
    return path


def export_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Inventory_Export_{datetime.now().strftime("%d-%m-%Y")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Amount', 'Group', 'Vendor',
                    'Usecase', 'Location', 'Created at', 'Created by', 'Description'])
    for obj in queryset:
        username = User.objects.get(id=obj.user_id).username
        writer.writerow([obj.full_id, obj.name, obj.amount, obj.group, obj.vendor,
                        obj.usecase, obj.location, obj.created_at, username, obj.description])
    return response

def export_json(queryset):
    json_export_dict = {
        'objects':[]
    }
    for obj in queryset:
        temp_dict = {
                'id': obj.full_id,
                'name': obj.name,
                'amount': obj.amount,
                'group': obj.group,
                'vendor': obj.vendor,
                'usecase': obj.usecase,
                'location': obj.location,
                'created_at': str(obj.created_at),
                'created_by': User.objects.get(id=obj.user_id).username,
                'description': obj.description
            }
        
        json_export_dict['objects'].append(temp_dict)
    print(json_export_dict)
    json_export = json.dumps(json_export_dict, indent=4)
    response = HttpResponse(json_export, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="Inventory_Export{datetime.now().strftime("%d-%m-%Y")}.json"'
    return response

def export_yaml(queryset):
    yaml_export_dict = {
        'objects':[]
    }
    for obj in queryset:
        temp_dict = {
                'id': obj.full_id,
                'name': obj.name,
                'amount': obj.amount,
                'group': obj.group,
                'vendor': obj.vendor,
                'usecase': obj.usecase,
                'location': obj.location,
                'created_at': str(obj.created_at),
                'created_by': User.objects.get(id=obj.user_id).username,
                'description': obj.description
            }
        
        yaml_export_dict['objects'].append(temp_dict)
    print(yaml_export_dict)
    yaml_export = yaml.dump(yaml_export_dict)
    response = HttpResponse(yaml_export, content_type='application/yaml')
    response['Content-Disposition'] = f'attachment; filename="Inventory_Export{datetime.now().strftime("%d-%m-%Y")}.yaml"'
    return response

def import_csv(file, user_id):
    # with open(csv_file, 'r') as f:
    if file == None:
        return ('No file selected')
    csv_file = file.read().decode('utf-8')
    # reader = csv.reader(file)
    csv_data = csv_file.split("\n")
    # print(csv_data)
    print(type(csv_data))
    for line in csv_data:
        # print(line)
        row = line.split(",")
        print(row)
        print(type(row))
        if row[0] == 'ID':
            print('Header')
            print(row[0])
            continue
        if row[0] != 'ID':
            if Inventory_Item.objects.filter(name=row[1], vendor=row[4], usecase=row[5], location=row[6], group=row[3], user_id=user_id).exists():
                print('Item already exists')
                old_amount = Inventory_Item.objects.get(
                    name=row[1], vendor=row[4], usecase=row[5], location=row[6], group=row[3], user_id=user_id).amount
                print(old_amount)
                new_amount = int(old_amount) + int(row[2])
                print(new_amount)
                Inventory_Item.objects.filter(
                    name=row[1], vendor=row[4], usecase=row[5], location=row[6], group=row[3], user_id=user_id).update(amount=new_amount)
            else:
                # elif Inventory_Item.objects.filter(name=row[1], vendor=row[4], usecase=row[5], location=row[6], group=row[3], description=row[8]).exists() == False:
                Inventory_Item.objects.create(
                    name=row[1], vendor=row[4], usecase=row[5], location=row[6], group=row[3], description=row[8], amount=row[2], user_id=user_id)

                if Inventory_item_LocationID.objects.filter(location_name=row[6]).exists():
                    pass
                else:
                    Inventory_item_LocationID.objects.create(
                        location_name=row[6])
                if Inventory_item_UsecaseID.objects.filter(usecase_name=row[5]).exists():
                    pass
                else:
                    Inventory_item_UsecaseID.objects.create(
                        usecase_name=row[5])

                Item_id = Inventory_Item.objects.get(
                    name=row[1], vendor=row[4], created_at=datetime.today().strftime('%Y-%m-%d'), user_id=user_id).id
                Location_id = Inventory_item_LocationID.objects.get(
                    location_name=row[6]).id
                Usecase_id = Inventory_item_UsecaseID.objects.get(
                    usecase_name=row[5]).id
                Full_id = str(Location_id) + "-" + \
                    str(Usecase_id) + "-" + str(Item_id)
                Inventory_Item.objects.filter(
                    id=Item_id, user_id=user_id).update(full_id=Full_id)
                

def import_json(file, user_id):
    if file == None:
        return ('No file selected')
    json_file = file.read().decode('utf-8')
    json_data = json.loads(json_file)
    for obj in json_data['objects']:
        if Inventory_Item.objects.filter(name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], user_id=user_id).exists():
            print('Item already exists')
            old_amount = Inventory_Item.objects.get(
                name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], user_id=user_id).amount
            print(old_amount)
            new_amount = int(old_amount) + int(obj['amount'])
            print(new_amount)
            Inventory_Item.objects.filter(
                name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], user_id=user_id).update(amount=new_amount)
        else:
            Inventory_Item.objects.create(
                name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], description=obj['description'], amount=obj['amount'], user_id=user_id)

            if Inventory_item_LocationID.objects.filter(location_name=obj['location']).exists():
                pass
            else:
                Inventory_item_LocationID.objects.create(
                    location_name=obj['location'])
            if Inventory_item_UsecaseID.objects.filter(usecase_name=obj['usecase']).exists():
                pass
            else:
                Inventory_item_UsecaseID.objects.create(
                    usecase_name=obj['usecase'])

            Item_id = Inventory_Item.objects.get(
                name=obj['name'], vendor=obj['vendor'], created_at=datetime.today().strftime('%Y-%m-%d'), user_id=user_id).id
            Location_id = Inventory_item_LocationID.objects.get(
                location_name=obj['location']).id
            Usecase_id = Inventory_item_UsecaseID.objects.get(
                usecase_name=obj['usecase']).id
            Full_id = str(Location_id) + "-" + \
                str(Usecase_id) + "-" + str(Item_id)
            Inventory_Item.objects.filter(
                id=Item_id, user_id=user_id).update(full_id=Full_id)

def import_yaml(file, user_id):
    if file == None:
        return ('No file selected')
    yaml_file = file.read().decode('utf-8')
    yaml_data = yaml.safe_load(yaml_file)
    for obj in yaml_data['objects']:
        if Inventory_Item.objects.filter(name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], user_id=user_id).exists():
            print('Item already exists')
            old_amount = Inventory_Item.objects.get(
                name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], user_id=user_id).amount
            print(old_amount)
            new_amount = int(old_amount) + int(obj['amount'])
            print(new_amount)
            Inventory_Item.objects.filter(
                name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], user_id=user_id).update(amount=new_amount)
        else:
            Inventory_Item.objects.create(
                name=obj['name'], vendor=obj['vendor'], usecase=obj['usecase'], location=obj['location'], group=obj['group'], description=obj['description'], amount=obj['amount'], user_id=user_id)

            if Inventory_item_LocationID.objects.filter(location_name=obj['location']).exists():
                pass
            else:
                Inventory_item_LocationID.objects.create(
                    location_name=obj['location'])
            if Inventory_item_UsecaseID.objects.filter(usecase_name=obj['usecase']).exists():
                pass
            else:
                Inventory_item_UsecaseID.objects.create(
                    usecase_name=obj['usecase'])

            Item_id = Inventory_Item.objects.get(
                name=obj['name'], vendor=obj['vendor'], created_at=datetime.today().strftime('%Y-%m-%d'), user_id=user_id).id
            Location_id = Inventory_item_LocationID.objects.get(
                location_name=obj['location']).id
            Usecase_id = Inventory_item_UsecaseID.objects.get(
                usecase_name=obj['usecase']).id
            Full_id = str(Location_id) + "-" + \
                str(Usecase_id) + "-" + str(Item_id)
            Inventory_Item.objects.filter(
                id=Item_id, user_id=user_id).update(full_id=Full_id)


def random_string(length):
    letters = string.ascii_letters + string.digits + "&" + "$"
    return ''.join(random.choice(letters) for _ in range(length))


def read_paper_file():
    # /prj/Inventory_Managment_System_Django/
    with open('lable_paper.yml', 'r') as file:
        yml_dict = yaml.safe_load(file)
    return yml_dict['dymo8']

def gen_device_link_file():
    session_token = ''.join(random.choice(string.digits) for _ in range(128))
    device_link_dict = {
        'domain': Site.objects.get_current().domain,
        'database': {
            'host': config_file.DB_HOST,
            'port': config_file.DB_PORT,
            'user': config_file.DB_USER,
            'password': config_file.DB_PASS,
            'name': config_file.DB_NAME,
        }
    }

    device_link_file = yaml.dump(device_link_dict)

    return device_link_file

