import qrcode
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code39
from .models import Inventory_Settings
from io import BytesIO
import os


def gen_print_label(text_input, qr=None, icon=None, bbox=False, font_size=10, font='Helvetica'):

    #dir = '/prj/Inventory_Managment_System_Django/'
    dir = ''

    # label size
    file_name = str(Inventory_Settings.objects.get(id=1).print_file_name)
    output = dir + file_name
    paper_height = int(Inventory_Settings.objects.get(id=1).paper_height) - 3
    paper_width = int(Inventory_Settings.objects.get(id=1).paper_width) - 3
    LABEL_SIZE = (paper_height * mm, paper_width * mm)

    # create label
    c = canvas.Canvas(output, pagesize=LABEL_SIZE)

    # transform so that we can render as if it's landscape mode
    c.rotate(-90)
    c.translate(-LABEL_SIZE[1], 0)

    
    # draw qr code
    qr_size = LABEL_SIZE[0] - 20
    if qr is not None:
        qr = qrcode.make(qr)
        c.drawImage(ImageReader(qr._img),
                    LABEL_SIZE[1] - qr_size - 10, 0, qr_size, qr_size)
        print("QR code generated")
    else:
        qr_size = 0
    
    '''
    # draw barcode
    qr_size = LABEL_SIZE[0]
    print(LABEL_SIZE)
    print(type(qr_size))
    code = code39.Standard39(qr, barHeight=LABEL_SIZE[0], barWidth= 25, stop=10)
    code.drawOn(c, LABEL_SIZE[1] - qr_size - 75, 0)
    '''

    # draw bounding box
    if bbox:
        c.rect(0, 0, LABEL_SIZE[1], LABEL_SIZE[0], stroke=1, fill=0)

    # font
    c.setFont(font, font_size)

    # font metrics
    def getTextHeight(fontName, fontSize):
        face = pdfmetrics.getFont(fontName).face
        ascent = (face.ascent * fontSize) / 1000.0
        descent = (face.descent * fontSize) / 1000.0

        height = ascent - descent  # <-- descent it's negative
        print("Font height: %s" % height)
        return height

    item_spacing = 4

    # margins
    leftMargin = 4
    c.translate(leftMargin, 0)

    if icon is not None:
        # TODO: don't hardcode so many things
        img_width = 20
        c.drawImage(
            icon, 0, (LABEL_SIZE[0] - img_width) / 2, img_width, img_width)
        c.translate(img_width + item_spacing, 0)
        print("Icon added")

    # vertically centered text drawn from the current point in multiple lines so
    # that it fits in the given box size
    textWidth = LABEL_SIZE[1] - qr_size - leftMargin - item_spacing

    def wrappedTextBox(canvas, text, boxSize, fontName, fontSize, lineSpacing):
        print("Text width: %s" % textWidth)
        canvas.saveState()

        lineHeight = getTextHeight(fontName, fontSize) + lineSpacing
        lines = simpleSplit(text, fontName, fontSize, textWidth)

        totalHeight = len(lines) * lineHeight

        if totalHeight > boxSize[1]:
            raise RuntimeError("ERROR: Text is too big")

        # center text vertically
        canvas.translate(0, (boxSize[1] - totalHeight) /
                         2 + totalHeight - lineHeight)
        for i in range(len(lines)):
            canvas.drawString(0, -lineHeight * i, lines[i])

        canvas.restoreState()


    wrappedTextBox(c, text_input, (textWidth, LABEL_SIZE[0]), font, font_size, 5)
    c.save()
    return "Lable Generated"
