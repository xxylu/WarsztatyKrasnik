import tensorflow as tf
import numpy as np
import cv2
import os

# Konfiguracja ścieżki do folderu
folder_path = 'data'

if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
    print(f"Błąd: Folder '{folder_path}' nie istnieje lub nie jest katalogiem!")
else:
    # Wczytanie gotowego modelu
    model = tf.keras.models.load_model('ocr-mnist.keras')

    # 2. Pobranie listy plików w folderze (filtrujemy tylko rozszerzenia graficzne)
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

    if not image_files:
        print(f"Brak plików w folderze '{folder_path}'.")
    else:
        print(f"Znaleziono {len(image_files)} plików. Rozpoczynam rozpoznawanie:\n" + "-"*40)

        # 3. Pętla przetwarzająca każde zdjęcie w folderze
        for filename in image_files:
            file_path = os.path.join(folder_path, filename)

            # Wczytanie zdjęcia
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

            # Zabezpieczenie przed uszkodzonymi lub niemożliwymi do wczytania plikami
            if img is None:
                print(f"[{filename}] Błąd: Nie można wczytać pliku.")
                continue

            # Przygotowanie obrazu (czarne tło, biała cyfra, 28x28 pikseli)
            img_resized = cv2.resize(img, (28, 28))
            img_normalized = img_resized / 255.0                # Normalizacja (Aby wartości mieściły się w zakresie 0-1)
            img_batch = np.expand_dims(img_normalized, axis=0)  # Dodanie wymiaru "batch"

            predict = model.predict(img_batch, verbose=1)
            recognised = np.argmax(predict)

            print(f"Plik: {filename:15} | Rozpoznana cyfra: {recognised}")