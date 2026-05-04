
import easyocr
reader = easyocr.Reader(['en'])
def read_text(img):
    return reader.readtext(img)