from os.path import join
import os
from Inventory_Managment import settings
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



def print_lable(template_src, context_dict={}):
    pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'out.pdf')
    #path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    #config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    options = {
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'page-height': '400',
        'page-width': '800',
        'enable-local-file-access': ''
    }
    #hti = Html2Image()
    template = get_template(template_src)
    html = template.render(context_dict)
    pdfkit.from_string(html, pdf_path, options=options) #, configuration=config)
    pdf = open("out.pdf")
    pdf.close()
    #hti.screenshot(html_str=html, save_as='lable.jpg', size=(1051, 425), )
    print('Printing Lable')
    subprocess.call('lpr -P "Dymo_LableWriter_400_(LAN)" -o landscape -o media=Custom.89x36mm -o fit-to-page out.pdf', shell=True)
    os.remove("out.pdf")  # remove the locally created pdf file.
    return 'Lable printed'

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

