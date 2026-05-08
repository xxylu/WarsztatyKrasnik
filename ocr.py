import pytesseract
import cv2

image = 'tekst.png'

def ocr(image_path, lang):
    try:
        img = cv2.imread(image_path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        return pytesseract.image_to_string(gray, lang=lang)

    except Exception as e:
        return f"Wystąpił błąd: {e}"

wynik = ocr(image, lang='pol+eng')

print(wynik)